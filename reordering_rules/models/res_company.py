from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    enable_auto_reordering_rules = fields.Boolean(
        string='Enable Automatic Reordering Rules',
        default=False,
        help='When enabled, new storable and consumable products will automatically '
             'get MTS+MTO route and reordering rules configured.'
    ) 