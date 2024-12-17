from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Cuenta Analítica',
        domain="[('partner_id', '=', partner_id)]"
    )

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account(self):
        if self.analytic_account_id:
            for line in self. timesheet_ids:
                line.account_id = self.analytic_account_id
