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

    contract_value = fields.Monetary(
        string='Valor Total del Contrato',
        currency_field='currency_id',
        required=True,
        tracking=True,
        help='Valor total del contrato'
    )

    monthly_fee = fields.Monetary(
        string='Tarifa Mensual', 
        currency_field='currency_id',
        help='Costo mensual del servicio'
    )

    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda', 
        default=lambda self: self.env.company.currency_id
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

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('contract.general') or _('Nuevo')
        return super(Contract, self).create(vals)
