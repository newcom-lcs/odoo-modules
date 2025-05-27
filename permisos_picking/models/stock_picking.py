from odoo import models, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _create_backorder(self):
        """Inherit the backorder creation to copy scheduled_date to the next picking"""
        backorders = super()._create_backorder()
        if backorders and self.scheduled_date:
            # Copy scheduled_date to the immediate next picking
            backorders.write({'scheduled_date': self.scheduled_date})
        return backorders

    def button_validate(self):
        """Inherit the validate button to ensure scheduled_date is copied to next picking"""
        # Get the next picking before validation
        next_pickings = self.move_ids.mapped('move_dest_ids.picking_id')
        
        # Call the original method
        result = super().button_validate()
        
        # After validation, if we have a scheduled_date and next pickings, copy it
        if self.scheduled_date and next_pickings:
            next_pickings.write({'scheduled_date': self.scheduled_date})
            
        return result 