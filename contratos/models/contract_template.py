# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ContractTemplate(models.Model):
    _name = 'contract.template'
    _description = 'Plantilla de Contrato'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre de la plantilla'
    )

    description = fields.Text(
        string='Descripción',
        help='Descripción de la plantilla'
    )

    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help='Secuencia para ordenar las plantillas'
    )

    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está desmarcado, no se podrá usar esta plantilla'
    )

    # Contenido de la plantilla
    header_content = fields.Html(
        string='Encabezado',
        help='Contenido del encabezado del contrato'
    )

    body_content = fields.Html(
        string='Cuerpo del Contrato',
        required=True,
        help='Contenido principal del contrato con variables dinámicas'
    )

    footer_content = fields.Html(
        string='Pie de Página',
        help='Contenido del pie de página del contrato'
    )

    # Términos y condiciones
    terms_conditions = fields.Html(
        string='Términos y Condiciones',
        help='Términos y condiciones específicos de esta plantilla'
    )

    # Configuración
    contract_type_ids = fields.Many2many(
        'contract.type',
        'template_contract_type_rel',
        'template_id',
        'type_id',
        string='Tipos de Contrato',
        help='Tipos de contrato que pueden usar esta plantilla'
    )

    # Campos legales específicos para Costa Rica
    legal_framework = fields.Html(
        string='Marco Legal',
        help='Referencias al marco legal costarricense aplicable'
    )

    dispute_resolution = fields.Html(
        string='Resolución de Conflictos',
        help='Cláusulas de resolución de conflictos según legislación CR'
    )

    # Variables disponibles
    available_variables = fields.Text(
        string='Variables Disponibles',
        default="""Variables disponibles para usar en las plantillas:

INFORMACIÓN DE LA EMPRESA:
${object.partner_id.name} - Nombre de la empresa
${object.partner_id.company_legal_name} - Razón social completa
${object.partner_id.company_tax_id} - Cédula jurídica
${object.partner_id.company_registration} - Número de registro
${object.partner_id.email} - Email de la empresa
${object.partner_id.phone} - Teléfono de la empresa
${object.partner_id.street} - Dirección

REPRESENTANTE LEGAL:
${object.legal_representative_name} - Nombre del representante
${object.legal_representative_id} - Cédula del representante
${object.legal_position} - Puesto del representante
${object.legal_hierarchy} - Jerarquía legal

INFORMACIÓN DEL CONTRATO:
${object.name} - Número del contrato
${object.date_start} - Fecha de inicio
${object.date_end} - Fecha de finalización
${object.duration_months} - Duración en meses
${object.monthly_fee} - Tarifa mensual
${object.contract_value} - Valor total
${object.currency_id.symbol} - Símbolo de moneda

FECHAS:
${object.date_start.strftime('%d/%m/%Y')} - Fecha formateada
${object.date_end.strftime('%d de %B de %Y')} - Fecha en español

EMPRESA GEOTRACKING:
${object.company_id.name} - Nombre de nuestra empresa
${object.company_id.street} - Dirección de nuestra empresa
${object.company_id.phone} - Teléfono de nuestra empresa
""",
        readonly=True,
        help='Lista de variables que se pueden usar en las plantillas'
    )

    # Estadísticas
    contract_count = fields.Integer(
        string='Contratos Usando Esta Plantilla',
        compute='_compute_contract_count'
    )

    @api.depends('name')
    def _compute_contract_count(self):
        """Calcular cuántos contratos usan esta plantilla"""
        for template in self:
            template.contract_count = self.env['contract.general'].search_count([
                ('template_id', '=', template.id)
            ])

    def action_view_contracts(self):
        """Ver contratos que usan esta plantilla"""
        self.ensure_one()
        return {
            'name': _('Contratos - %s') % self.name,
            'view_mode': 'tree,form',
            'res_model': 'contract.general',
            'type': 'ir.actions.act_window',
            'domain': [('template_id', '=', self.id)],
            'context': {'default_template_id': self.id}
        }

    def preview_template(self):
        """Vista previa de la plantilla"""
        self.ensure_one()
        # Crear un contrato de ejemplo para la vista previa
        sample_contract = self.env['contract.general'].new({
            'name': 'EJEMPLO-001',
            'date_start': fields.Date.today(),
            'monthly_fee': 25000.0,
            'template_id': self.id,
        })

        # Renderizar la plantilla con datos de ejemplo
        rendered_content = self._render_template_content(sample_contract)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Vista Previa - %s') % self.name,
            'res_model': 'contract.template.preview',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_content': rendered_content,
                'default_template_id': self.id
            }
        }

    def _render_template_content(self, contract):
        """Renderizar el contenido de la plantilla con un contrato específico"""
        self.ensure_one()

        # Combinar todo el contenido
        full_content = f"""
        {self.header_content or ''}
        {self.body_content or ''}
        {self.terms_conditions or ''}
        {self.footer_content or ''}
        """

        # Aquí se haría el reemplazo de variables con los datos del contrato
        # Por simplicidad, retornamos el contenido tal como está
        return full_content

    @api.model
    def create_default_templates(self):
        """Crear plantillas por defecto"""
        default_template = {
            'name': 'Contrato GPS Estándar - Costa Rica',
            'description': 'Plantilla estándar para contratos de servicios GPS en Costa Rica',
            'header_content': '''
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2E7D32; margin-bottom: 10px;">CONTRATO DE SERVICIOS GPS</h1>
                <h2 style="color: #666; font-weight: normal;">Geotracking S.A.</h2>
            </div>
            ''',
            'body_content': '''
            <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <p><strong>CONTRATO NÚMERO:</strong> ${object.name}</p>
                <p><strong>FECHA:</strong> ${object.date_start.strftime('%d de %B de %Y') if object.date_start else 'No especificada'}</p>

                <h3 style="color: #2E7D32; margin-top: 30px;">PARTES CONTRATANTES</h3>

                <p><strong>EMPRESA PRESTADORA:</strong><br/>
                <strong>Geotracking S.A.</strong>, sociedad anónima debidamente constituida bajo las leyes de la República de Costa Rica, con cédula jurídica número [CEDULA_GEOTRACKING], domiciliada en [DIRECCION_GEOTRACKING], representada en este acto por su [CARGO_REPRESENTANTE], [NOMBRE_REPRESENTANTE], mayor de edad, [ESTADO_CIVIL], [PROFESION], vecino de [DOMICILIO], portador de la cédula de identidad número [CEDULA_REPRESENTANTE], con facultades suficientes para este acto.</p>

                <p><strong>EMPRESA CLIENTE:</strong><br/>
                <strong>${object.partner_id.name or 'NOMBRE_EMPRESA'}</strong>, ${object.partner_id.company_legal_name or 'razón social'}, con cédula jurídica número ${object.partner_id.company_tax_id or 'CEDULA_JURIDICA'}, domiciliada en ${object.partner_id.street or 'DIRECCION_EMPRESA'}, representada por ${object.legal_representative_name or 'NOMBRE_REPRESENTANTE_LEGAL'}, mayor de edad, en su calidad de ${object.legal_position or 'CARGO'}, con cédula de identidad número ${object.legal_representative_id or 'CEDULA_REPRESENTANTE'}.</p>

                <h3 style="color: #2E7D32; margin-top: 30px;">OBJETO DEL CONTRATO</h3>

                <p>Por medio del presente contrato, <strong>Geotracking S.A.</strong> se compromete a prestar servicios de rastreo GPS y monitoreo vehicular a <strong>${object.partner_id.name}</strong>, incluyendo:</p>

                <ul>
                    <li>Instalación y configuración de dispositivos GPS</li>
                    <li>Acceso a plataforma web de monitoreo 24/7</li>
                    <li>Soporte técnico especializado</li>
                    <li>Mantenimiento preventivo de equipos</li>
                    <li>Reportes y alertas personalizadas</li>
                </ul>

                <h3 style="color: #2E7D32; margin-top: 30px;">DURACIÓN Y VIGENCIA</h3>

                <p>El presente contrato tendrá una duración de <strong>${object.duration_months or 'X'} meses</strong>, iniciando el <strong>${object.date_start.strftime('%d de %B de %Y') if object.date_start else 'FECHA_INICIO'}</strong> y finalizando el <strong>${object.date_end.strftime('%d de %B de %Y') if object.date_end else 'FECHA_FIN'}</strong>.</p>

                % if object.auto_renewal:
                <p><strong>RENOVACIÓN AUTOMÁTICA:</strong> Este contrato se renovará automáticamente por períodos iguales, salvo aviso contrario con 30 días de anticipación.</p>
                % endif

                <h3 style="color: #2E7D32; margin-top: 30px;">ASPECTOS ECONÓMICOS</h3>

                <p><strong>TARIFA MENSUAL:</strong> ${object.currency_id.symbol if object.currency_id else '₡'} ${'{:,.2f}'.format(object.monthly_fee) if object.monthly_fee else 'X.XXX'} (${object.monthly_fee or 'CANTIDAD EN LETRAS'} colones exactos) mensuales.</p>

                % if object.setup_fee:
                <p><strong>COSTO DE INSTALACIÓN:</strong> ${object.currency_id.symbol if object.currency_id else '₡'} ${'{:,.2f}'.format(object.setup_fee)} (único pago).</p>
                % endif

                % if object.deposit_amount:
                <p><strong>DEPÓSITO DE GARANTÍA:</strong> ${object.currency_id.symbol if object.currency_id else '₡'} ${'{:,.2f}'.format(object.deposit_amount)} (reembolsable al finalizar el contrato).</p>
                % endif

                <p><strong>VALOR TOTAL DEL CONTRATO:</strong> ${object.currency_id.symbol if object.currency_id else '₡'} ${'{:,.2f}'.format(object.contract_value) if object.contract_value else 'X.XXX'}</p>

                <p><strong>FORMA DE PAGO:</strong> ${dict(object._fields['billing_cycle'].selection)[object.billing_cycle] if object.billing_cycle else 'Mensual'}</p>
            </div>
            ''',
            'terms_conditions': '''
            <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h3 style="color: #2E7D32; margin-top: 30px;">TÉRMINOS Y CONDICIONES</h3>

                <p><strong>1. RESPONSABILIDADES DE GEOTRACKING S.A.:</strong></p>
                <ul>
                    <li>Mantener la plataforma operativa 24/7</li>
                    <li>Brindar soporte técnico en horario laboral</li>
                    <li>Realizar mantenimiento preventivo de equipos</li>
                    <li>Garantizar la confidencialidad de la información</li>
                </ul>

                <p><strong>2. RESPONSABILIDADES DEL CLIENTE:</strong></p>
                <ul>
                    <li>Facilitar el acceso para instalación y mantenimiento</li>
                    <li>Realizar pagos según cronograma establecido</li>
                    <li>Informar inmediatamente sobre daños o irregularidades</li>
                    <li>Usar el servicio conforme a las condiciones pactadas</li>
                </ul>

                <p><strong>3. LIMITACIONES:</strong></p>
                <ul>
                    <li>El servicio depende de cobertura celular y GPS</li>
                    <li>No incluye recuperación de vehículos robados</li>
                    <li>Geotracking no se hace responsable por daños indirectos</li>
                </ul>

                <p><strong>4. TERMINACIÓN:</strong></p>
                <p>Cualquiera de las partes puede terminar este contrato con 30 días de aviso previo por escrito.</p>

                <p><strong>5. LEGISLACIÓN APLICABLE:</strong></p>
                <p>Este contrato se rige por las leyes de la República de Costa Rica. Cualquier disputa será resuelta por los tribunales costarricenses.</p>
            </div>
            ''',
            'footer_content': '''
            <div style="margin-top: 50px; text-align: center;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="width: 50%; text-align: center; padding: 20px; border-top: 1px solid #333;">
                            <strong>POR GEOTRACKING S.A.</strong><br/>
                            [NOMBRE_REPRESENTANTE_GEOTRACKING]<br/>
                            [CARGO_REPRESENTANTE_GEOTRACKING]<br/>
                            Cédula: [CEDULA_REPRESENTANTE_GEOTRACKING]
                        </td>
                        <td style="width: 50%; text-align: center; padding: 20px; border-top: 1px solid #333;">
                            <strong>POR ${object.partner_id.name or 'EMPRESA_CLIENTE'}</strong><br/>
                            ${object.legal_representative_name or 'NOMBRE_REPRESENTANTE'}<br/>
                            ${object.legal_position or 'CARGO'}<br/>
                            Cédula: ${object.legal_representative_id or 'CEDULA_REPRESENTANTE'}
                        </td>
                    </tr>
                </table>

                <p style="margin-top: 30px; font-size: 12px; color: #666;">
                    Documento generado automáticamente el ${ctx.get('today', fields.Date.today().strftime('%d/%m/%Y'))}<br/>
                    Geotracking S.A. - Servicios de Rastreo GPS<br/>
                    www.geotracking.cr
                </p>
            </div>
            ''',
            'legal_framework': '''
            <p><strong>MARCO LEGAL APLICABLE:</strong></p>
            <ul>
                <li>Código de Comercio de Costa Rica</li>
                <li>Ley de Protección al Consumidor No. 7472</li>
                <li>Ley de Protección de Datos No. 8968</li>
                <li>Decreto Ejecutivo de Telecomunicaciones</li>
            </ul>
            ''',
            'dispute_resolution': '''
            <p><strong>RESOLUCIÓN DE CONFLICTOS:</strong></p>
            <p>Las partes acuerdan que cualquier controversia derivada de este contrato será resuelta mediante:</p>
            <ol>
                <li>Negociación directa (30 días)</li>
                <li>Mediación en el Centro de Conciliación Nacional</li>
                <li>Arbitraje según el Código Procesal Civil de Costa Rica</li>
            </ol>
            '''
        }

        existing = self.search([('name', '=', default_template['name'])])
        if not existing:
            self.create(default_template)

class ContractTemplatePreview(models.TransientModel):
    _name = 'contract.template.preview'
    _description = 'Vista Previa de Plantilla'

    template_id = fields.Many2one('contract.template', string='Plantilla')
    content = fields.Html(string='Contenido', readonly=True)