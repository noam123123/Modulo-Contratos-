
{
    'name': 'Contratos Base - Versión Estable',
    'version': '15.0.1.0.0',
    'summary': 'Gestión básica de contratos - Versión mínima estable',
    'description': '''
        Módulo base para gestión de contratos.
        Versión mínima y estable que se puede expandir gradualmente.

        Características:
        - Contratos básicos
        - Estados simples
        - Sin dependencias complejas
    ''',
    'author': 'Geotracking SA',
    'website': 'https://geotracking.cr',
    'category': 'Sales',
    'depends': ['base', 'mail'],  # Solo dependencias básicas
    'data': [
        'security/ir.model.access.csv',
        'views/contract_views.xml',
        'views/menu_views.xml',
        'data/contract_sequence.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
