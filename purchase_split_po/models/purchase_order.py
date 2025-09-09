from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    def action_open_split_wizard(self):
        """
        Open the split wizard for the purchase order
        """
        # Use context to pass the necessary data
        context = {
            'default_purchase_order_id': self.id,
            'default_supplier_id': self.partner_id.id,
            'active_model': 'purchase.order',
            'active_id': self.id,
        }
        
        # Return an action to open the wizard
        return {
            'name': _('Dividir Líneas de Orden de Compra'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order.split.wizard',
            'target': 'new',
            'context': context,
        }
