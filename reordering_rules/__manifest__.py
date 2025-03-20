{
    'name': 'Reglas de Reabastecimiento Automático MTO+MTS',
    'version': '1.0',
    'summary': 'Configura automáticamente rutas MTO+MTS y reglas de reabastecimiento para productos',
    'description': """
Este módulo configura automáticamente las rutas MTO+MTS y crea reglas de reabastecimiento 
para productos almacenables y consumibles.

Características:
• Aplica automáticamente la ruta combinada MTO+MTS a nuevos productos
• Crea reglas de reabastecimiento automáticamente
• Compatible con múltiples compañías
• Excluye productos de tipo servicio
• Maneja múltiples almacenes por compañía

Requisitos:
• Módulo de Inventario (stock)
• Módulo de Rutas MTO+MTS (stock_mts_mto_rule)
• Módulo de Compras (purchase)
    """,
    'author': 'Newcom LCS',
    'website': 'https://www.newcom-lcs.com',
    'license': 'LGPL-3',
    'depends': [
        'stock',
        'stock_mts_mto_rule',
        'purchase'
    ],
    'data': [
        'views/res_company_views.xml',
        'data/res_partner_data.xml',
    ],
    'installable': True,
    'application': False,
    'category': 'Inventory/Inventory',
}
