
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Contract(models.Model):
    _name = 'contract.general'
    _description = 'Contrato General'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, name'
    _rec_name = 'name'

    name = fields.Char(
        string='Número de Contrato', 
        required=True, 
        copy=False, 
        readonly=True, 
        default=lambda self: _('Nuevo')
    )

    # Removed computed field to prevent installation hanging

    partner_id = fields.Many2one(
        'res.partner', 
        string='Empresa Cliente', 
        required=True, 
        tracking=True,
        domain=[('is_company', '=', True)]
    )

    contact_person_id = fields.Many2one(
        'res.partner', 
        string='Persona de Contacto', 
        tracking=True,
        domain="[('parent_id', '=', partner_id), ('is_company', '=', False)]"
    )

    contract_type_id = fields.Many2one(
        'contract.type', 
        string='Tipo de Contrato', 
        required=True, 
        tracking=True
    )

    state = fields.Selection([
        ('new', 'Nuevo'),
        ('negotiation', 'En Negociación'),
        ('valid', 'Vigente'),
        ('renewed', 'Renovado'),
        ('terminated', 'Finiquitado'),
        ('cancelled', 'Cancelado')
    ], string='Estado', default='new', tracking=True)

    date_start = fields.Date(
        string='Fecha de Inicio', 
        required=True, 
        default=fields.Date.today, 
        tracking=True
    )

    date_end = fields.Date(string='Fecha de Vencimiento', tracking=True, required=True)

    duration_months = fields.Integer(string='Duración (meses)', default=12, required=True)

    description = fields.Text(
        string='Descripción del Contrato',
        help='Descripción detallada del objeto y alcance del contrato'
    )

    # Financial Fields
    contract_value = fields.Monetary(
        string='Valor del Contrato',
        currency_field='currency_id',
        help='Valor total del contrato'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id
    )
    
    payment_terms = fields.Text(
        string='Términos de Pago',
        help='Condiciones y términos de pago del contrato'
    )
    
    notes = fields.Text(
        string='Notas Internas',
        help='Notas internas sobre el contrato'
    )



    @api.onchange('duration_months', 'date_start')
    def _onchange_duration(self):
        if self.date_start and self.duration_months:
            from datetime import timedelta
            # Calculate end date using approximate month calculation
            total_days = self.duration_months * 30
            self.date_end = self.date_start + timedelta(days=total_days)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.contact_person_id = False

    @api.onchange('contract_type_id')
    def _onchange_contract_type_id(self):
        if self.contract_type_id and self.contract_type_id.default_duration:
            self.duration_months = self.contract_type_id.default_duration

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('contract.general') or _('Nuevo')
        return super(Contract, self).create(vals)

    def action_negotiate(self):
        self.ensure_one()
        self.state = 'negotiation'
        self.message_post(body=_('Contrato en negociación'))

    def action_validate(self):
        self.ensure_one()
        self.state = 'valid'
        self.message_post(body=_('Contrato validado y vigente'))

    def action_renew(self):
        self.ensure_one()
        self.state = 'renewed'
        self.message_post(body=_('Contrato renovado'))

    def action_terminate(self):
        self.ensure_one()
        self.state = 'terminated'
        self.message_post(body=_('Contrato finiquitado'))

    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'
        self.message_post(body=_('Contrato cancelado'))
