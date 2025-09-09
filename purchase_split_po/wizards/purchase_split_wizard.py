from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging 

_logger = logging.getLogger(__name__)

class PurchaseSplitWizardLine(models.TransientModel):
    _name = 'purchase.split.wizard.line'
    _description = 'Purchase Split Wizard Line'
    
    wizard_id = fields.Many2one('purchase.order.split.wizard', required=True)
    purchase_line_id = fields.Many2one('purchase.order.line', required=True)
    product_id = fields.Many2one('product.product', related='purchase_line_id.product_id', readonly=True)
    name = fields.Text(related='purchase_line_id.name', readonly=True)
    product_qty = fields.Float(related='purchase_line_id.product_qty', readonly=True)
    selected = fields.Boolean(string='Seleccionar', default=False)

class PurchaseOrderSplitWizard(models.TransientModel):
    _name = 'purchase.order.split.wizard'
    _description = 'Asistente para Dividir Línea de Orden de Compra'

    purchase_order_id = fields.Many2one(
        'purchase.order', 
        string='Orden de Compra Original',
        required=True,
    )
    purchase_line_id = fields.Many2one(
        'purchase.order.line', 
        string='Línea de Orden de Compra',
        required=True,
    )
    product_id = fields.Many2one(
        'product.product', 
        string='Producto',
        required=True,
        readonly=True,
    )
    # Field to show all available lines for selection
    available_line_ids = fields.Many2many(
        'purchase.order.line',
        'purchase_split_wizard_available_line_rel',
        'wizard_id',
        'line_id',
        string='Líneas Disponibles',
        readonly=True
    )
    # Field for user to select lines (One2many approach)
    line_selection_ids = fields.One2many(
        'purchase.split.wizard.line',
        'wizard_id',
        string='Líneas para Seleccionar'
    )
    supplier_id = fields.Many2one(
        'res.partner', 
        string='Proveedor',
        required=True,
    )
    existing_purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Orden de Compra Existente',
        domain="[('state', 'in', ['draft', 'sent']), ('partner_id', '=', supplier_id)]",
        help="Selecciona una orden de compra existente para mover esta línea"
    )
    action_type = fields.Selection([
        ('new', 'Crear Nueva Orden de Compra'),
        ('existing', 'Mover a Orden Existente')
    ], string='Acción', default='new', required=True)
    order_qty = fields.Float(
        string='Cantidad Ordenada',
        required=True,
    )
    expected_date = fields.Datetime(
        string='Fecha Prevista',
        required=True,
    )
    remaining_qty = fields.Float(
        string='Cantidad Restante',
        compute='_compute_remaining_qty',
    )
    total_selected_qty = fields.Float(
        string='Cantidad Total Seleccionada',
        compute='_compute_total_selected_qty',
    )
    # Add a reference field to display the linked sale order
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Orden de Venta Vinculada',
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
        
        # Check if we're coming from a purchase order
        if self._context.get('active_model') == 'purchase.order':
            po_id = self._context.get('active_id')
            if po_id:
                po = self.env['purchase.order'].browse(po_id)
                if po and po.exists():
                    # Get all draft/sent lines from this PO
                    available_lines = po.order_line.filtered(lambda l: l.state in ['draft', 'sent'])
                    if available_lines:
                        first_line = available_lines[0]
                        res.update({
                            'purchase_order_id': po.id,
                            'purchase_line_id': first_line.id,
                            'product_id': first_line.product_id.id,
                            'order_qty': first_line.product_qty,
                            'expected_date': first_line.date_planned,
                            'supplier_id': po.partner_id.id,
                            'available_line_ids': [(6, 0, available_lines.ids)],
                        })
        
        # Check if we're coming from a PO line (single or multiple)
        elif self._context.get('active_model') == 'purchase.order.line':
            active_ids = self._context.get('active_ids', [])
            if not active_ids and self._context.get('active_id'):
                active_ids = [self._context.get('active_id')]
            
            if active_ids:
                lines = self.env['purchase.order.line'].browse(active_ids)
                if lines and lines.exists():
                    # Use the first line for basic info
                    first_line = lines[0]
                    po = first_line.order_id
                    # Get all draft/sent lines from the same PO
                    available_lines = po.order_line.filtered(lambda l: l.state in ['draft', 'sent'])
                    res.update({
                        'purchase_order_id': po.id,
                        'purchase_line_id': first_line.id,
                        'product_id': first_line.product_id.id,
                        'order_qty': first_line.product_qty,
                        'expected_date': first_line.date_planned,
                        'supplier_id': po.partner_id.id,
                        'available_line_ids': [(6, 0, available_lines.ids)],
                        'selected_line_ids': [(6, 0, active_ids)],
                    })
        return res
    
    @api.depends('order_qty', 'purchase_line_id')
    def _compute_remaining_qty(self):
        for wizard in self:
            wizard.remaining_qty = wizard.purchase_line_id.product_qty - wizard.order_qty
    
    @api.depends('line_selection_ids.selected')
    def _compute_total_selected_qty(self):
        for wizard in self:
            selected_lines = wizard.line_selection_ids.filtered('selected')
            wizard.total_selected_qty = sum(line.product_qty for line in selected_lines)
    
    @api.model
    def create(self, vals):
        """Override create to populate wizard lines after wizard creation"""
        wizard = super(PurchaseOrderSplitWizard, self).create(vals)
        
        # Debug logging
        _logger.info(f"Creating wizard with vals: {vals}")
        _logger.info(f"Wizard purchase_order_id: {wizard.purchase_order_id}")
        
        # Get available lines from the purchase order
        if wizard.purchase_order_id:
            available_lines = wizard.purchase_order_id.order_line.filtered(lambda l: l.state in ['draft', 'sent'])
            _logger.info(f"Found {len(available_lines)} available lines")
            
            if available_lines:
                # Create wizard lines for selection
                wizard_lines = []
                for line in available_lines:
                    wizard_lines.append((0, 0, {
                        'purchase_line_id': line.id,
                        'selected': False,
                    }))
                wizard.line_selection_ids = wizard_lines
                _logger.info(f"Created {len(wizard_lines)} wizard lines")
        return wizard
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create_multi to populate wizard lines after wizard creation"""
        wizards = super(PurchaseOrderSplitWizard, self).create(vals_list)
        
        for wizard in wizards:
            # Get available lines from the purchase order
            if wizard.purchase_order_id:
                available_lines = wizard.purchase_order_id.order_line.filtered(lambda l: l.state in ['draft', 'sent'])
                _logger.info(f"Found {len(available_lines)} available lines for wizard {wizard.id}")
                
                if available_lines:
                    # Create wizard lines for selection
                    wizard_lines = []
                    for line in available_lines:
                        wizard_lines.append((0, 0, {
                            'purchase_line_id': line.id,
                            'selected': False,
                        }))
                    wizard.line_selection_ids = wizard_lines
                    _logger.info(f"Created {len(wizard_lines)} wizard lines for wizard {wizard.id}")
        return wizards
    
    @api.onchange('purchase_order_id')
    def _onchange_purchase_order_id(self):
        """Populate wizard lines when purchase order is set"""
        if self.purchase_order_id and not self.line_selection_ids:
            available_lines = self.purchase_order_id.order_line.filtered(lambda l: l.state in ['draft', 'sent'])
            _logger.info(f"Onchange: Found {len(available_lines)} available lines")
            
            if available_lines:
                # Create wizard lines for selection
                wizard_lines = []
                for line in available_lines:
                    wizard_lines.append((0, 0, {
                        'purchase_line_id': line.id,
                        'selected': False,
                    }))
                self.line_selection_ids = wizard_lines
                _logger.info(f"Onchange: Created {len(wizard_lines)} wizard lines")
    
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
    
    @api.onchange('supplier_id')
    def _onchange_supplier_id(self):
        """Update existing PO domain when supplier changes"""
        if self.supplier_id:
            return {
                'domain': {
                    'existing_purchase_order_id': [
                        ('state', 'in', ['draft', 'sent']),
                        ('partner_id', '=', self.supplier_id.id)
                    ]
                }
            }
        return {
            'domain': {
                'existing_purchase_order_id': [('id', '=', False)]
            }
        }
    
    def action_create_new_po(self):                       
        """
        Create a new purchase order with the selected lines and supplier
        """
        self.ensure_one()
        
        # Use selected lines if available, otherwise fall back to single line
        lines_to_move = self.selected_line_ids if self.selected_line_ids else [self.purchase_line_id]
        
        if not lines_to_move:
            raise UserError(_('Debe seleccionar al menos una línea para mover.'))
        
        original_po = self.purchase_order_id

        # Get procurement group if needed for MTO (use first line)
        procurement_group_id = False
        first_line = lines_to_move[0]
        if first_line.move_dest_ids:
            procurement_group_id = first_line.move_dest_ids[0].group_id.id
        elif original_po.group_id:
            procurement_group_id = original_po.group_id.id
            
        # Also get the sale order if directly linked (use first line)
        sale_order_id = False
        if hasattr(first_line, 'sale_line_id') and first_line.sale_line_id and first_line.sale_line_id.order_id:
            sale_order_id = first_line.sale_line_id.order_id.id

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
        
        # Move all selected lines to the new PO
        for line in lines_to_move:
            line.write({
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
    
    def action_move_to_existing_po(self):
        """
        Move the selected purchase order lines to an existing purchase order
        """
        self.ensure_one()
        
        if not self.existing_purchase_order_id:
            raise UserError(_('Debe seleccionar una orden de compra existente.'))
        
        # Use selected lines if available, otherwise fall back to single line
        lines_to_move = self.selected_line_ids if self.selected_line_ids else [self.purchase_line_id]
        
        if not lines_to_move:
            raise UserError(_('Debe seleccionar al menos una línea para mover.'))
        
        target_po = self.existing_purchase_order_id
        
        # Validate that the target PO is compatible
        if target_po.partner_id != self.supplier_id:
            raise UserError(_('El proveedor de la orden de compra seleccionada debe coincidir con el proveedor seleccionado.'))
        
        if target_po.state not in ['draft', 'sent']:
            raise UserError(_('Solo se pueden mover líneas a órdenes de compra en estado Borrador o Enviado.'))
        
        # Move all selected lines to the target PO
        for line in lines_to_move:
            line.write({
                'order_id': target_po.id,
            })
        
        # Return action to open the target purchase order
        return {
            'name': _('Purchase Order'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'res_id': target_po.id,
            'target': 'current',
        }
    
    def action_execute(self):
        """
        Execute the selected action (create new PO or move to existing)
        """
        self.ensure_one()
        
        # Get selected lines from the wizard lines
        selected_lines = self.line_selection_ids.filtered('selected')
        
        # Validate that at least one line is selected
        if not selected_lines:
            raise UserError(_('Debe seleccionar al menos una línea para procesar.'))
        
        # Update selected_line_ids for compatibility with existing methods
        self.selected_line_ids = [(6, 0, selected_lines.mapped('purchase_line_id').ids)]
        
        if self.action_type == 'new':
            return self.action_create_new_po()
        elif self.action_type == 'existing':
            return self.action_move_to_existing_po()
        else:
            raise UserError(_('Tipo de acción no válido.')) 