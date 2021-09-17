from odoo import api, fields, models, _

class SellerGroup(models.Model):
    _name = 'seller.group'
    _description = 'Seller Group To Generate Single Transfer'

    name = fields.Char(required=True)
    seller_ids = fields.Many2many('res.partner',string="Sellers",domain="[('seller','=',True),('parent_id','=',False)]")

    @api.model
    def create(self,vals):
        res = super(SellerGroup,self).create(vals)
        res.write_group_id()
        return res

    def write(self,vals):
        if 'seller_ids' in vals:
            self.seller_ids.write({'seller_group_id':False})
        res = super(SellerGroup,self).write(vals)
        self.write_group_id()
        return res

    def write_group_id(self):
        return self.seller_ids.write({'seller_group_id':self.id})

class ResPartner(models.Model):
    _inherit = "res.partner"

    seller_group_id = fields.Many2one("seller.group")


