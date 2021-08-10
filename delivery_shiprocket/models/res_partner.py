# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from .shiprocket_request import ShipRocket


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_shiprocket_pickup_location = fields.Boolean()
    pickup_location_id = fields.Char()
    pickup_location_name = fields.Char("Pickup Location Name", size=8)

    # To Create Shiprocket Pickup Location
    def add_pickup_location(self):
        if not self.pickup_location_name:
            raise UserError("Pickup Location Name Is Required")
        shiprocket = ShipRocket(self.env.company)
        check_value = shiprocket.check_required_address_value(self)
        if check_value:
            raise UserError(check_value)
        response = shiprocket.create_new_pickup_location(self)
        response_dict = response.json()
        if response.status_code == 200:
            self.write({'pickup_location_id':response_dict['pickup_id']})
            title="Success"
            message_id = self.env['message.box'].create({'message': '<b>Pickup Location Successfully Created In Shiprocket</b>'})
        else:
            title=response_dict['message']
            message_id = self.env['message.box'].create({'message': '<b>'+str(response_dict['errors'])+'</b>'})
        return {
            "name": title,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "message.box",
            "res_id": message_id.id,
            "target": "new",
        }
