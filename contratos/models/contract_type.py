# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ContractType(models.Model):
    _name = 'contract.type'
    _description = 'Tipo de Contrato'
    _order = 'name'

    name = fields.Char(
        string='Nombre del Tipo', 
        required=True
    )
    
    code = fields.Char(
        string='Código', 
        required=True,
        help='Código único para identificar el tipo de contrato'
    )
    
    description = fields.Text(
        string='Descripción',
        help='Descripción detallada del tipo de contrato'
    )
    
    active = fields.Boolean(
        string='Activo', 
        default=True
    )
    
    monthly_fee = fields.Monetary(
        string='Tarifa Mensual Base',
        currency_field='currency_id',
        help='Tarifa mensual base para este tipo de contrato'
    )
    
    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda', 
        default=lambda self: self.env.company.currency_id
    )

    @api.constrains('code')
    def _check_code_unique(self):
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_('El código del tipo de contrato debe ser único.'))