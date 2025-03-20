from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging 

_logger = logging.getLogger(__name__)

class PurchaseOrderSplitWizard(models.TransientModel):
    _name = 'purchase.order.split.wizard'
    _description = 'Wizard to Split Purchase Order Line to New PO'

    purchase_order_id = fields.Many2one(
        'purchase.order', 
        string='Original Purchase Order',
        required=True,
    )
    purchase_line_id = fields.Many2one(
        'purchase.order.line', 
        string='Purchase Order Line',
        required=True,
    )
    product_id = fields.Many2one(
        'product.product', 
        string='Product',
        required=True,
        readonly=True,
    )
    supplier_id = fields.Many2one(
        'res.partner', 
        string='Supplier',
        required=True,
    )
    order_qty = fields.Float(
        string='Order Quantity',
        required=True,
    )
    expected_date = fields.Datetime(
        string='Expected Date',
        required=True,
    )
    remaining_qty = fields.Float(
        string='Remaining Quantity',
        compute='_compute_remaining_qty',
    )
    # Add a reference field to display the linked sale order
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Linked Sales Order',
        compute='_compute_sale_order',
        readonly=True,
    )
    
    @api.depends('purchase_line_id')
    def _compute_sale_order(self):
        """
        Compute the linked sales order based on the purchase line's sale_line_id
        """
        for wizard in self:
            wizard.sale_order_id = False
            if wizard.purchase_line_id and wizard.purchase_line_id.sale_line_id:
                wizard.sale_order_id = wizard.purchase_line_id.sale_line_id.order_id
    
    @api.model
    def default_get(self, fields_list):
        """
        Override default_get to automatically set field values
        """
        res = super(PurchaseOrderSplitWizard, self).default_get(fields_list)
        
        # Check if we're coming from a PO line
        if self._context.get('active_model') == 'purchase.order.line' and self._context.get('active_id'):
            line = self.env['purchase.order.line'].browse(self._context.get('active_id'))
            if line and line.exists():
                res.update({
                    'purchase_order_id': line.order_id.id,
                    'purchase_line_id': line.id,
                    'product_id': line.product_id.id,
                    'order_qty': line.product_qty,
                    'expected_date': line.date_planned,
                    'supplier_id': line.order_id.partner_id.id,  # Set default supplier from original PO
                })
        return res
    
    @api.depends('order_qty', 'purchase_line_id')
    def _compute_remaining_qty(self):
        for wizard in self:
            wizard.remaining_qty = wizard.purchase_line_id.product_qty - wizard.order_qty
    
    @api.onchange('purchase_line_id')
    def _onchange_purchase_line_id(self):
        if self.purchase_line_id:
            self.product_id = self.purchase_line_id.product_id
            self.order_qty = self.purchase_line_id.product_qty
            self.expected_date = self.purchase_line_id.date_planned
            # Set the original supplier as default
            if self.purchase_order_id and self.purchase_order_id.partner_id:
                self.supplier_id = self.purchase_order_id.partner_id.id
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            # Get suppliers for this product
            suppliers = self.env['product.supplierinfo'].search([
                '|',
                ('product_id', '=', self.product_id.id),
                ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
            ]).mapped('partner_id')
            
            # No domain restrictions - allow searching all contacts
            return {}
    
    def action_create_new_po(self):                       
        """
        Create a new purchase order with the selected line and supplier
        """
        self.ensure_one()
        
        purchase_line = self.purchase_line_id
        original_po = self.purchase_order_id


               
        # Get procurement group if needed for MTO
        procurement_group_id = False
        if purchase_line.move_dest_ids:
            procurement_group_id = purchase_line.move_dest_ids[0].group_id.id
        elif original_po.group_id:
            procurement_group_id = original_po.group_id.id
            
        # Also get the sale order if directly linked
        sale_order_id = False
        if hasattr(purchase_line, 'sale_line_id') and purchase_line.sale_line_id and purchase_line.sale_line_id.order_id:
            sale_order_id = purchase_line.sale_line_id.order_id.id

        if not sale_order_id:
            sale_order_id = original_po.origin
        
        
        # Create a new purchase order - set origin to prioritize sales order
        new_po_vals = {
            'partner_id': self.supplier_id.id,
            'user_id': original_po.user_id.id,
            'currency_id': original_po.currency_id.id,
            'date_order': fields.Datetime.now(),
            'company_id': original_po.company_id.id,
            'fiscal_position_id': original_po.fiscal_position_id.id,
            'group_id': procurement_group_id,
            'state': 'draft',
            'origin': sale_order_id,
        }
       
        new_po = self.env['purchase.order'].create(new_po_vals)
        purchase_line.write({
                'order_id': new_po.id,
        })        
        
        
        # Return action to open the new purchase order
        return {
            'name': _('New Purchase Order'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'res_id': new_po.id,
            'target': 'current',
        } 