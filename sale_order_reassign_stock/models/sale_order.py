from odoo import models, api, exceptions
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def reassign_stock_and_purchase(self, source_order_id, target_order_id, product_id, quantity):
        # Obtener las órdenes de venta
        source_order = self.env['sale.order'].browse(source_order_id)
        target_order = self.env['sale.order'].browse(target_order_id)
        product = self.env['product.product'].browse(product_id)

        if not source_order or not target_order:
            raise exceptions.UserError("No se encontraron las órdenes de venta especificadas.")
        if not product:
            raise exceptions.UserError("Producto no válido.")

        # Verificar stock reservado en la orden fuente
        source_moves = self.env['stock.move'].search([
            ('origin', '=', source_order.name),
            ('product_id', '=', product.id),
            ('state', '=', 'assigned')  # Solo movimientos reservados
        ])

        target_moves = self.env['stock.move'].search([
            ('origin', '=', target_order.name),
            ('product_id', '=', product.id),
            ('state', '=', 'waiting')  
        ])
        
        reserved_qty = sum(move.reserved_availability for move in source_moves)
        forecasted_qty = sum(move.forecast_availability for move in target_moves)

        _logger.info(f"cantidad reservada en orden de origen {reserved_qty}..")
        _logger.info(f"cantidad esperando recepción en orden de destino {forecasted_qty}..")
        
        # if forecasted_qty < quantity:
        #     raise exceptions.UserError(f"no se pueden transferir más de {forecasted_qty} {product.name} a la orden  {target_order.name}.")
        
        if reserved_qty < quantity:
            raise exceptions.UserError(f"No hay suficiente stock reservado en la orden {source_order.name}.")


        # Paso 1: Reducir la cantidad reservada de productos en la orden de venta A
        cantidades_en_a = {}
        qty_to_release = quantity
        for line in source_order.order_line.filtered(lambda l: l.product_id.id == product_id):
            if qty_to_release <= 0:
                break
            cantidades_en_a[line.id] = line.product_uom_qty
            release_qty = min(line.product_uom_qty, qty_to_release)
            line.product_uom_qty = line.product_uom_qty - release_qty
            qty_to_release -= release_qty
            moves = line.move_ids.filtered(lambda m: m.state == 'assigned')
                

        # Paso 2: Cancelar el delivery order de la orden de venta B
        delivery_orders = target_order.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
        for picking in delivery_orders:
            picking_lines = picking.move_ids_without_package.filtered(lambda m: m.product_id.id == product_id)
            if picking_lines:
                picking.action_cancel()
        

        # Paso 3: Actualizo la cantidad en la orden b para que se vuelva a generar el delivery
        cantidades_en_b = {}
        target_order.write({'state': 'draft'})
        
        for line in target_order.order_line.filtered(lambda l: l.product_id.id == product_id):
            product_uom_qty = line.product_uom_qty

        target_order.action_confirm()


        # # Paso 4: Restaurar las cantidades originales en la orden de venta A
        source_order.write({'state': 'draft'})
        for line in source_order.order_line.filtered(lambda l: l.product_id.id == product_id):
            line.product_uom_qty = cantidades_en_a[line.id]
        source_order.action_confirm()

        return True

      
