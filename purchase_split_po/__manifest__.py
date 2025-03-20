{
    'name': "Purchase Split PO",
    'summary': """
        Split Purchase Orders and create new ones from existing lines
    """,
    'description': """
        This module allows users to create a new Purchase Order (PO) from 
        a line inside an existing PO. It includes a wizard to select a supplier 
        and ensures proper stock management while maintaining the link to the 
        original Sales Order (SO).
    """,
    'author': 'Newcom LCS',
    'website': 'https://www.newcom-lcs.com',
    'license': 'LGPL-3',
    'website': "",
    'category': 'Inventory/Purchase',
    'version': '1.0',
    'depends': ['purchase_stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/purchase_split_wizard_views.xml',
        'views/purchase_order_line_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
} 