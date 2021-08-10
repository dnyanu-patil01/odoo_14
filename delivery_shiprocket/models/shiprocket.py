# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ShiprocketChannel(models.Model):
    _name = "shiprocket.channel"
    _description = "Sales Channel For Shiprocket"

    channel_id = fields.Char("Channel ID")
    name = fields.Char("Channel Name")
    channel_status = fields.Char("Channel Status")
    base_channel_code = fields.Char("Base Channel Code")
    brand_name = fields.Char("Brand Name")
    active = fields.Boolean("Active", default=True)


class ShiprocketPickupLocation(models.Model):
    _name = "shiprocket.pickup.location"
    _description = "Shiprocket Pickup Location"
    _rec_name = "pickup_location"

    pickup_location_id = fields.Char(required=True)
    name = fields.Char("Shipper Name", required=True)
    pickup_location = fields.Char("Pickup Location", size=8)
    email = fields.Char(required=True)
    phone = fields.Char(required=True)
    alternate_phone = fields.Char()
    address = fields.Char("Street", required=True, size=80)
    address2 = fields.Char("Street2")
    city = fields.Char(required=True)
    state_id = fields.Many2one("res.country.state", required=False)
    country_id = fields.Many2one("res.country", required=True)
    pin_code = fields.Char("Pincode", required=True)
    active = fields.Boolean("Active", default=True)


class ShiprocketCourier(models.Model):
    _name = "shiprocket.courier"
    _description = "Shiprocket Courier"

    name = fields.Char("Name")
    code = fields.Char("Code")
    is_international = fields.Boolean()
    is_return = fields.Boolean()


class ShiprocketOrderStatus(models.Model):
    _name = "shiprocket.order.status"
    _description = "Shiprocket Order Status"

    name = fields.Char("Name")
    status_code = fields.Char("Code")
    active = fields.Boolean("Active", default=True)
    is_call_status_cron = fields.Boolean("Call Cron Status")



class ShiprocketServiceabilityMatrix(models.Model):
    _name = "shiprocket.serviceability.matrix"
    _description = (
        "Shiprocket Serviceability Matrix To Show Available Courier Companies"
    )
    _rec_name = "courier_company_id"

    courier_company_id = fields.Many2one("shiprocket.courier")
    courier_name = fields.Char()
    rate = fields.Float("Cost")
    rating = fields.Float("Rating")
    estimated_delivery_days = fields.Char()
    etd_hours = fields.Char()
    etd = fields.Char()
    picking_id = fields.Many2one("stock.picking")
