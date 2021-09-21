from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    seller_id = fields.Many2one('res.partner','Seller', index=True, copy=False)
    seller_shopify_sequence = fields.Char(readonly=True)

    @api.model
    def create(self, vals):
        if 'seller_id' in vals and vals['seller_id'] != False:
            seller_obj = self.env['res.partner'].browse(vals['seller_id'])
            if seller_obj.seller_sale_sequence_id:
                vals['name'] = seller_obj.seller_sale_sequence_id._next()
        return super(SaleOrder, self).create(vals)
        
    def _prepare_invoice(self):
        """This method used set seller info in customer invoice.
        """
        invoice_val = super(SaleOrder, self)._prepare_invoice()
        if self.seller_id:
            invoice_val.update({'seller_id': self.seller_id.id})
        if self.seller_id.seller_invoice_sequence_id:
            invoice_val.update({'name':self.seller_id.seller_invoice_sequence_id._next()})
        return invoice_val

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    seller_id = fields.Many2one('res.partner','Seller', index=True, copy=False)

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id and self.product_id.seller_id:
            self.seller_id = self.product_id.seller_id.id
        return res

    #To Pass Seller To Stock Move
    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        if self.order_id.seller_id:
            res.update({'seller_id':self.order_id.seller_id.id})
        return res
