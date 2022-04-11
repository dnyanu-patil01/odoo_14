from odoo import _, api, fields, models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    seller_id = fields.Many2one("res.partner",string="Seller",copy=False,domain="[('seller','=',True),('active','=',True),('parent_id','=',False)]")
    mobile = fields.Char(related="partner_id.mobile",readonly=True) 
    phone = fields.Char(related="partner_id.phone",readonly=True)

    @api.model
    def create(self, vals):
        #To Pass Seller ID While Creating Backorders
        if 'backorder_id' in vals and vals['backorder_id'] != False:
            orgin = self.browse(int(vals['backorder_id']))
            if orgin.seller_id:
                vals.update({'seller_id':orgin.seller_id.id})
        return super(StockPicking ,self).create(vals)