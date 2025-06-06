
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

    default_duration = fields.Integer(
        string='Duración por Defecto (meses)',
        default=12,
        help='Duración en meses por defecto para este tipo de contrato'
    )

    contract_count = fields.Integer(
        string='Número de Contratos',
        compute='_compute_contract_count'
    )

    def _compute_contract_count(self):
        for contract_type in self:
            contract_type.contract_count = self.env['contract.general'].search_count([
                ('contract_type_id', '=', contract_type.id)
            ])

    @api.constrains('code')
    def _check_code_unique(self):
        for record in self:
            if record.code:
                existing = self.search([
                    ('code', '=', record.code),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_('El código del tipo de contrato debe ser único.'))

    def action_view_contracts(self):
        self.ensure_one()
        return {
            'name': _('Contratos de tipo: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'contract.general',
            'view_mode': 'tree,form',
            'domain': [('contract_type_id', '=', self.id)],
            'context': {'default_contract_type_id': self.id}
        }
