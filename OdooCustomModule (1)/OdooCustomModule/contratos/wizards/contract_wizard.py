# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class ContractWizard(models.TransientModel):
    _name = 'contract.wizard'
    _description = 'Asistente para Creación de Contratos'

    # Paso 1: Información básica
    step = fields.Selection([
        ('step1', 'Información del Cliente'),
        ('step2', 'Tipo y Configuración'),
        ('step3', 'Representante Legal'),
        ('step4', 'Detalles Financieros'),
        ('step5', 'Revisión y Confirmación')
    ], string='Paso', default='step1', required=True)

    # Información del cliente (Paso 1)
    partner_id = fields.Many2one(
        'res.partner',
        string='Empresa Cliente',
        domain=[('is_company', '=', True)],
        required=True
    )

    create_new_partner = fields.Boolean(
        string='Crear Nueva Empresa',
        default=False
    )

    partner_name = fields.Char(string='Nombre de la Empresa')
    partner_email = fields.Char(string='Email de la Empresa')
    partner_phone = fields.Char(string='Teléfono de la Empresa')
    partner_vat = fields.Char(string='Identificación Fiscal')

    # Tipo y configuración (Paso 2)
    contract_type_id = fields.Many2one(
        'contract.type',
        string='Tipo de Contrato',
        required=True
    )

    template_id = fields.Many2one(
        'contract.template',
        string='Plantilla de Contrato'
    )

    date_start = fields.Date(
        string='Fecha de Inicio',
        default=fields.Date.today,
        required=True
    )

    duration_months = fields.Integer(
        string='Duración (meses)',
        default=12,
        required=True
    )

    auto_renewal = fields.Boolean(
        string='Renovación Automática',
        default=True
    )

    service_description = fields.Text(
        string='Descripción de Servicios',
        required=True
    )

    # Representante legal (Paso 3)
    legal_contact_id = fields.Many2one(
        'res.partner',
        string='Contacto Legal Existente'
    )

    create_new_legal_contact = fields.Boolean(
        string='Crear Nuevo Representante',
        default=True
    )

    legal_representative_name = fields.Char(
        string='Nombre Completo',
        required=True
    )

    legal_representative_position = fields.Char(
        string='Puesto/Cargo',
        required=True
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
        string='Cédula',
        required=True
    )

    legal_representative_email = fields.Char(
        string='Email',
        required=True
    )

    legal_representative_phone = fields.Char(string='Teléfono')
    legal_representative_address = fields.Text(string='Dirección')

    # Detalles financieros (Paso 4)
    contract_value = fields.Monetary(
        string='Valor Total',
        currency_field='currency_id',
        required=True
    )

    monthly_fee = fields.Monetary(
        string='Tarifa Mensual',
        currency_field='currency_id'
    )

    setup_fee = fields.Monetary(
        string='Costo de Configuración',
        currency_field='currency_id'
    )

    deposit = fields.Monetary(
        string='Depósito de Garantía',
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id
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

    # Líneas de contrato
    line_ids = fields.One2many(
        'contract.wizard.line',
        'wizard_id',
        string='Líneas del Contrato'
    )

    # Configuración adicional
    contract_manager_id = fields.Many2one(
        'res.users',
        string='Responsable del Contrato',
        default=lambda self: self.env.user,
        required=True
    )

    special_conditions = fields.Html(string='Condiciones Especiales')
    internal_notes = fields.Text(string='Notas Internas')

    @api.onchange('contract_type_id')
    def _onchange_contract_type(self):
        if self.contract_type_id:
            self.duration_months = self.contract_type_id.default_duration
            self.auto_renewal = self.contract_type_id.auto_renewal
            self.template_id = self.contract_type_id.template_id
            self.monthly_fee = self.contract_type_id.default_monthly_fee
            self.setup_fee = self.contract_type_id.default_setup_fee

            if not self.service_description:
                self.service_description = f"Servicios de {self.contract_type_id.name}"

            # Calcular valor total basado en tarifa mensual
            if self.monthly_fee and self.duration_months:
                self.contract_value = self.monthly_fee * self.duration_months + (self.setup_fee or 0)

    @api.onchange('monthly_fee', 'duration_months', 'setup_fee')
    def _onchange_calculate_total(self):
        if self.monthly_fee and self.duration_months:
            self.contract_value = self.monthly_fee * self.duration_months + (self.setup_fee or 0)

    @api.onchange('legal_contact_id')
    def _onchange_legal_contact(self):
        if self.legal_contact_id:
            self.legal_representative_name = self.legal_contact_id.name
            self.legal_representative_email = self.legal_contact_id.email
            self.legal_representative_phone = self.legal_contact_id.phone

            # Construir dirección
            address_parts = []
            if self.legal_contact_id.street:
                address_parts.append(self.legal_contact_id.street)
            if self.legal_contact_id.city:
                address_parts.append(self.legal_contact_id.city)
            if self.legal_contact_id.country_id:
                address_parts.append(self.legal_contact_id.country_id.name)
            self.legal_representative_address = ', '.join(address_parts)

    def action_next_step(self):
        """Avanzar al siguiente paso"""
        self.ensure_one()

        if self.step == 'step1':
            self._validate_step1()
            self.step = 'step2'
        elif self.step == 'step2':
            self._validate_step2()
            self.step = 'step3'
        elif self.step == 'step3':
            self._validate_step3()
            self.step = 'step4'
        elif self.step == 'step4':
            self._validate_step4()
            self.step = 'step5'

        return self._return_wizard_action()

    def action_previous_step(self):
        """Retroceder al paso anterior"""
        self.ensure_one()

        if self.step == 'step2':
            self.step = 'step1'
        elif self.step == 'step3':
            self.step = 'step2'
        elif self.step == 'step4':
            self.step = 'step3'
        elif self.step == 'step5':
            self.step = 'step4'

        return self._return_wizard_action()

    def action_create_contract(self):
        """Crear el contrato final"""
        self.ensure_one()
        self._validate_all_steps()

        # Crear empresa si es necesario
        if self.create_new_partner:
            partner = self._create_partner()
        else:
            partner = self.partner_id

        # Crear contacto legal si es necesario
        if self.create_new_legal_contact:
            legal_contact = self._create_legal_contact()
        else:
            legal_contact = self.legal_contact_id

        # Crear contrato
        contract_vals = self._prepare_contract_values(partner, legal_contact)
        contract = self.env['contract.general'].create(contract_vals)

        # Crear líneas del contrato
        if self.line_ids:
            for line in self.line_ids:
                line_vals = line._prepare_contract_line_values(contract.id)
                self.env['contract.general.line'].create(line_vals)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Contrato Creado'),
            'res_model': 'contract.general',
            'res_id': contract.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _validate_step1(self):
        """Validar paso 1"""
        if not self.partner_id and not self.create_new_partner:
            raise ValidationError(_('Debe seleccionar una empresa o crear una nueva.'))

        if self.create_new_partner and not self.partner_name:
            raise ValidationError(_('El nombre de la empresa es requerido.'))

    def _validate_step2(self):
        """Validar paso 2"""
        if not self.contract_type_id:
            raise ValidationError(_('Debe seleccionar un tipo de contrato.'))

        if not self.service_description:
            raise ValidationError(_('La descripción de servicios es requerida.'))

    def _validate_step3(self):
        """Validar paso 3"""
        if not self.legal_contact_id and not self.create_new_legal_contact:
            raise ValidationError(_('Debe seleccionar un representante legal o crear uno nuevo.'))

        if self.create_new_legal_contact:
            required_fields = ['legal_representative_name', 'legal_representative_position',
                             'legal_representative_id_number', 'legal_representative_email']
            for field in required_fields:
                if not getattr(self, field):
                    field_label = self._fields[field].string
                    raise ValidationError(_('El campo %s es requerido.') % field_label)

    def _validate_step4(self):
        """Validar paso 4"""
        if not self.contract_value or self.contract_value <= 0:
            raise ValidationError(_('El valor del contrato debe ser mayor que cero.'))

    def _validate_all_steps(self):
        """Validar todos los pasos"""
        self._validate_step1()
        self._validate_step2()
        self._validate_step3()
        self._validate_step4()

    def _create_partner(self):
        """Crear nueva empresa"""
        vals = {
            'name': self.partner_name,
            'is_company': True,
            'customer_rank': 1,
            'email': self.partner_email,
            'phone': self.partner_phone,
            'vat': self.partner_vat,
        }
        return self.env['res.partner'].create(vals)

    def _create_legal_contact(self):
        """Crear nuevo contacto legal"""
        vals = {
            'name': self.legal_representative_name,
            'email': self.legal_representative_email,
            'phone': self.legal_representative_phone,
            'is_company': False,
            'parent_id': self.partner_id.id if not self.create_new_partner else False,
            'is_legal_representative': True,
            'legal_position': self.legal_representative_position,
            'legal_hierarchy': self.legal_representative_hierarchy,
            'legal_id_number': self.legal_representative_id_number,
        }

        # Agregar dirección si existe
        if self.legal_representative_address:
            address_parts = self.legal_representative_address.split(',')
            if len(address_parts) > 0:
                vals['street'] = address_parts[0].strip()
            if len(address_parts) > 1:
                vals['city'] = address_parts[1].strip()

        return self.env['res.partner'].create(vals)

    def _prepare_contract_values(self, partner, legal_contact):
        """Preparar valores para el contrato"""
        return {
            'partner_id': partner.id,
            'legal_contact_id': legal_contact.id,
            'contract_type_id': self.contract_type_id.id,
            'template_id': self.template_id.id if self.template_id else False,
            'date_start': self.date_start,
            'duration_months': self.duration_months,
            'auto_renewal': self.auto_renewal,
            'service_description': self.service_description,
            'legal_representative_name': self.legal_representative_name,
            'legal_representative_position': self.legal_representative_position,
            'legal_representative_hierarchy': self.legal_representative_hierarchy,
            'legal_representative_id_number': self.legal_representative_id_number,
            'legal_representative_email': self.legal_representative_email,
            'legal_representative_phone': self.legal_representative_phone,
            'legal_representative_address': self.legal_representative_address,
            'contract_value': self.contract_value,
            'monthly_fee': self.monthly_fee,
            'setup_fee': self.setup_fee,
            'deposit': self.deposit,
            'currency_id': self.currency_id.id,
            'billing_cycle': self.billing_cycle,
            'payment_method': self.payment_method,
            'contract_manager_id': self.contract_manager_id.id,
            'special_conditions': self.special_conditions,
            'internal_notes': self.internal_notes,
        }

    def _return_wizard_action(self):
        """Retornar acción del wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Asistente de Contrato'),
            'res_model': 'contract.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


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