{
    'name': 'Inventory Read Only Access',
    'version': '1.0',
    'category': 'Inventory',
    'license': 'LGPL-3',
    'author': 'Newcom LCS',
    'summary': 'Restricts inventory access to read-only except for PEDIDO operations',
    'description': """
        This module creates a new permission group that:
        - Gives read-only access to inventory
        - Allows write access only for operations with sequence_code = 'PEDIDO'
    """,
    'website': 'https://www.yourcompany.com',
    'depends': ['stock'],
    'data': [
        'security/stock_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
} 