{
    'name': 'Sale Order Stock Reassign',
    'summary': """Permite mover items reservados entre Ordenes de Venta""",
    'description': """""",
    'license': 'LGPL-3',
    'author': 'Newcom LCS',
    'category': 'Sales',
    'depends': ['base',  "stock", 'sale_management'],
    
    'data': [
        "views/wizard_views.xml",
        "views/menu_views.xml",
        "security/ir.model.access.csv",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}



