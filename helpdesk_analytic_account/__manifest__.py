# -*- coding: utf-8 -*-
{
    'name': 'Help Desk Update Analytic Account to Timesheets',
    'license': 'LGPL-3',
    'version': '16.0.2',
    'category': 'Stock',
    'depends': ['timesheet_grid', 'helpdesk', 'helpdesk_timesheet' ],
    'data':[ 
        'views/helpdesk_ticket_views.xml',
     ],
    'auto_install': False,
    'installable' : True,
    'application' : False,
}