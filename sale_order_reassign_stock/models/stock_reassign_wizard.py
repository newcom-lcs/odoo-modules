from odoo import models, fields, api, exceptions

class StockReassignWizard(models.TransientModel):
    _name = 'stock.reassign.wizard'
    _description = 'Reasignación de Stock y Ordenes de Compra'

    source_order_id = fields.Many2one('sale.order', string="Orden de Venta Fuente", required=True)
    target_order_id = fields.Many2one('sale.order', string="Orden de Venta Destino", required=True)
    product_id = fields.Many2one('product.product', string="Producto", required=True)
    quantity = fields.Float(string="Cantidad a Reasignar", required=True)

    @api.onchange('source_order_id', 'target_order_id')
    def _onchange_orders(self):
        if self.source_order_id and self.target_order_id:
            # Obtener los productos de ambas órdenes
            source_products = self.source_order_id.order_line.mapped('product_id')
            target_products = self.target_order_id.order_line.mapped('product_id')
            
            # Filtrar productos que estén en ambas órdenes
            common_products = source_products & target_products
            
            # Aplicar el dominio al campo product_id
            return {'domain': {'product_id': [('id', 'in', common_products.ids)]}}
        else:
            # Si no hay órdenes seleccionadas, no aplicar filtro
            return {'domain': {'product_id': []}}

    def action_reassign_stock(self):
        if self.source_order_id and self.target_order_id and self.product_id and self.quantity > 0:
            self.source_order_id.reassign_stock_and_purchase(
                source_order_id=self.source_order_id.id,
                target_order_id=self.target_order_id.id,
                product_id=self.product_id.id,
                quantity=self.quantity
            )
        else:
            raise exceptions.UserError("Por favor, complete todos los campos correctamente.")
