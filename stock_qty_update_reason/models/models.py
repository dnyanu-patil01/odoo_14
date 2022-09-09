from odoo import api, models, fields,_

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    note = fields.Text()

    @api.model
    def _get_inventory_fields_create(self):
        """ Returns a list of fields user can edit when he want to create a quant in `inventory_mode`.
        """
        res = super()._get_inventory_fields_create()
        res += ['note']
        return res
    
    @api.model
    def _get_inventory_fields_write(self):
        """ Returns a list of fields user can edit when he want to edit a quant in `inventory_mode`.
        """
        res = super()._get_inventory_fields_write()
        res += ['note']
        return res
    
    @api.onchange('inventory_quantity')
    def _onchange_inventory_quantity(self):
        if self.inventory_quantity:
            self.note = False
        return super(StockQuant,self)._onchange_inventory_quantity()

class ProductChangeQuantity(models.TransientModel):
    _inherit = "stock.change.product.qty"

    note = fields.Text(string='Note')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.env.user.has_group('seller_management.group_sellers_management_manager'):
            self.new_quantity = self.product_id.qty_available
        else:
            shopify_tmpl_id = self.env['shopify.product.template.ept'].sudo().search([('product_tmpl_id','=',self.product_id.product_tmpl_id.id)])
            shopify_stock_location = shopify_tmpl_id.shopify_instance_id.shopify_warehouse_id.lot_stock_id
            location_qty = self.env['stock.quant'].search([('location_id','=',shopify_stock_location.id),('product_id','=',self.product_id.id)]).quantity
            self.new_quantity = location_qty

    def change_product_qty(self):
        """ Changes the Product Quantity by creating/editing corresponding quant.
        """
        super().change_product_qty()
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id)], limit=1
        )
        shopify_tmpl_id = self.env['shopify.product.template.ept'].sudo().search([('product_tmpl_id','=',self.product_id.product_tmpl_id.id)])
        shopify_warehouse = shopify_tmpl_id.shopify_instance_id.shopify_warehouse_id
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': self.product_id.id,
            'location_id': shopify_warehouse.lot_stock_id.id if shopify_tmpl_id else warehouse.lot_stock_id.id,
            'inventory_quantity': self.new_quantity,
            'note':self.note,
        })
        return {'type': 'ir.actions.act_window_close'}

class Product(models.Model):
    _name='product.product'
    _inherit = ['product.product','mail.thread']


    def prepare_free_qty_query(self, location_ids, simple_product_list_ids):
        """
        This method prepares query for fetching the free qty.
        @param location_ids:Ids of Locations.
        @param simple_product_list_ids: Ids of products which are not BoM.
        @return: Prepared query in string.
        @author: Maulik Barad on Date 21-Oct-2020.
        @inherited: To Get On Hand Qunatity
        """
        query = """select pp.id as product_id,
                COALESCE(sum(sq.quantity),0) as stock
                from product_product pp
                left join stock_quant sq on pp.id = sq.product_id and sq.location_id in (%s)
                where pp.id in (%s) group by pp.id;""" % (location_ids, simple_product_list_ids)
        return query