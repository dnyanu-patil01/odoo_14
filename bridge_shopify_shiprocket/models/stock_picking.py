from odoo import fields, models

class ShiprocketPickupLocation(models.Model):
    _inherit = "shiprocket.pickup.location"

    seller_id = fields.Many2one("res.partner",domain=[('seller','=',True),('parent_id','=',False)])

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    self_tracking_url = fields.Char("Tracking Link",copy=False)

    def update_delivery_carrier(self):
        '''popup wizard to update carrier after done state'''
        picking_ids = False
        if self.env.context.get('active_model') == 'stock.picking':
            picking_ids = self.env.context.get('active_ids') or False
        if not picking_ids:
            ctx={'picking_ids':self.ids}
        else:
            ctx = {"picking_ids": picking_ids}
        return {
            "name": ("Update Delivery Carrier"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "update.delivery.carrier",
            "target": "new",
            "context":ctx,
        }

class ProviderShiprocket(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('self', 'Self Fulfilment')])

    def self_get_tracking_link(self, picking):
        return picking.self_tracking_url