
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ContractType(models.Model):
    _name = 'contract.type'
    _description = 'Tipo de Contrato'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nombre del Tipo',
        required=True,
        translate=True,
        help='Nombre del tipo de contrato'
    )

    code = fields.Char(
        string='Código',
        required=True,
        help='Código único para identificar el tipo de contrato'
    )

    description = fields.Text(
        string='Descripción',
        translate=True,
        help='Descripción detallada del tipo de contrato'
    )

    category = fields.Selection([
        ('service', 'Servicio'),
        ('product', 'Producto'),
        ('maintenance', 'Mantenimiento'),
        ('mixed', 'Mixto')
    ], string='Categoría', required=True, default='service')

    active = fields.Boolean(string='Activo', default=True)

    sequence = fields.Integer(string='Secuencia', default=10)

    # Configuración por defecto
    default_duration = fields.Integer(
        string='Duración por Defecto (meses)',
        default=12,
        help='Duración en meses que se aplicará por defecto'
    )

    auto_renewal = fields.Boolean(
        string='Renovación Automática por Defecto',
        default=True,
        help='Si está marcado, los contratos de este tipo se renovarán automáticamente'
    )

    # Tarifas por defecto
    default_monthly_fee = fields.Monetary(
        string='Tarifa Mensual por Defecto',
        currency_field='currency_id',
        help='Tarifa mensual que se aplicará por defecto'
    )

    default_setup_fee = fields.Monetary(
        string='Costo de Configuración por Defecto',
        currency_field='currency_id',
        help='Costo de configuración que se aplicará por defecto'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id
    )

    # Plantilla por defecto
    template_id = fields.Many2one(
        'contract.template',
        string='Plantilla por Defecto',
        help='Plantilla de contrato que se usará por defecto para este tipo'
    )

    # Estadísticas
    contract_count = fields.Integer(
        string='Número de Contratos',
        compute='_compute_contract_count'
    )

    @api.depends()
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
        """Ver contratos de este tipo"""
        self.ensure_one()
        return {
            'name': _('Contratos de tipo %s') % self.name,
            'view_mode': 'tree,form',
            'res_model': 'contract.general',
            'type': 'ir.actions.act_window',
            'domain': [('contract_type_id', '=', self.id)],
            'context': {'default_contract_type_id': self.id}
        }
