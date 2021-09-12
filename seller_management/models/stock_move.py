from odoo import _, api, fields, models

class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model   
    def _get_seller_domain(self):
        domain=[]
        if self.env.user.has_group('seller_management.group_sellers_management_manager'):
            domain = [('seller','=',True)]
        elif self.env.user.has_group('seller_management.group_sellers_management_user'):
            domain.append(('id','=',self.env.user.partner_id.id))
        return domain

    seller_id = fields.Many2one("res.partner",domain=lambda self:self._get_seller_domain(),index=True, copy=False)
    
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