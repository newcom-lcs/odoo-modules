{
    'name': 'Sales Order Purchase View',
    'version': '16.0.1.0.0',
    'category': 'Sales',
    'summary': 'Allow purchase team to view sales orders without price information',
    'description': """
        This module allows purchase team members to view sales orders
        while hiding sensitive price information. The view is read-only
        and excludes all price-related fields.
    """,
    'author': 'Newcom',
    'website': 'https://www.newcom.com',
    'depends': ['sale_management', 'purchase'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
