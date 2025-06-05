# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Contract(models.Model):
    _name = 'contract.basic'
    _description = 'Contrato Básico'
    _inherit = ['mail.thread']
    _order = 'create_date desc, name'

    name = fields.Char(
        string='Número de Contrato',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nuevo')
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        tracking=True
    )

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('active', 'Activo'),
        ('finished', 'Finalizado'),
        ('cancelled', 'Cancelado')
    ], string='Estado', default='draft', tracking=True)

    date_start = fields.Date(
        string='Fecha de Inicio',
        required=True,
        default=fields.Date.today,
        tracking=True
    )

    date_end = fields.Date(
        string='Fecha de Fin',
        tracking=True
    )

    duration_months = fields.Integer(
        string='Duración (Meses)',
        default=12
    )

    monthly_amount = fields.Float(
        string='Monto Mensual',
        tracking=True
    )

    total_amount = fields.Float(
        string='Monto Total',
        compute='_compute_total_amount',
        store=True
    )

    description = fields.Text(
        string='Descripción',
        help='Descripción del contrato'
    )

    notes = fields.Text(
        string='Observaciones'
    )

    # Relación con facturas
    invoice_ids = fields.One2many(
        'account.move',
        'contract_id',
        string='Facturas',
        domain=[('move_type', 'in', ['out_invoice', 'out_refund'])],
        help='Facturas generadas desde este contrato'
    )

    invoice_count = fields.Integer(
        string='Número de Facturas',
        compute='_compute_invoice_count',
        help='Cantidad de facturas relacionadas'
    )

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for contract in self:
            contract.invoice_count = len(contract.invoice_ids)

    @api.depends('monthly_amount', 'duration_months')
    def _compute_total_amount(self):
        for contract in self:
            contract.total_amount = contract.monthly_amount * contract.duration_months

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('contract.basic') or _('Nuevo')
        return super(Contract, self).create(vals)

    def action_confirm(self):
        """Confirmar contrato"""
        self.state = 'confirmed'

    def action_activate(self):
        """Activar contrato"""
        self.state = 'active'

    def action_finish(self):
        """Finalizar contrato"""
        self.state = 'finished'

    def action_cancel(self):
        """Cancelar contrato"""
        self.state = 'cancelled'

    def action_reset_to_draft(self):
        """Regresar a borrador"""
        self.state = 'draft'

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        """Validar fechas"""
        for contract in self:
            if contract.date_start and contract.date_end:
                if contract.date_start >= contract.date_end:
                    raise ValidationError(_('La fecha de inicio debe ser anterior a la fecha de fin.'))

    @api.constrains('monthly_amount', 'duration_months')
    def _check_amounts(self):
        """Validar montos"""
        for contract in self:
            if contract.monthly_amount < 0:
                raise ValidationError(_('El monto mensual no puede ser negativo.'))
            if contract.duration_months <= 0:
                raise ValidationError(_('La duración debe ser mayor a 0.'))