
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ContractLine(models.Model):
    _name = 'contract.line'
    _description = 'Línea de Contrato'
    _order = 'sequence, id'

    contract_id = fields.Many2one(
        'contract.general',
        string='Contrato',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(string='Secuencia', default=10)
    
    name = fields.Char(
        string='Descripción',
        required=True,
        help='Descripción del producto o servicio'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        help='Producto asociado a esta línea'
    )

    description = fields.Text(
        string='Descripción Detallada',
        help='Descripción más detallada del producto o servicio'
    )

    quantity = fields.Float(
        string='Cantidad',
        default=1.0,
        digits='Product Unit of Measure',
        required=True
    )

    uom_id = fields.Many2one(
        'uom.uom',
        string='Unidad de Medida',
        help='Unidad de medida del producto'
    )

    price_unit = fields.Monetary(
        string='Precio Unitario',
        currency_field='currency_id',
        help='Precio por unidad'
    )

    subtotal = fields.Monetary(
        string='Subtotal',
        currency_field='currency_id',
        compute='_compute_subtotal',
        store=True,
        help='Cantidad × Precio Unitario'
    )

    currency_id = fields.Many2one(
        related='contract_id.currency_id',
        string='Moneda',
        readonly=True
    )

    # Campos específicos para dispositivos GPS
    device_imei = fields.Char(
        string='IMEI del Dispositivo',
        help='Número IMEI del dispositivo GPS'
    )

    device_serial = fields.Char(
        string='Número de Serie',
        help='Número de serie del dispositivo'
    )

    sim_number = fields.Char(
        string='Número de SIM',
        help='Número de la tarjeta SIM'
    )

    sim_iccid = fields.Char(
        string='ICCID de SIM',
        help='Código ICCID de la tarjeta SIM'
    )

    # Campos para instalación
    installation_date = fields.Date(
        string='Fecha de Instalación',
        help='Fecha en que se instaló el dispositivo'
    )

    installation_location = fields.Char(
        string='Ubicación de Instalación',
        help='Dirección donde se instaló el dispositivo'
    )

    installer_name = fields.Char(
        string='Nombre del Instalador',
        help='Técnico que realizó la instalación'
    )

    # Estado de la línea
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('pending', 'Pendiente de Instalación'),
        ('installed', 'Instalado'),
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('returned', 'Devuelto')
    ], string='Estado', default='draft')

    notes = fields.Text(
        string='Notas',
        help='Observaciones adicionales sobre esta línea'
    )

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        """Calcular el subtotal de la línea"""
        for line in self:
            line.subtotal = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Actualizar información cuando se selecciona un producto"""
        if self.product_id:
            self.name = self.product_id.name
            self.description = self.product_id.description or self.product_id.description_sale
            self.price_unit = self.product_id.list_price
            self.uom_id = self.product_id.uom_id

    @api.constrains('device_imei')
    def _check_device_imei(self):
        """Validar formato del IMEI"""
        for line in self:
            if line.device_imei:
                # IMEI debe tener 15 dígitos
                if not line.device_imei.isdigit() or len(line.device_imei) != 15:
                    raise ValidationError(_('El IMEI debe contener exactamente 15 dígitos.'))

    @api.constrains('sim_number')
    def _check_sim_number(self):
        """Validar formato del número de SIM"""
        for line in self:
            if line.sim_number:
                # Número de SIM para Costa Rica (8 dígitos)
                if not line.sim_number.isdigit() or len(line.sim_number) not in [8, 11]:
                    raise ValidationError(_('El número de SIM debe tener 8 u 11 dígitos.'))

    def action_mark_installed(self):
        """Marcar línea como instalada"""
        self.ensure_one()
        if not self.installation_date:
            self.installation_date = fields.Date.today()
        self.state = 'installed'

    def action_activate(self):
        """Activar la línea"""
        self.ensure_one()
        if self.state != 'installed':
            raise ValidationError(_('Solo se pueden activar líneas instaladas.'))
        self.state = 'active'

    def action_deactivate(self):
        """Desactivar la línea"""
        self.ensure_one()
        self.state = 'inactive'

    def action_return(self):
        """Marcar como devuelto"""
        self.ensure_one()
        self.state = 'returned'

    def name_get(self):
        """Personalizar el nombre mostrado"""
        result = []
        for line in self:
            name = line.name
            if line.device_imei:
                name = f"{name} (IMEI: {line.device_imei})"
            elif line.sim_number:
                name = f"{name} (SIM: {line.sim_number})"
            result.append((line.id, name))
        return result
