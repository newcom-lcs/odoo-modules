{
    'name': "Dividir Órdenes de Compra",
    'summary': """
        Dividir Órdenes de Compra y crear nuevas o mover líneas a órdenes existentes
    """,
    'description': """
        Este módulo permite a los usuarios crear una nueva Orden de Compra (OC) a partir de 
        una línea dentro de una OC existente, o mover líneas a órdenes de compra existentes. 
        Incluye un asistente para seleccionar un proveedor y asegura una gestión adecuada 
        del inventario mientras mantiene el vínculo con la Orden de Venta (OV) original.
    """,
    'author': 'Newcom LCS',
    'website': 'https://www.newcom-lcs.com',
    'license': 'LGPL-3',
    'website': "",
    'category': 'Inventory/Purchase',
    'version': '1.1',
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