from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_view_sales_orders(self):
        self.ensure_one()
        return {
            'name': 'Related Sales Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.order_line.mapped('sale_line_id.order_id').ids)],
            'context': {'create': False, 'edit': False},
        } 