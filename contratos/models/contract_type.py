
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ContractType(models.Model):
    _name = 'contract.type'
    _description = 'Tipo de Contrato'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre del tipo de contrato'
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

    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help='Secuencia para ordenar los tipos de contrato'
    )

    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está desmarcado, no se podrá seleccionar para nuevos contratos'
    )

    # Configuración específica del tipo
    duration_months = fields.Integer(
        string='Duración (Meses)',
        default=12,
        help='Duración estándar en meses para este tipo de contrato'
    )

    auto_renewal = fields.Boolean(
        string='Renovación Automática',
        default=False,
        help='Si está marcado, los contratos de este tipo se renovarán automáticamente'
    )

    requires_devices = fields.Boolean(
        string='Requiere Dispositivos',
        default=True,
        help='Si está marcado, los contratos de este tipo requieren dispositivos GPS'
    )

    billing_cycle = fields.Selection([
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('semiannual', 'Semestral'),
        ('annual', 'Anual')
    ], string='Ciclo de Facturación', default='monthly')

    # Plantilla por defecto
    template_id = fields.Many2one(
        'contract.template',
        string='Plantilla por Defecto',
        help='Plantilla que se usará por defecto para este tipo de contrato'
    )

    # Configuraciones financieras
    default_monthly_fee = fields.Monetary(
        string='Tarifa Mensual por Defecto',
        currency_field='currency_id',
        help='Tarifa mensual sugerida para este tipo de contrato'
    )

    default_setup_fee = fields.Monetary(
        string='Costo de Instalación por Defecto',
        currency_field='currency_id',
        help='Costo de instalación sugerido'
    )

    default_deposit = fields.Monetary(
        string='Depósito por Defecto',
        currency_field='currency_id',
        help='Depósito sugerido para garantía'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        required=True
    )

    # Productos relacionados
    product_ids = fields.Many2many(
        'product.product',
        'contract_type_product_rel',
        'contract_type_id',
        'product_id',
        string='Productos Asociados',
        help='Productos que se pueden incluir en este tipo de contrato'
    )

    # Términos legales específicos
    legal_terms = fields.Html(
        string='Términos Legales Específicos',
        help='Términos y condiciones específicos para este tipo de contrato'
    )

    # Configuración de notificaciones
    notification_days_before = fields.Integer(
        string='Días de Notificación Previa',
        default=60,
        help='Días antes del vencimiento para enviar notificación'
    )

    send_expiry_notifications = fields.Boolean(
        string='Enviar Notificaciones de Vencimiento',
        default=True,
        help='Si está marcado, se enviarán notificaciones antes del vencimiento'
    )

    # Estadísticas (removed contract_count to prevent field dependency errors)

    # Color para la interfaz
    color = fields.Integer(
        string='Color',
        help='Color para mostrar en la interfaz'
    )

    @api.constrains('code')
    def _check_code_unique(self):
        """Validar que el código sea único"""
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_('El código del tipo de contrato debe ser único.'))

    @api.constrains('duration_months')
    def _check_duration(self):
        """Validar que la duración sea positiva"""
        for record in self:
            if record.duration_months <= 0:
                raise ValidationError(_('La duración debe ser mayor a 0 meses.'))

    @api.constrains('notification_days_before')
    def _check_notification_days(self):
        """Validar días de notificación"""
        for record in self:
            if record.notification_days_before < 0:
                raise ValidationError(_('Los días de notificación no pueden ser negativos.'))

    def action_view_contracts(self):
        """Ver contratos de este tipo"""
        self.ensure_one()
        return {
            'name': _('Contratos - %s') % self.name,
            'view_mode': 'tree,form',
            'res_model': 'contract.general',
            'type': 'ir.actions.act_window',
            'domain': [('contract_type_id', '=', self.id)],
            'context': {'default_contract_type_id': self.id}
        }

    def get_default_values(self):
        """Obtener valores por defecto para este tipo de contrato"""
        self.ensure_one()
        return {
            'duration_months': self.duration_months,
            'auto_renewal': self.auto_renewal,
            'billing_cycle': self.billing_cycle,
            'monthly_fee': self.default_monthly_fee,
            'setup_fee': self.default_setup_fee,
            'deposit_amount': self.default_deposit,
            'template_id': self.template_id.id if self.template_id else False,
        }

    def name_get(self):
        """Personalizar el nombre mostrado"""
        result = []
        for record in self:
            name = f"[{record.code}] {record.name}"
            result.append((record.id, name))
        return result

    @api.model
    def create_default_types(self):
        """Crear tipos de contrato por defecto"""
        default_types = [
            {
                'name': 'Servicio GPS Básico',
                'code': 'GPS_BASIC',
                'description': 'Servicio básico de rastreo GPS con plataforma web',
                'duration_months': 12,
                'auto_renewal': True,
                'requires_devices': True,
                'billing_cycle': 'monthly',
                'default_monthly_fee': 15000.0,  # ₡15,000
                'default_setup_fee': 25000.0,   # ₡25,000
                'default_deposit': 50000.0,     # ₡50,000
            },
            {
                'name': 'Servicio GPS Premium',
                'code': 'GPS_PREMIUM',
                'description': 'Servicio premium con alertas, reportes y soporte 24/7',
                'duration_months': 12,
                'auto_renewal': True,
                'requires_devices': True,
                'billing_cycle': 'monthly',
                'default_monthly_fee': 25000.0,  # ₡25,000
                'default_setup_fee': 35000.0,   # ₡35,000
                'default_deposit': 75000.0,     # ₡75,000
            },
            {
                'name': 'Venta de Dispositivo',
                'code': 'DEVICE_SALE',
                'description': 'Venta directa de dispositivo GPS sin servicio',
                'duration_months': 0,
                'auto_renewal': False,
                'requires_devices': True,
                'billing_cycle': 'annual',
                'default_monthly_fee': 0.0,
                'default_setup_fee': 0.0,
                'default_deposit': 0.0,
            },
            {
                'name': 'Alquiler de Dispositivo',
                'code': 'DEVICE_RENTAL',
                'description': 'Alquiler de dispositivo GPS con opción de compra',
                'duration_months': 24,
                'auto_renewal': False,
                'requires_devices': True,
                'billing_cycle': 'monthly',
                'default_monthly_fee': 12000.0,  # ₡12,000
                'default_setup_fee': 15000.0,   # ₡15,000
                'default_deposit': 100000.0,    # ₡100,000
            }
        ]

        for type_data in default_types:
            if not self.search([('code', '=', type_data['code'])]):
                self.create(type_data)
