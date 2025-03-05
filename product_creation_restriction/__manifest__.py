{
    'name': 'Product Creation Restriction',
    'version': '16.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Restrict product creation to authorized users only',
    'description': """
        This module restricts the creation of products to users in the Product Creation group.
        Only users with specific permissions will be able to create new products.
        Prevents product creation from Sales Orders and Purchase Orders.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['product', 'sale_management', 'purchase'],
    'data': [
        'security/product_security.xml',
        'security/ir.model.access.csv',
        'views/product_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
} 