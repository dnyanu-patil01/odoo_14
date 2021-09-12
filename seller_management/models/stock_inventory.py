from odoo import _, api, fields, models

class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    @api.model   
    def _get_seller_domain(self):
        domain=[]
        if self.env.user.has_group('seller_management.group_sellers_management_manager'):
            domain = [('seller','=',True)]
        elif self.env.user.has_group('seller_management.group_sellers_management_user'):
            domain.append(('id','=',self.env.user.partner_id.id))
        return domain

    seller_id = fields.Many2one("res.partner",domain=lambda self:self._get_seller_domain(),index=True, copy=False)
    
    def _get_filtered_seller_warehouse_record(self):
        action = self.env["ir.actions.actions"]._for_xml_id("seller_management.seller_stock_transfer_action")
        if self.env.user.has_group('seller_management.group_sellers_management_manager'):
            action['domain'] = [('seller_id','!=',False)]
        elif self.env.user.has_group('seller_management.group_sellers_management_user'):
            action['domain'] = [
                ('seller_id', '=', self.env.user.partner_id.id),
                ('seller_id','!=',False)
            ]
        else:
            action['domain'] = [('seller_id','!=',False)]
        action['context'] = {'default_seller_id':self.env.user.partner_id.id}
        return action
