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
    
    @api.model
    def create(self, vals):
        if 'note' in vals:
            product_id = vals['product_id'] if 'product_id' in vals else self.product_id.id
            product = self.env['product.product'].browse(product_id)
            body='%s'%(vals['note'])
            product.message_post(body=body)
        return super(StockQuant,self).create(vals)
    
    def write(self, vals):
        body = None
        if 'inventory_quantity' in vals:
            product_id = vals['product_id'] if 'product_id' in vals else self.product_id.id
            product = self.env['product.product'].browse(product_id)
            body = 'On Hand Quantity Updated From %s to %s'%(str(self.inventory_quantity),str(vals['inventory_quantity']))
        if 'note' in vals:
            body+='<br/> %s'%(vals['note'])
        if body:
            product.message_post(body=body)
        return super(StockQuant,self).write(vals)

class ProductChangeQuantity(models.TransientModel):
    _inherit = "stock.change.product.qty"

    note = fields.Text(string='Note')

    def change_product_qty(self):
        """ Changes the Product Quantity by creating/editing corresponding quant.
        """
        super().change_product_qty()
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id)], limit=1
        )
        shopify_product_tmpl_id = self.env['shopify.product.template.ept'].search([('product_tmpl_id','=',self.product_id.product_tmpl_id.id)])
        if shopify_product_tmpl_id:
            import_product_obj = self.env['shopify.process.import.export'].create({})
            import_product_obj.with_context({'active_ids':shopify_product_tmpl_id.ids}).sudo().shopify_selective_product_stock_export()
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': self.product_id.id,
            'location_id': warehouse.lot_stock_id.id,
            'inventory_quantity': self.new_quantity,
            'note':self.note,
        })
        return {'type': 'ir.actions.act_window_close'}

class Product(models.Model):
    _name='product.product'
    _inherit = ['product.product','mail.thread']