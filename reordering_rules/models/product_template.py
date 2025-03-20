from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model_create_multi
    def create(self, vals_list):
        products = super().create(vals_list)
        products._set_default_properties()
        return products

    def write(self, vals):
        res = super().write(vals)
        self._set_default_properties()
        return res

    def _set_default_properties(self):
        """Configure default properties for products including MTS+MTO route and reordering rules."""
        if not self._should_process_products():
            return

        combined_route = self._get_combined_route()
        example_vendor = self._get_example_vendor()

        if not (combined_route and example_vendor):
            return

        products_to_process = self.filtered(lambda p: p.type in ['product', 'consu'])
        for product in products_to_process:
            self._configure_product(product, combined_route, example_vendor)

    def _should_process_products(self):
        """Check if products should be processed based on type and configuration."""
        if self.filtered(lambda p: p.type == 'service'):
            _logger.info("Skipping service products for MTS+MTO configuration")
            return False
        return True

    def _get_combined_route(self):
        """Get the MTS+MTO combined route."""
        combined_route = self.env.ref('stock_mts_mto_rule.route_mto_mts', raise_if_not_found=False)
        if not combined_route:
            _logger.warning("MTS+MTO route not found. Make sure stock_mts_mto_rule module is installed.")
        return combined_route

    def _get_example_vendor(self):
        """Get the example vendor for reordering rules."""
        example_vendor = self.env.ref('reordering_rules.partner_example_vendor', raise_if_not_found=False)
        if not example_vendor:
            _logger.warning("Example vendor not found. Make sure the data file is properly loaded.")
        return example_vendor

    def _get_company_warehouse(self, company):
        """Get the warehouse for a specific company."""
        warehouse = self.env['stock.warehouse'].search([
            ('company_id', '=', company.id)
        ], limit=1)
        
        if not warehouse:
            _logger.error(f"No warehouse found for company {company.name}")
            return False

        if not warehouse.lot_stock_id:
            _logger.error(f"No stock location found for warehouse {warehouse.name} in company {company.name}")
            return False
            
        return warehouse

    def _create_or_get_supplier_info(self, product, example_vendor, company):
        """Create or get supplier info for a product."""
        try:
            # First ensure the vendor exists and is properly configured
            if not example_vendor.supplier_rank:
                example_vendor.write({'supplier_rank': 1})

            # Search for existing supplier info
            supplier_info = self.env['product.supplierinfo'].search([
                ('product_tmpl_id', '=', product.id),
                ('partner_id', '=', example_vendor.id),
                ('company_id', '=', company.id),
            ], limit=1)
            
            if not supplier_info:
                _logger.info(f"Creating supplier info for product {product.name}")
                supplier_info = self.env['product.supplierinfo'].create({
                    'partner_id': example_vendor.id,
                    'product_tmpl_id': product.id,
                    'price': 0.0,
                    'delay': 1,
                    'min_qty': 1,
                    'company_id': company.id,
                })

                # Explicitly link the supplier to the product
                product.write({
                    'seller_ids': [(4, supplier_info.id, 0)]
                })

            return supplier_info

        except Exception as e:
            _logger.error(f"Failed to create/get supplier info for product {product.name}: {str(e)}")
            return False

    def _create_orderpoint(self, product, warehouse, supplier_info):
        """Create orderpoint for a product if it doesn't exist."""
        if not product.product_variant_id:
            _logger.warning(f"No product variant found for product {product.name}")
            return

        if product.product_variant_id.orderpoint_ids:
            _logger.info(f"Orderpoint already exists for product {product.name}")
            return

        try:
            orderpoint_vals = {
                'product_id': product.product_variant_id.id,
                'location_id': warehouse.lot_stock_id.id,
                'warehouse_id': warehouse.id,
                'route_id': self._get_combined_route().id,
                'company_id': warehouse.company_id.id,
            }

            if 'supplier_id' in self.env['stock.warehouse.orderpoint']._fields and supplier_info:
                orderpoint_vals['supplier_id'] = supplier_info.id

            self.env['stock.warehouse.orderpoint'].with_company(warehouse.company_id.id).create(orderpoint_vals)
            _logger.info(f"Created orderpoint for product {product.name}")

        except Exception as e:
            _logger.error(f"Failed to create orderpoint for product {product.name}: {str(e)}")

    def _configure_product(self, product, combined_route, example_vendor):
        """Configure a single product with routes and reordering rules."""
        try:
            company = product.company_id or self.env.company
            
            if not company.enable_auto_reordering_rules:
                _logger.info(f"Automatic reordering rules are disabled for company {company.name}")
                return

            warehouse = self._get_company_warehouse(company)
            if not warehouse:
                return

            # Set list_price to 0
            product.list_price = 0.0
            _logger.info(f"Set list_price to 0 for product {product.name}")

            # Create or get supplier info and ensure it's linked
            supplier_info = self._create_or_get_supplier_info(product, example_vendor, company)
            if not supplier_info:
                return

            # Apply the combined MTO + MTS route
            if combined_route and combined_route not in product.route_ids:
                product.route_ids = [(4, combined_route.id)]

            # Create orderpoint
            self._create_orderpoint(product, warehouse, supplier_info)

        except Exception as e:
            _logger.error(f"Failed to process product {product.name}: {str(e)}")
