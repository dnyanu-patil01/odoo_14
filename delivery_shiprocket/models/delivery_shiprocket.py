# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from .shiprocket_request import ShipRocket


class ProviderShiprocket(models.Model):
    _inherit = "delivery.carrier"

    def _get_default_channel_id(self):
        custom_channel =  self.env['shiprocket.channel'].search(
            [('base_channel_code', '=', 'CS')],limit=1)
        if custom_channel:
            return custom_channel.id
        else:
            return False

    delivery_type = fields.Selection([('fixed', 'Fixed Price'),("shiprocket", "Shiprocket")],
    ondelete={'shiprocket': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})},required=False)
    shiprocket_channel_id = fields.Many2one("shiprocket.channel", string="Channel",default=_get_default_channel_id)
    shiprocket_payment_mode = fields.Selection(
        [("cod", "COD"), ("pre", "Prepaid")], string="Payment Mode" ,default="pre",ondelete='set null'
    )


    def _compute_can_generate_return(self):
        super(ProviderShiprocket, self)._compute_can_generate_return()
        for carrier in self:
            if carrier.delivery_type == "shiprocket":
                carrier.can_generate_return = True

    def shiprocket_rate_shipment(self, order):
        return {
            "success": True,
            "price": 0.0,
            "error_message": False,
            "warning_message": False,
        }

    # Create Order/Return Order In ShipRocket
    def shiprocket_send_shipping(self, pickings):
        res = []
        shiprocket = ShipRocket(self.env.company)
        # API Call To Create Order Request
        for picking in pickings:
            response_data = shiprocket.create_channel_specific_order(picking)
            if response_data:
                picking.write(response_data)
                response_data.update(
                    {
                        "exact_price": 0,
                        "tracking_number": "",
                    }
                )
                res.append(response_data)
        return res

    def shiprocket_return_order_creation(self, pickings):
        res = []
        shiprocket = ShipRocket(self.env.company)
        # API Call To Create Return Order Request
        for picking in pickings:
            response_data = shiprocket.create_return_order(picking)
            if response_data:
                picking.write(response_data)
                response_data.update(
                    {
                        "exact_price": 0,
                        "tracking_number": "",
                    }
                )
                res.append(response_data)
        return res

    def shiprocket_get_tracking_link(self, picking):
        shiprocket = ShipRocket(self.env.company)
        return "https://app.shiprocket.co//tracking/%s" % picking.carrier_tracking_ref
