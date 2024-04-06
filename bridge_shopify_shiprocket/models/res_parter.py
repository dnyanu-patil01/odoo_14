from odoo import _, api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    pickup_location_lines = fields.One2many('shiprocket.pickup.location', 'seller_id', string='Pickup Locations')
    automate_shiprocket_process = fields.Boolean("Automate Shiprocket Process")

    @api.onchange('fulfilment_type')
    def _onchange_fulfilment_type(self):
        if self.fulfilment_type == 'self_fulfilment':
            self.automate_shiprocket_process = False

class StockMove(models.Model):
    _inherit = "stock.move"
    
    def _get_new_picking_values(self):
        """We need this method to set Seller Pickup Location in Stock Picking"""
        res = super(StockMove, self)._get_new_picking_values()
        order_id = self.sale_line_id.order_id
        if order_id.seller_id and order_id.seller_id.pickup_location_lines:
            res.update({'pickup_location': order_id.seller_id.pickup_location_lines.ids[0],'automate_shiprocket_process':order_id.seller_id.automate_shiprocket_process})
        return res

class StockPicking(models.Model):
    _inherit = "stock.picking"

    automate_shiprocket_process = fields.Boolean(related="seller_id.automate_shiprocket_process",string="Automate Shiprocket Process",store=True)




