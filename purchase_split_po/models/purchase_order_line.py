from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    def action_open_split_wizard(self):
        """
        Open the split wizard for the selected purchase order line
        """
        self.ensure_one()
        
        # Instead of directly creating a wizard, we'll use context
        # to pass the necessary data
        context = {
            'default_purchase_order_id': self.order_id.id,
            'default_purchase_line_id': self.id,
            'default_product_id': self.product_id.id,
            'default_order_qty': self.product_qty,
            'default_expected_date': self.date_planned,
            'default_supplier_id': self.order_id.partner_id.id,
        }
        
        # Return an action to open the wizard
        return {
            'name': _('Dividir Línea de Orden de Compra'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order.split.wizard',
            'target': 'new',
            'context': context,
        }
    
    # def _prepare_stock_moves(self, picking):
    #     """
    #     Override to ensure sale_line_id is properly transferred to stock moves
    #     during purchase order confirmation.
    #     """
    #     # Get the result from the standard method
    #     res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        
    #     # For each move values dictionary, ensure sale_line_id is included
    #     for move_vals in res:
    #         if self.sale_line_id:
    #             move_vals['sale_line_id'] = self.sale_line_id.id
    #             _logger.info(f"Added sale_line_id {self.sale_line_id.id} to stock move values")
                
    #     return res

    # def _create_or_update_picking(self):
    #     """
    #     Override to ensure the sale_line_id reference is preserved
    #     in the stock moves after creation or updates.
    #     """
    #     result = super(PurchaseOrderLine, self)._create_or_update_picking()
        
    #     # Ensure all moves created for this purchase line have the sale_line_id set
    #     if self.sale_line_id:
    #         _logger.info(f"PO Line {self.id} has sale_line_id {self.sale_line_id.id}")
    #         moves = self.env['stock.move'].search([
    #             ('purchase_line_id', '=', self.id),
    #             ('state', 'not in', ['done', 'cancel'])
    #         ])
    #         if moves:
    #             _logger.info(f"Updating sale_line_id on {len(moves)} moves for PO Line {self.id}")
    #             moves.write({'sale_line_id': self.sale_line_id.id})
                
    #             # Also update the procurement group's name to include the SO
    #             for move in moves:
    #                 if move.group_id and self.sale_line_id.order_id:
    #                     so_name = self.sale_line_id.order_id.name
    #                     if so_name and so_name not in (move.group_id.name or ''):
    #                         new_name = f"{so_name}"
    #                         if move.group_id.name:
    #                             new_name = f"{so_name}, {move.group_id.name}"
    #                         _logger.info(f"Updating procurement group name from '{move.group_id.name}' to '{new_name}'")
    #                         move.group_id.name = new_name
        
    #     return result 