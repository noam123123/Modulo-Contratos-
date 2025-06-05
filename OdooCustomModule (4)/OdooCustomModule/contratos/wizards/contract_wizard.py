# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class ContractWizard(models.TransientModel):
    _name = 'contract.wizard'
    _description = 'Wizard para Creación de Contratos'

    # Estado del wizard
    state = fields.Selection([
        ('step1', 'Paso 1: Información Básica'),
        ('step2', 'Paso 2: Empresa y Representante'),
        ('step3', 'Paso 3: Detalles del Contrato'),
        ('step4', 'Paso 4: Confirmación')
    ], string='Estado', default='step1', readonly=True)

    # === PASO 1: Información Básica ===
    contract_type_id = fields.Many2one(
        'contract.type',
        string='Tipo de Contrato',
        required=True,
        help='Seleccione el tipo de contrato a crear'
    )

    template_id = fields.Many2one(
        'contract.template',
        string='Plantilla',
        help='Plantilla base para el contrato'
    )

    # === PASO 2: Empresa y Representante ===
    # Información de la empresa
    partner_id = fields.Many2one(
        'res.partner',
        string='Empresa Cliente',
        domain=[('is_company', '=', True)],
        help='Empresa que firmará el contrato'
    )

    create_new_company = fields.Boolean(
        string='Crear Nueva Empresa',
        help='Marcar para crear una nueva empresa'
    )

    # Campos para nueva empresa
    company_name = fields.Char(
        string='Nombre de la Empresa',
        help='Razón social de la empresa'
    )

    company_legal_name = fields.Char(
        string='Razón Social Completa',
        help='Nombre legal completo de la empresa'
    )

    company_tax_id = fields.Char(
        string='Cédula Jurídica',
        help='Cédula jurídica de la empresa'
    )

    company_registration = fields.Char(
        string='Número de Registro',
        help='Número de registro empresarial'
    )

    company_email = fields.Char(
        string='Email de la Empresa',
        help='Correo electrónico principal'
    )

    company_phone = fields.Char(
        string='Teléfono de la Empresa',
        help='Teléfono principal de contacto'
    )

    company_street = fields.Char(string='Dirección')
    company_city = fields.Char(string='Ciudad')
    company_state_id = fields.Many2one('res.country.state', string='Provincia')
    company_zip = fields.Char(string='Código Postal')
    company_country_id = fields.Many2one('res.country', string='País', default=lambda self: self.env.ref('base.cr'))

    # Información del representante legal
    legal_contact_id = fields.Many2one(
        'res.partner',
        string='Representante Legal Existente',
        domain=[('is_company', '=', False)],
        help='Representante legal existente en el sistema'
    )

    create_new_legal_rep = fields.Boolean(
        string='Crear Nuevo Representante',
        help='Marcar para crear un nuevo representante legal'
    )

    # Campos para nuevo representante legal
    legal_representative_name = fields.Char(
        string='Nombre del Representante',
        help='Nombre completo del representante legal'
    )

    legal_position = fields.Char(
        string='Puesto/Cargo',
        help='Posición en la empresa'
    )

    legal_hierarchy = fields.Selection([
        ('president', 'Presidente'),
        ('vp', 'Vicepresidente'),
        ('general_manager', 'Gerente General'),
        ('manager', 'Gerente'),
        ('legal_rep', 'Representante Legal'),
        ('attorney', 'Apoderado Generalísimo'),
        ('attorney_special', 'Apoderado Especial'),
        ('other', 'Otro')
    ], string='Jerarquía Legal', default='general_manager')

    legal_id_number = fields.Char(
        string='Cédula del Representante',
        help='Número de cédula del representante legal'
    )

    legal_email = fields.Char(
        string='Email del Representante',
        help='Correo electrónico del representante'
    )

    legal_phone = fields.Char(
        string='Teléfono del Representante',
        help='Teléfono del representante legal'
    )

    # === PASO 3: Detalles del Contrato ===
    date_start = fields.Date(
        string='Fecha de Inicio',
        default=fields.Date.today,
        required=True
    )

    duration_months = fields.Integer(
        string='Duración (Meses)',
        default=12,
        required=True
    )

    date_end = fields.Date(
        string='Fecha de Finalización',
        compute='_compute_date_end',
        store=True
    )

    auto_renewal = fields.Boolean(
        string='Renovación Automática',
        help='El contrato se renovará automáticamente'
    )

    billing_cycle = fields.Selection([
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('semiannual', 'Semestral'),
        ('annual', 'Anual')
    ], string='Ciclo de Facturación', default='monthly', required=True)

    # Valores financieros
    monthly_fee = fields.Monetary(
        string='Tarifa Mensual',
        currency_field='currency_id',
        help='Costo mensual del servicio'
    )

    setup_fee = fields.Monetary(
        string='Costo de Instalación',
        currency_field='currency_id',
        help='Costo único de instalación'
    )

    deposit_amount = fields.Monetary(
        string='Depósito/Garantía',
        currency_field='currency_id',
        help='Monto del depósito de garantía'
    )

    contract_value = fields.Monetary(
        string='Valor Total del Contrato',
        currency_field='currency_id',
        compute='_compute_contract_value',
        store=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        required=True
    )

    # Observaciones
    notes = fields.Text(
        string='Observaciones',
        help='Notas adicionales sobre el contrato'
    )

    contract_manager_id = fields.Many2one(
        'res.users',
        string='Responsable del Contrato',
        default=lambda self: self.env.user,
        required=True
    )

    # === PASO 4: Confirmación ===
    summary_html = fields.Html(
        string='Resumen del Contrato',
        compute='_compute_summary_html'
    )

    @api.depends('date_start', 'duration_months')
    def _compute_date_end(self):
        """Calcular fecha de finalización"""
        for wizard in self:
            if wizard.date_start and wizard.duration_months:
                wizard.date_end = wizard.date_start + timedelta(days=wizard.duration_months * 30)
            else:
                wizard.date_end = False

    @api.depends('monthly_fee', 'duration_months', 'setup_fee', 'deposit_amount')
    def _compute_contract_value(self):
        """Calcular valor total del contrato"""
        for wizard in self:
            monthly_total = (wizard.monthly_fee or 0) * (wizard.duration_months or 0)
            wizard.contract_value = monthly_total + (wizard.setup_fee or 0) + (wizard.deposit_amount or 0)

    @api.depends('partner_id', 'legal_contact_id', 'contract_type_id', 'monthly_fee', 'duration_months')
    def _compute_summary_html(self):
        """Generar resumen HTML del contrato"""
        for wizard in self:
            if not wizard.partner_id and not wizard.create_new_company:
                wizard.summary_html = "<p>Complete la información de la empresa para ver el resumen.</p>"
                continue

            company_name = wizard.partner_id.name if wizard.partner_id else wizard.company_name
            legal_name = wizard.legal_contact_id.name if wizard.legal_contact_id else wizard.legal_representative_name

            wizard.summary_html = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h3 style="color: #2E7D32; margin-bottom: 20px;">📋 Resumen del Contrato</h3>

                <div style="background: #F5F5F5; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h4 style="margin-top: 0; color: #1976D2;">🏢 Información de la Empresa</h4>
                    <p><strong>Empresa:</strong> {company_name or 'No especificada'}</p>
                    <p><strong>Representante Legal:</strong> {legal_name or 'No especificado'}</p>
                </div>

                <div style="background: #E8F5E8; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h4 style="margin-top: 0; color: #2E7D32;">📄 Detalles del Contrato</h4>
                    <p><strong>Tipo:</strong> {wizard.contract_type_id.name if wizard.contract_type_id else 'No seleccionado'}</p>
                    <p><strong>Duración:</strong> {wizard.duration_months} meses</p>
                    <p><strong>Fecha de Inicio:</strong> {wizard.date_start.strftime('%d/%m/%Y') if wizard.date_start else 'No especificada'}</p>
                    <p><strong>Fecha de Finalización:</strong> {wizard.date_end.strftime('%d/%m/%Y') if wizard.date_end else 'No calculada'}</p>
                    <p><strong>Renovación Automática:</strong> {'Sí' if wizard.auto_renewal else 'No'}</p>
                </div>

                <div style="background: #FFF3E0; padding: 15px; border-radius: 8px;">
                    <h4 style="margin-top: 0; color: #F57C00;">💰 Información Financiera</h4>
                    <p><strong>Tarifa Mensual:</strong> {wizard.currency_id.symbol} {'{:,.2f}'.format(wizard.monthly_fee or 0)}</p>
                    <p><strong>Costo de Instalación:</strong> {wizard.currency_id.symbol} {'{:,.2f}'.format(wizard.setup_fee or 0)}</p>
                    <p><strong>Depósito:</strong> {wizard.currency_id.symbol} {'{:,.2f}'.format(wizard.deposit_amount or 0)}</p>
                    <p style="font-size: 18px; font-weight: bold; color: #2E7D32;"><strong>Valor Total:</strong> {wizard.currency_id.symbol} {'{:,.2f}'.format(wizard.contract_value or 0)}</p>
                </div>
            </div>
            """

    @api.onchange('contract_type_id')
    def _onchange_contract_type_id(self):
        """Actualizar valores por defecto según el tipo"""
        if self.contract_type_id:
            defaults = self.contract_type_id.get_default_values()
            self.update(defaults)
            self.template_id = self.contract_type_id.template_id

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Actualizar campos cuando se selecciona una empresa"""
        if self.partner_id:
            self.create_new_company = False
            # Buscar representante legal asociado
            legal_rep = self.env['res.partner'].search([
                ('parent_id', '=', self.partner_id.id),
                ('is_legal_representative', '=', True)
            ], limit=1)
            if legal_rep:
                self.legal_contact_id = legal_rep

    def action_next_step(self):
        """Avanzar al siguiente paso"""
        if self.state == 'step1':
            if not self.contract_type_id:
                raise ValidationError(_('Debe seleccionar un tipo de contrato.'))
            self.state = 'step2'
        elif self.state == 'step2':
            self._validate_step2()
            self.state = 'step3'
        elif self.state == 'step3':
            self._validate_step3()
            self.state = 'step4'
        elif self.state == 'step4':
            return self.action_create_contract()

        return self._reopen_wizard()

    def action_previous_step(self):
        """Retroceder al paso anterior"""
        if self.state == 'step2':
            self.state = 'step1'
        elif self.state == 'step3':
            self.state = 'step2'
        elif self.state == 'step4':
            self.state = 'step3'

        return self._reopen_wizard()

    def _validate_step2(self):
        """Validar información del paso 2"""
        if not self.partner_id and not self.create_new_company:
            raise ValidationError(_('Debe seleccionar una empresa existente o crear una nueva.'))

        if self.create_new_company:
            if not self.company_name:
                raise ValidationError(_('Debe especificar el nombre de la empresa.'))
            if not self.company_tax_id:
                raise ValidationError(_('Debe especificar la cédula jurídica.'))

        if not self.legal_contact_id and not self.create_new_legal_rep:
            raise ValidationError(_('Debe seleccionar un representante legal existente o crear uno nuevo.'))

        if self.create_new_legal_rep:
            if not self.legal_representative_name:
                raise ValidationError(_('Debe especificar el nombre del representante legal.'))
            if not self.legal_id_number:
                raise ValidationError(_('Debe especificar la cédula del representante.'))

    def _validate_step3(self):
        """Validar información del paso 3"""
        if not self.date_start:
            raise ValidationError(_('Debe especificar la fecha de inicio.'))
        if self.duration_months <= 0:
            raise ValidationError(_('La duración debe ser mayor a 0 meses.'))
        if not self.monthly_fee and self.contract_type_id.code != 'DEVICE_SALE':
            raise ValidationError(_('Debe especificar la tarifa mensual.'))

    def _reopen_wizard(self):
        """Reabrir el wizard en el paso actual"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'contract.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }

    def action_create_contract(self):
        """Crear el contrato final"""
        self.ensure_one()

        # Crear o actualizar empresa
        if self.create_new_company:
            partner = self._create_company()
        else:
            partner = self.partner_id

        # Crear o actualizar representante legal
        if self.create_new_legal_rep:
            legal_contact = self._create_legal_representative(partner)
        else:
            legal_contact = self.legal_contact_id

        # Crear el contrato
        contract_vals = {
            'partner_id': partner.id,
            'legal_contact_id': legal_contact.id,
            'contract_type_id': self.contract_type_id.id,
            'template_id': self.template_id.id if self.template_id else False,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'duration_months': self.duration_months,
            'auto_renewal': self.auto_renewal,
            'billing_cycle': self.billing_cycle,
            'monthly_fee': self.monthly_fee,
            'setup_fee': self.setup_fee,
            'deposit_amount': self.deposit_amount,
            'contract_value': self.contract_value,
            'currency_id': self.currency_id.id,
            'notes': self.notes,
            'contract_manager_id': self.contract_manager_id.id,
            'state': 'nuevo',
        }

        contract = self.env['contract.general'].create(contract_vals)

        # Mostrar el contrato creado
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'contract.general',
            'view_mode': 'form',
            'res_id': contract.id,
            'target': 'current',
            'context': {'form_view_initial_mode': 'edit'},
        }

    def _create_company(self):
        """Crear nueva empresa"""
        vals = {
            'name': self.company_name,
            'company_legal_name': self.company_legal_name,
            'company_tax_id': self.company_tax_id,
            'company_registration': self.company_registration,
            'email': self.company_email,
            'phone': self.company_phone,
            'street': self.company_street,
            'city': self.company_city,
            'state_id': self.company_state_id.id if self.company_state_id else False,
            'zip': self.company_zip,
            'country_id': self.company_country_id.id if self.company_country_id else False,
            'is_company': True,
            'customer_rank': 1,
        }
        return self.env['res.partner'].create(vals)

    def _create_legal_representative(self, company):
        """Crear nuevo representante legal"""
        vals = {
            'name': self.legal_representative_name,
            'email': self.legal_email,
            'phone': self.legal_phone,
            'parent_id': company.id,
            'is_company': False,
            'is_legal_representative': True,
            'legal_position': self.legal_position,
            'legal_hierarchy': self.legal_hierarchy,
            'legal_id_number': self.legal_id_number,
        }
        return self.env['res.partner'].create(vals)

class ContractWizardLine(models.TransientModel):
    _name = 'contract.wizard.line'
    _description = 'Línea del Asistente de Contrato'

    wizard_id = fields.Many2one(
        'contract.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )

    name = fields.Text(string='Descripción', required=True)
    quantity = fields.Float(string='Cantidad', default=1.0, required=True)
    unit_price = fields.Monetary(
        string='Precio Unitario',
        currency_field='currency_id',
        required=True
    )
    subtotal = fields.Monetary(
        string='Subtotal',
        currency_field='currency_id',
        compute='_compute_subtotal'
    )
    currency_id = fields.Many2one(
        related='wizard_id.currency_id',
        string='Moneda'
    )

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    def _prepare_contract_line_values(self, contract_id):
        """Preparar valores para la línea del contrato"""
        return {
            'contract_id': contract_id,
            'name': self.name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
        }