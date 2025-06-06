
# -*- coding: utf-8 -*-
__manifest__ = {
    'name': 'Gestión de Contratos - Geotracking SA',
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'summary': 'Sistema de gestión de contratos empresariales',
    'description': """
Sistema de Gestión de Contratos
================================

Módulo completo para la gestión de contratos empresariales:
* Contratos con estados configurables
* Integración con contactos
* Seguimiento completo
* Campos específicos para Costa Rica
    """,
    'author': 'Geotracking SA',
    'website': 'https://www.geotracking.cr',
    'depends': [
        'base',
        'mail'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/contract_sequence.xml',
        'data/contract_types.xml',
        'views/contract_type_views.xml',
        'views/contract_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
