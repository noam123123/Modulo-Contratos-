# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class Contract(models.Model):
    _name = 'contract.general'
    _description = 'Contrato General'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
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

    # Solo contactos tipo empresa
    partner_id = fields.Many2one(
        'res.partner', 
        string='Empresa Cliente', 
        required=True, 
        tracking=True,
        domain=[('is_company', '=', True)]
    )

    # Contacto legal que firma/aprueba el contrato
    legal_contact_id = fields.Many2one(
        'res.partner',
        string='Contacto Legal/Firmante',
        required=True,
        tracking=True,
        help='Persona que firma o aprueba el contrato'
    )

    # Información del representante legal
    legal_representative_name = fields.Char(
        string='Nombre Representante Legal',
        required=True,
        tracking=True
    )

    legal_representative_position = fields.Char(
        string='Puesto/Cargo',
        required=True,
        help='Ej: Gerente General, Presidente, Apoderado Generalísimo'
    )

    legal_representative_hierarchy = fields.Selection([
        ('president', 'Presidente'),
        ('vp', 'Vicepresidente'),
        ('general_manager', 'Gerente General'),
        ('manager', 'Gerente'),
        ('legal_rep', 'Representante Legal'),
        ('attorney', 'Apoderado Generalísimo'),
        ('attorney_special', 'Apoderado Especial'),
        ('other', 'Otro')
    ], string='Jerarquía', required=True, default='general_manager')

    legal_representative_id_number = fields.Char(
        string='Cédula Representante',
        required=True,
        help='Número de cédula del representante legal'
    )

    legal_representative_email = fields.Char(
        string='Email Representante',
        required=True
    )

    legal_representative_phone = fields.Char(
        string='Teléfono Representante'
    )

    legal_representative_address = fields.Text(
        string='Dirección Representante'
    )

    contract_type_id = fields.Many2one(
        'contract.type', 
        string='Tipo de Contrato', 
        required=True, 
        tracking=True
    )

    template_id = fields.Many2one(
        'contract.template',
        string='Plantilla de Contrato',
        help='Plantilla utilizada para generar el PDF del contrato'
    )

    # Estados actualizados del contrato
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

    auto_renewal = fields.Boolean(
        string='Contrato Autorenovable', 
        default=True,
        help='Si está marcado, el contrato se renovará automáticamente'
    )

    last_renewal_date = fields.Date(
        string='Última Fecha de Renovación',
        readonly=True,
        help='Fecha en la que se renovó por última vez'
    )

    renewal_count = fields.Integer(
        string='Número de Renovaciones',
        default=0,
        readonly=True
    )

    service_description = fields.Text(
        string='Descripción de Servicios', 
        required=True,
        help='Descripción detallada de los servicios o productos contratados'
    )

    # Valor del contrato
    contract_value = fields.Monetary(
        string='Valor Total del Contrato',
        currency_field='currency_id',
        required=True,
        tracking=True,
        help='Valor total del contrato'
    )

    # Información financiera
    monthly_fee = fields.Monetary(
        string='Tarifa Mensual', 
        currency_field='currency_id',
        help='Costo mensual del servicio'
    )

    setup_fee = fields.Monetary(
        string='Costo de Configuración', 
        currency_field='currency_id',
        help='Costo único de configuración o instalación'
    )

    deposit = fields.Monetary(
        string='Depósito de Garantía', 
        currency_field='currency_id',
        help='Depósito requerido como garantía'
    )

    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda', 
        default=lambda self: self.env.company.currency_id
    )

    # Líneas del contrato
    contract_line_ids = fields.One2many(
        'contract.line', 
        'contract_id', 
        string='Detalles del Contrato'
    )

    billing_cycle = fields.Selection([
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('semiannual', 'Semestral'),
        ('annual', 'Anual')
    ], string='Ciclo de Facturación', default='monthly', required=True)

    payment_method = fields.Selection([
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia Bancaria'),
        ('check', 'Cheque'),
        ('card', 'Tarjeta de Crédito/Débito'),
        ('deposit', 'Depósito Bancario')
    ], string='Método de Pago', default='transfer')

    # Información adicional personalizable
    special_conditions = fields.Html(
        string='Condiciones Especiales',
        help='Condiciones específicas para este contrato que se agregarán al documento'
    )

    internal_notes = fields.Text(string='Notas Internas')

    # Integración con ventas
    sale_order_id = fields.Many2one('sale.order', string='Orden de Venta Relacionada')
    invoice_ids = fields.One2many(
        'account.move', 
        'contract_id', 
        string='Facturas'
    )
    invoice_count = fields.Integer(string='Número de Facturas', compute='_compute_invoice_count')

    # Responsable del contrato para notificaciones
    contract_manager_id = fields.Many2one(
        'res.users',
        string='Responsable del Contrato',
        required=True,
        default=lambda self: self.env.user,
        help='Usuario responsable que recibirá las notificaciones'
    )

    # Campos de notificación
    notification_2_months = fields.Boolean(
        string='Notificación enviada (2 meses)',
        default=False,
        readonly=True
    )

    notification_expiry = fields.Boolean(
        string='Notificación enviada (vencimiento)',
        default=False,
        readonly=True
    )

    notification_renewal = fields.Boolean(
        string='Notificación enviada (renovación)',
        default=False,
        readonly=True
    )

    @api.depends('name', 'partner_id', 'contract_type_id')
    def _compute_display_name(self):
        for contract in self:
            if contract.name and contract.name != _('Nuevo'):
                contract.display_name = f"{contract.name} - {contract.partner_id.name}"
            else:
                type_name = contract.contract_type_id.name if contract.contract_type_id else "General"
                partner_name = contract.partner_id.name if contract.partner_id else "Cliente"
                contract.display_name = f"Contrato {type_name} - {partner_name}"

    @api.depends('invoice_ids.move_type')
    def _compute_invoice_count(self):
        for contract in self:
            # Count only out_invoices manually to avoid domain issues
            invoice_count = 0
            for invoice in contract.invoice_ids:
                if invoice.move_type == 'out_invoice':
                    invoice_count += 1
            contract.invoice_count = invoice_count

    @api.onchange('duration_months', 'date_start')
    def _onchange_duration(self):
        if self.date_start and self.duration_months:
            self.date_end = self.date_start + timedelta(days=self.duration_months * 30)

    @api.onchange('contract_type_id')
    def _onchange_contract_type(self):
        if self.contract_type_id:
            self.duration_months = self.contract_type_id.default_duration
            self.auto_renewal = self.contract_type_id.auto_renewal
            self.template_id = self.contract_type_id.template_id
            if not self.service_description:
                self.service_description = f"Servicios de {self.contract_type_id.name}"

    @api.onchange('legal_contact_id')
    def _onchange_legal_contact(self):
        if self.legal_contact_id:
            self.legal_representative_name = self.legal_contact_id.name
            self.legal_representative_email = self.legal_contact_id.email
            self.legal_representative_phone = self.legal_contact_id.phone
            # Construir dirección completa
            address_parts = []
            if self.legal_contact_id.street:
                address_parts.append(self.legal_contact_id.street)
            if self.legal_contact_id.street2:
                address_parts.append(self.legal_contact_id.street2)
            if self.legal_contact_id.city:
                address_parts.append(self.legal_contact_id.city)
            if self.legal_contact_id.state_id:
                address_parts.append(self.legal_contact_id.state_id.name)
            if self.legal_contact_id.country_id:
                address_parts.append(self.legal_contact_id.country_id.name)
            self.legal_representative_address = ', '.join(address_parts)

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('contract.general') or _('Nuevo')
        contract = super(Contract, self).create(vals)
        # Crear o actualizar contacto legal
        contract._update_legal_contact_info()
        return contract

    def write(self, vals):
        result = super(Contract, self).write(vals)
        # Actualizar información del contacto legal si cambió
        if any(field in vals for field in ['legal_representative_name', 'legal_representative_email', 
                                          'legal_representative_phone', 'legal_representative_address']):
            self._update_legal_contact_info()
        return result

    def _update_legal_contact_info(self):
        """Actualizar información del contacto legal en el modelo de contactos"""
        for contract in self:
            if contract.legal_contact_id:
                # Preparar datos para sincronización
                contract_data = {
                    'name': contract.legal_representative_name,
                    'email': contract.legal_representative_email,
                    'phone': contract.legal_representative_phone,
                    'is_legal_representative': True,
                    'legal_position': contract.legal_representative_position,
                    'legal_hierarchy': contract.legal_representative_hierarchy,
                    'legal_id_number': contract.legal_representative_id_number,
                }

                # Sincronizar usando el método del partner
                contract.legal_contact_id.sync_from_contract(contract_data)

            # También sincronizar datos de la empresa cliente
            if contract.partner_id:
                company_data = {
                    'name': contract.partner_id.name,
                    'email': contract.partner_id.email,
                    'phone': contract.partner_id.phone,
                    'is_company': True,
                    'company_legal_name': contract.partner_id.company_legal_name,
                    'company_tax_id': contract.partner_id.company_tax_id,
                    'company_registration': contract.partner_id.company_registration,
                }

                contract.partner_id.sync_from_contract(company_data)

    def action_negotiate(self):
        """Pasar contrato a negociación"""
        self.ensure_one()
        self.state = 'negotiation'
        self.message_post(body=_('Contrato en proceso de negociación'))

    def action_validate(self):
        """Validar/hacer vigente el contrato"""
        self.ensure_one()
        if self.state not in ['new', 'negotiation']:
            raise UserError(_('Solo se pueden validar contratos nuevos o en negociación.'))
        if not self.sale_order_id and (self.monthly_fee or self.setup_fee or self.contract_line_ids):
            self._create_sale_order()
        self.state = 'valid'
        self.message_post(body=_('Contrato validado y en vigor'))

    def action_renew(self):
        """Renovar contrato"""
        self.ensure_one()
        if self.state != 'valid':
            raise UserError(_('Solo se pueden renovar contratos vigentes.'))

        old_end_date = self.date_end
        new_end_date = self.date_end + timedelta(days=self.duration_months * 30)

        self.write({
            'state': 'renewed',
            'date_end': new_end_date,
            'last_renewal_date': fields.Date.today(),
            'renewal_count': self.renewal_count + 1,
            'notification_2_months': False,
            'notification_expiry': False,
            'notification_renewal': False
        })

        # Enviar notificación de renovación
        self._send_renewal_notification(old_end_date, new_end_date)
        self.message_post(
            body=_('Contrato renovado automáticamente. Nueva fecha de vencimiento: %s') % new_end_date
        )

    def action_terminate(self):
        """Terminar/finiquitar contrato"""
        self.ensure_one()
        self.state = 'terminated'
        self.message_post(body=_('Contrato finiquitado'))

    def action_cancel(self):
        """Cancelar contrato"""
        self.ensure_one()
        self.state = 'cancelled'
        self.message_post(body=_('Contrato cancelado'))

    def action_view_invoices(self):
        """Ver facturas del contrato"""
        self.ensure_one()
        return {
            'name': _('Facturas del Contrato'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'context': {'default_contract_id': self.id}
        }

    def _create_sale_order(self):
        """Crear orden de venta basada en el contrato"""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'contract_id': self.id,
            'order_line': self._prepare_sale_order_lines()
        })
        self.sale_order_id = sale_order.id
        return sale_order

    def _prepare_sale_order_lines(self):
        """Preparar líneas de la orden de venta"""
        lines = []
        if self.monthly_fee:
            lines.append((0, 0, {
                'name': f"Servicio mensual - {self.service_description[:50]}...",
                'product_uom_qty': self.duration_months,
                'price_unit': self.monthly_fee,
            }))
        if self.setup_fee:
            lines.append((0, 0, {
                'name': "Costo de configuración/instalación",
                'product_uom_qty': 1,
                'price_unit': self.setup_fee,
            }))
        for line in self.contract_line_ids:
            lines.append((0, 0, {
                'name': line.name,
                'product_uom_qty': line.quantity,
                'price_unit': line.unit_price,
            }))
        return lines

    def generate_contract_pdf(self):
        """Generar PDF del contrato"""
        self.ensure_one()
        return self.env.ref('contratos.action_report_contract').report_action(self)

    @api.model
    def _cron_check_contract_expiry(self):
        """Cron para verificar vencimientos y enviar notificaciones"""
        today = fields.Date.today()
        two_months_ahead = today + timedelta(days=60)

        # Notificaciones a 2 meses del vencimiento
        contracts_2_months = self.search([
            ('state', 'in', ['valid', 'renewed']),
            ('date_end', '=', two_months_ahead),
            ('notification_2_months', '=', False)
        ])

        for contract in contracts_2_months:
            contract._send_expiry_warning_notification()
            contract.notification_2_months = True

        # Notificaciones el día del vencimiento
        contracts_expiring = self.search([
            ('state', 'in', ['valid', 'renewed']),
            ('date_end', '=', today),
            ('notification_expiry', '=', False)
        ])

        for contract in contracts_expiring:
            if contract.auto_renewal:
                contract.action_renew()
            else:
                contract._send_expiry_notification()
                contract.notification_expiry = True

    def _send_expiry_warning_notification(self):
        """Enviar notificación de advertencia de vencimiento (2 meses antes)"""
        self.ensure_one()
        template = self.env.ref('contratos.email_template_contract_expiry_warning', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

    def _send_expiry_notification(self):
        """Enviar notificación de vencimiento"""
        self.ensure_one()
        template = self.env.ref('contratos.email_template_contract_expiry', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

    def _send_renewal_notification(self, old_date, new_date):
        """Enviar notificación de renovación"""
        self.ensure_one()
        template = self.env.ref('contratos.email_template_contract_renewal', raise_if_not_found=False)
        if template:
            template.with_context(
                old_end_date=old_date,
                new_end_date=new_date
            ).send_mail(self.id, force_send=True)
        self.notification_renewal = True


class AccountMove(models.Model):
    _inherit = 'account.move'

    contract_id = fields.Many2one(
        'contract.general',
        string='Contrato Relacionado',
        help='Contrato del cual se generó esta factura'
    )


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_id = fields.Many2one(
        'contract.general', 
        string='Contrato', 
        help='Contrato relacionado con esta orden de venta'
    )