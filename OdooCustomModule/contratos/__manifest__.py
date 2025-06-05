
__manifest__ = {
    'name': 'Gestión de Contratos Generales - Geotracking SA',
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'summary': 'Módulo completo para gestión de contratos generales con empresas',
    'description': '''
Gestión de Contratos Generales - Geotracking SA
===============================================

Sistema completo de gestión de contratos generales específicamente para empresas
con representantes legales y cumplimiento normativo para Costa Rica.

Características principales:
* Contratos exclusivos para empresas (contactos tipo compañía)
* Gestión completa de representantes legales
* Estados de contrato: Nuevo, En Negociación, Vigente, Renovado, Finiquitado
* Notificaciones automáticas de vencimiento (2 meses y día de vencimiento)
* Renovación automática configurable
* Integración completa con contactos, ventas y contabilidad
* Cumplimiento legal para Costa Rica
* Plantillas personalizables de contratos
* Gestión de valor total del contrato
* Interfaz 100% en español
* Compatible con Odoo 15.0

Funcionalidades empresariales:
* Solo permite contratos con contactos tipo empresa
* Identificación de representantes legales con jerarquía
* Campos legales específicos (cédula jurídica, registro nacional)
* Actualización automática de información de contactos
* Notificaciones por email a responsables
* Estados workflow completo del contrato
* Renovaciones automáticas con histórico

Cumplimiento Costa Rica:
* Código de Comercio costarricense
* Ley de Protección al Consumidor No. 7472
* Ley de Protección de Datos No. 8968
* Plantillas con formato legal apropiado
    ''',
    'author': 'Geotracking SA',
    'website': 'https://www.geotracking.cr',
    'depends': ['base', 'sale', 'account', 'mail', 'portal'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/contract_sequence.xml',
        'data/contract_types.xml',
        'data/contract_templates.xml',
        'data/contract_cron.xml',
        'data/email_templates.xml',
        'views/menu_views.xml',
        'views/contract_type_views.xml',
        'views/contract_views.xml',
        'views/contract_template_views.xml',
        'views/partner_views.xml',
        'wizards/contract_wizard_views.xml',
        'reports/contract_report.xml',
        'reports/contract_template.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
}
