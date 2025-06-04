# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ContractLine(models.Model):
    _name = 'contract.general.line'
    _description = 'Línea de Contrato General'
    _order = 'contract_id, sequence, id'

    contract_id = fields.Many2one(
        'contract.general',
        string='Contrato',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(string='Secuencia', default=10)

    name = fields.Text(
        string='Descripción',
        required=True,
        help='Descripción del producto o servicio'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        help='Producto relacionado (opcional)'
    )

    quantity = fields.Float(
        string='Cantidad',
        default=1.0,
        digits='Product Unit of Measure',
        required=True
    )

    unit_price = fields.Monetary(
        string='Precio Unitario',
        currency_field='currency_id',
        required=True
    )

    subtotal = fields.Monetary(
        string='Subtotal',
        currency_field='currency_id',
        compute='_compute_subtotal',
        store=True
    )

    currency_id = fields.Many2one(
        related='contract_id.currency_id',
        string='Moneda',
        readonly=True
    )

    # Campos adicionales para servicios GPS
    service_type = fields.Selection([
        ('monthly', 'Servicio Mensual'),
        ('installation', 'Instalación'),
        ('device', 'Dispositivo'),
        ('sim', 'SIM Card'),
        ('maintenance', 'Mantenimiento'),
        ('other', 'Otro')
    ], string='Tipo de Servicio', default='monthly')

    recurring = fields.Boolean(
        string='Recurrente',
        default=True,
        help='Si está marcado, este ítem se facturará de forma recurrente'
    )

    notes = fields.Text(string='Notas Adicionales')

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.unit_price = self.product_id.list_price

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_('La cantidad debe ser mayor que cero.'))

    @api.constrains('unit_price')
    def _check_unit_price(self):
        for line in self:
            if line.unit_price < 0:
                raise ValidationError(_('El precio unitario no puede ser negativo.'))