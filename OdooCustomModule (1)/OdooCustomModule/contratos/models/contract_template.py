# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import base64
import re
from datetime import timedelta

class ContractTemplate(models.Model):
    _name = 'contract.template'
    _description = 'Plantilla de Contrato'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nombre de la Plantilla',
        required=True,
        translate=True
    )

    code = fields.Char(
        string='Código',
        required=True,
        help='Código único para identificar la plantilla'
    )

    description = fields.Text(
        string='Descripción',
        translate=True
    )

    active = fields.Boolean(string='Activo', default=True)
    sequence = fields.Integer(string='Secuencia', default=10)

    # Configuración visual
    company_logo = fields.Binary(
        string='Logo de la Empresa',
        help='Logo que aparecerá en el contrato'
    )

    logo_size = fields.Selection([
        ('small', 'Pequeño (100px)'),
        ('medium', 'Mediano (150px)'),
        ('large', 'Grande (200px)'),
        ('custom', 'Personalizado')
    ], string='Tamaño del Logo', default='medium')

    logo_custom_width = fields.Integer(
        string='Ancho Personalizado (px)',
        default=150
    )

    logo_position = fields.Selection([
        ('left', 'Izquierda'),
        ('center', 'Centro'),
        ('right', 'Derecha')
    ], string='Posición del Logo', default='center')

    # Colores personalizables
    primary_color = fields.Char(
        string='Color Primario',
        default='#1f2937',
        help='Color principal para títulos y elementos destacados'
    )

    secondary_color = fields.Char(
        string='Color Secundario',
        default='#6b7280',
        help='Color secundario para subtítulos'
    )

    accent_color = fields.Char(
        string='Color de Acento',
        default='#3b82f6',
        help='Color para enlaces y elementos de acento'
    )

    text_color = fields.Char(
        string='Color del Texto',
        default='#374151',
        help='Color principal del texto'
    )

    background_color = fields.Char(
        string='Color de Fondo',
        default='#ffffff',
        help='Color de fondo del documento'
    )

    # Tipografía
    font_family = fields.Selection([
        ('Arial, sans-serif', 'Arial'),
        ('Helvetica, sans-serif', 'Helvetica'),
        ('Times New Roman, serif', 'Times New Roman'),
        ('Georgia, serif', 'Georgia'),
        ('Courier New, monospace', 'Courier New'),
        ('custom', 'Personalizada')
    ], string='Familia de Fuente', default='Arial, sans-serif')

    custom_font_family = fields.Char(
        string='Fuente Personalizada',
        help='Especificar fuente personalizada (ej: "Open Sans", sans-serif)'
    )

    font_size_base = fields.Integer(
        string='Tamaño Base de Fuente',
        default=12,
        help='Tamaño base de fuente en puntos'
    )

    # Contenido del contrato
    header_content = fields.Html(
        string='Encabezado del Contrato',
        default='''
        <div class="contract-header">
            <h1>CONTRATO DE SERVICIOS</h1>
            <p>Entre ${object.env.company.name} y ${object.partner_id.name}</p>
        </div>
        ''',
        help='Contenido HTML del encabezado. Usar ${object.campo} para variables dinámicas'
    )

    introduction_content = fields.Html(
        string='Introducción',
        default='''
        <div class="contract-intro">
            <p>Por medio del presente documento se establece un contrato de servicios entre:</p>
            <div class="parties">
                <div class="party">
                    <strong>EL PROVEEDOR:</strong> ${object.env.company.name}<br/>
                    Identificación: ${object.env.company.vat or 'No especificado'}<br/>
                    Dirección: ${object.env.company.street or ''} ${object.env.company.city or ''}<br/>
                    Teléfono: ${object.env.company.phone or ''}<br/>
                    Email: ${object.env.company.email or ''}
                </div>
                <div class="party">
                    <strong>EL CLIENTE:</strong> ${object.partner_id.name}<br/>
                    Identificación: ${object.partner_id.vat or 'No especificado'}<br/>
                    Dirección: ${object.partner_id.contact_address}<br/>
                    Teléfono: ${object.partner_id.phone or ''}<br/>
                    Email: ${object.partner_id.email or ''}
                </div>
            </div>
        </div>
        ''',
        help='Contenido de introducción con información de las partes'
    )

    terms_content = fields.Html(
        string='Términos y Condiciones',
        default='''
        <div class="contract-terms">
            <h2>TÉRMINOS Y CONDICIONES</h2>

            <h3>1. OBJETO DEL CONTRATO</h3>
            <p>El presente contrato tiene por objeto la prestación de servicios de ${object.service_description}.</p>

            <h3>2. VIGENCIA</h3>
            <p>El presente contrato tendrá una vigencia de ${object.duration_months} meses, iniciando el ${object.date_start} y finalizando el ${object.date_end}.</p>

            <h3>3. VALOR Y FORMA DE PAGO</h3>
            <p>El valor total del presente contrato es de ${object.currency_id.symbol} ${object.contract_value}.</p>
            <p>La forma de pago será: ${object.get_billing_cycle_display()}.</p>

            <h3>4. REPRESENTANTE LEGAL</h3>
            <p>El cliente designa como representante legal a ${object.legal_representative_name}, 
            quien ostenta el cargo de ${object.legal_representative_position} 
            e identificado con cédula número ${object.legal_representative_id_number}.</p>

            <h3>5. RENOVACIÓN AUTOMÁTICA</h3>
            % if object.auto_renewal:
            <p>Este contrato se renovará automáticamente por períodos iguales al inicial, 
            salvo notificación escrita con 30 días de anticipación.</p>
            % else:
            <p>Este contrato NO se renovará automáticamente. Deberá gestionarse una renovación manual antes del vencimiento.</p>
            % endif
        </div>
        ''',
        help='Términos y condiciones principales del contrato'
    )

    financial_details_content = fields.Html(
        string='Detalles Financieros',
        default='''
        <div class="financial-details">
            <h2>DETALLES FINANCIEROS</h2>
            <table class="financial-table">
                <thead>
                    <tr>
                        <th>Concepto</th>
                        <th>Valor</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Valor Total del Contrato</td>
                        <td>${object.currency_id.symbol} ${object.contract_value}</td>
                    </tr>
                    % if object.monthly_fee:
                    <tr>
                        <td>Tarifa Mensual</td>
                        <td>${object.currency_id.symbol} ${object.monthly_fee}</td>
                    </tr>
                    % endif
                    % if object.setup_fee:
                    <tr>
                        <td>Costo de Configuración</td>
                        <td>${object.currency_id.symbol} ${object.setup_fee}</td>
                    </tr>
                    % endif
                    % if object.deposit:
                    <tr>
                        <td>Depósito de Garantía</td>
                        <td>${object.currency_id.symbol} ${object.deposit}</td>
                    </tr>
                    % endif
                    <tr>
                        <td>Ciclo de Facturación</td>
                        <td>${object.get_billing_cycle_display()}</td>
                    </tr>
                    <tr>
                        <td>Método de Pago</td>
                        <td>${object.get_payment_method_display()}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        ''',
        help='Tabla de detalles financieros del contrato'
    )

    special_conditions_content = fields.Html(
        string='Condiciones Especiales',
        default='''
        <div class="special-conditions">
            % if object.special_conditions:
            <h2>CONDICIONES ESPECIALES</h2>
            ${object.special_conditions}
            % endif
        </div>
        ''',
        help='Sección para condiciones especiales del contrato'
    )

    signature_content = fields.Html(
        string='Área de Firmas',
        default='''
        <div class="signatures">
            <h2>FIRMAS</h2>
            <div class="signature-area">
                <div class="signature-box">
                    <p><strong>POR EL PROVEEDOR:</strong></p>
                    <div class="signature-line"></div>
                    <p>${object.env.company.name}</p>
                    <p>Representante Legal</p>
                </div>

                <div class="signature-box">
                    <p><strong>POR EL CLIENTE:</strong></p>
                    <div class="signature-line"></div>
                    <p>${object.legal_representative_name}</p>
                    <p>${object.legal_representative_position}</p>
                    <p>Cédula: ${object.legal_representative_id_number}</p>
                </div>
            </div>

            <div class="contract-footer">
                <p>Lugar y fecha: _________________, ${object.date_start}</p>
            </div>
        </div>
        ''',
        help='Área de firmas y fecha del contrato'
    )

    footer_content = fields.Html(
        string='Pie de Página',
        default='''
        <div class="contract-footer-info">
            <p class="footer-text">
                Documento generado automáticamente el ${datetime.now().strftime('%d/%m/%Y')} 
                por el sistema de gestión de contratos.
            </p>
            <p class="footer-text">
                Contrato No. ${object.name} - ${object.env.company.name}
            </p>
        </div>
        ''',
        help='Información del pie de página'
    )

    # CSS personalizado
    custom_css = fields.Text(
        string='CSS Personalizado',
        help='CSS adicional para personalizar la apariencia del contrato'
    )

    # Configuración de secciones
    section_ids = fields.One2many(
        'contract.template.section',
        'template_id',
        string='Secciones del Contrato'
    )

    @api.constrains('code')
    def _check_code_unique(self):
        for record in self:
            if record.code:
                existing = self.search([
                    ('code', '=', record.code),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(_('El código de la plantilla debe ser único.'))

    @api.model
    def create(self, vals):
        template = super(ContractTemplate, self).create(vals)
        template._create_default_sections()
        return template

    def _create_default_sections(self):
        """Crear secciones por defecto para la plantilla"""
        default_sections = [
            {'name': 'Encabezado', 'sequence': 10, 'content_field': 'header_content'},
            {'name': 'Introducción', 'sequence': 20, 'content_field': 'introduction_content'},
            {'name': 'Términos y Condiciones', 'sequence': 30, 'content_field': 'terms_content'},
            {'name': 'Detalles Financieros', 'sequence': 40, 'content_field': 'financial_details_content'},
            {'name': 'Condiciones Especiales', 'sequence': 50, 'content_field': 'special_conditions_content'},
            {'name': 'Firmas', 'sequence': 60, 'content_field': 'signature_content'},
            {'name': 'Pie de Página', 'sequence': 70, 'content_field': 'footer_content'},
        ]

        for section_data in default_sections:
            self.env['contract.template.section'].create({
                'template_id': self.id,
                'name': section_data['name'],
                'sequence': section_data['sequence'],
                'content_field': section_data['content_field'],
                'active': True
            })

    def generate_contract_html(self, contract):
        """Generar HTML completo del contrato"""
        self.ensure_one()

        # Generar CSS dinámico
        css = self._generate_dynamic_css()

        # Generar secciones ordenadas
        sections = self._generate_contract_sections(contract)

        # Construir HTML completo
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Contrato {contract.name}</title>
            {css}
        </head>
        <body>
            {self._generate_logo_html()}
            {''.join(sections)}
        </body>
        </html>
        """

        return html_content

    def _generate_logo_html(self):
        """Generar HTML del logo"""
        if not self.company_logo:
            return ''

        logo_width = {
            'small': '100px',
            'medium': '150px',
            'large': '200px',
            'custom': f'{self.logo_custom_width}px'
        }.get(self.logo_size, '150px')

        logo_base64 = base64.b64encode(self.company_logo).decode()

        return f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}" 
                 style="width: {logo_width}; height: auto;" 
                 alt="Logo de la empresa" />
        </div>
        """

    def _generate_contract_sections(self, contract):
        """Generar todas las secciones del contrato"""
        sections = []
        template_context = self._prepare_template_context(contract)

        for section in self.section_ids.filtered('active').sorted('sequence'):
            if section.content_field and hasattr(self, section.content_field):
                content = getattr(self, section.content_field)
                if content:
                    # Procesar variables dinámicas
                    processed_content = self._process_template_variables(content, template_context)
                    sections.append(f'<div class="contract-section">{processed_content}</div>')

        return sections

    def _prepare_template_context(self, contract):
        """Preparar contexto para las variables de plantilla"""
        return {
            'object': contract,
            'env': self.env,
            'datetime': __import__('datetime'),
        }

    def _process_template_variables(self, content, context):
        """Procesar variables dinámicas en el contenido"""
        if not content:
            return ''

        # Procesar variables ${object.field}
        def replace_variable(match):
            var_path = match.group(1)
            try:
                # Evaluar la variable en el contexto
                result = eval(var_path, {"__builtins__": {}}, context)
                return str(result) if result is not None else ''
            except:
                return f"${{{var_path}}}"  # Devolver variable original si hay error

        # Reemplazar variables ${...}
        content = re.sub(r'\$\{([^}]+)\}', replace_variable, content)

        # Procesar condicionales simples % if ... % endif
        content = self._process_template_conditionals(content, context)

        return content

    def _process_template_conditionals(self, content, context):
        """Procesar condicionales simples en las plantillas"""
        # Patrón para % if condition: ... % endif
        pattern = r'% if ([^:]+):\s*(.*?)\s*% endif'

        def replace_conditional(match):
            condition = match.group(1).strip()
            content_if = match.group(2).strip()

            try:
                # Evaluar condición
                if eval(condition, {"__builtins__": {}}, context):
                    return content_if
                else:
                    return ''
            except:
                return content_if  # Si hay error, mostrar contenido

        return re.sub(pattern, replace_conditional, content, flags=re.DOTALL)

    def _generate_dynamic_css(self):
        """Generar CSS dinámico basado en la configuración"""
        font_family = self.custom_font_family if self.font_family == 'custom' else self.font_family

        logo_width = {
            'small': '100px',
            'medium': '150px', 
            'large': '200px',
            'custom': f'{self.logo_custom_width}px'
        }.get(self.logo_size, '150px')

        css = f"""
        <style>
        body {{
            font-family: {font_family};
            font-size: {self.font_size_base}px;
            color: {self.text_color};
            background-color: {self.background_color};
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }}

        h1 {{
            color: {self.primary_color};
            font-size: {self.font_size_base + 12}px;
            margin-bottom: 20px;
        }}

        h2 {{
            color: {self.primary_color};
            font-size: {self.font_size_base + 8}px;
            margin-bottom: 15px;
        }}

        h3 {{
            color: {self.secondary_color};
            font-size: {self.font_size_base + 4}px;
            margin-bottom: 10px;
        }}

        h4 {{
            color: {self.secondary_color};
            font-size: {self.font_size_base + 2}px;
            margin-bottom: 8px;
        }}

        .logo-container {{
            text-align: {self.logo_position};
            margin-bottom: 30px;
        }}

        .contract-header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid {self.primary_color};
            padding-bottom: 20px;
        }}

        .parties {{
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
        }}

        .party {{
            flex: 1;
            margin: 0 10px;
            padding: 15px;
            border: 1px solid {self.secondary_color};
            border-radius: 5px;
        }}

        .financial-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        .financial-table th,
        .financial-table td {{
            border: 1px solid {self.secondary_color};
            padding: 10px;
            text-align: left;
        }}

        .financial-table th {{
            background-color: {self.primary_color};
            color: white;
        }}

        .signature-area {{
            display: flex;
            justify-content: space-between;
            margin: 40px 0;
        }}

        .signature-box {{
            flex: 1;
            margin: 0 20px;
            text-align: center;
        }}

        .signature-line {{
            border-bottom: 1px solid {self.text_color};
            height: 50px;
            margin: 20px 0;
        }}

        .contract-footer {{
            text-align: center;
            margin-top: 40px;
            border-top: 1px solid {self.secondary_color};
            padding-top: 20px;
        }}

        .contract-footer-info {{
            font-size: {self.font_size_base - 2}px;
            color: {self.secondary_color};
            text-align: center;
            margin-top: 30px;
        }}

        .contract-section {{
            margin-bottom: 25px;
        }}

        .highlight-box {{
            background-color: {self.accent_color}1A;
            border-left: 4px solid {self.accent_color};
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}

        .info-box {{
            background-color: #e8f4fd;
            border: 1px solid {self.accent_color};
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }}

        .warning-box {{
            background-color: #fff3cd;
            border: 1px solid {self.accent_color};
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
        }}

        {self.custom_css or ''}
        </style>
        """

        return css

    def preview_contract(self):
        """Vista previa de la plantilla con datos de ejemplo"""
        self.ensure_one()

        # Crear contrato de ejemplo para la vista previa
        example_contract = self.env['contract.general'].new({
            'name': 'CONT-PREVIEW-001',
            'partner_id': self.env.ref('base.res_partner_3').id,  # Partner de demostración
            'legal_representative_name': 'Juan Pérez González',
            'legal_representative_position': 'Gerente General',
            'legal_representative_id_number': '1-1234-5678',
            'service_description': 'Servicios de monitoreo GPS y telemetría',
            'contract_value': 120000,
            'monthly_fee': 10000,
            'setup_fee': 20000,
            'duration_months': 12,
            'date_start': fields.Date.today(),
            'date_end': fields.Date.today() + timedelta(days=365),
            'auto_renewal': True,
            'billing_cycle': 'monthly',
            'payment_method': 'transfer',
        })

        html_content = self.generate_contract_html(example_contract)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Vista Previa - %s') % self.name,
            'res_model': 'contract.template.preview',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_html_content': html_content,
                'default_template_id': self.id
            }
        }


class ContractTemplateSection(models.Model):
    _name = 'contract.template.section'
    _description = 'Sección de Plantilla de Contrato'
    _order = 'template_id, sequence, id'

    template_id = fields.Many2one(
        'contract.template',
        string='Plantilla',
        required=True,
        ondelete='cascade'
    )

    name = fields.Char(
        string='Nombre de la Sección',
        required=True
    )

    sequence = fields.Integer(string='Secuencia', default=10)

    active = fields.Boolean(string='Activo', default=True)

    content_field = fields.Selection([
        ('header_content', 'Encabezado'),
        ('introduction_content', 'Introducción'),
        ('terms_content', 'Términos y Condiciones'),
        ('financial_details_content', 'Detalles Financieros'),
        ('special_conditions_content', 'Condiciones Especiales'),
        ('signature_content', 'Firmas'),
        ('footer_content', 'Pie de Página'),
    ], string='Campo de Contenido', required=True)

    notes = fields.Text(string='Notas')


class ContractTemplatePreview(models.TransientModel):
    _name = 'contract.template.preview'
    _description = 'Vista Previa de Plantilla'

    template_id = fields.Many2one('contract.template', string='Plantilla')
    html_content = fields.Html(string='Contenido HTML')