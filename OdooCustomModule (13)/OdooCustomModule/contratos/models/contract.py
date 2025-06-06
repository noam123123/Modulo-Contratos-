
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta


class Contract(models.Model):
    _name = 'contract.general'
    _description = 'Contrato General'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, name'
    _rec_name = 'display_name'

    name = fields.Char(
        string='Número de Contrato', 
        required=True, 
        copy=False, 
        readonly=True, 
        default=lambda self: _('Nuevo')
    )

    display_name = fields.Char(
        string='Nombre del Contrato', 
        compute='_compute_display_name', 
        store=True
    )

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
        help='Descripción detallada del contrato'
    )

    notes = fields.Text(
        string='Notas Internas',
        help='Notas internas sobre el contrato'
    )

    @api.depends('name', 'partner_id', 'contract_type_id')
    def _compute_display_name(self):
        for contract in self:
            if contract.name and contract.name != _('Nuevo'):
                type_name = contract.contract_type_id.name if contract.contract_type_id else "General"
                partner_name = contract.partner_id.name if contract.partner_id else "Cliente"
                contract.display_name = f"Contrato {type_name} - {partner_name}"
            else:
                contract.display_name = _('Nuevo Contrato')

    @api.onchange('duration_months', 'date_start')
    def _onchange_duration(self):
        if self.date_start and self.duration_months:
            start_date = fields.Date.from_string(self.date_start) if isinstance(self.date_start, str) else self.date_start
            self.date_end = start_date + timedelta(days=self.duration_months * 30)

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
