
# -*- coding: utf-8 -*-
__manifest__ = {
    'name': 'Gestión de Contratos - Geotracking SA',
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'summary': 'Sistema de gestión de contratos empresariales',
    'description': """
Sistema de Gestión de Contratos Generales
==========================================

Módulo completo para la gestión de contratos empresariales:
* Gestión de contratos generales
* Estados configurables del contrato
* Integración con contactos empresariales
* Seguimiento completo de actividades
* Configuración para Costa Rica
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
        'views/contract_type_views.xml',
        'data/contract_types.xml',
        'views/contract_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
