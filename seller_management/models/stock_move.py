from odoo import _, api, fields, models

class StockMove(models.Model):
    _inherit = "stock.move"

    seller_id = fields.Many2one("res.partner",index=True, copy=False,domain="[('seller','=',True),('active','=',True),('parent_id','=',False)]")
    
    def _get_new_picking_values(self):
        """We need this method to set Seller in Stock Picking"""
        res = super(StockMove, self)._get_new_picking_values()
        order_id = self.sale_line_id.order_id
        if order_id.seller_id:
            res.update({'seller_id': order_id.seller_id.id})
        return res

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        """We need this method to set Seller in Stock Move"""
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['seller_id']
        return fields