{
    'name': 'Fecha Prevista Stock',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Propagate schedule date to next picking',
    'description': """
        This module ensures that when a stock picking is validated,
        its schedule_date is copied to the immediate next picking in the chain.
    """,
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
} 