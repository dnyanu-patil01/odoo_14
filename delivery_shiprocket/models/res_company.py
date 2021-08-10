# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools
import requests
import json
from odoo.exceptions import UserError
from .shiprocket_request import ShipRocket


class ResCompany(models.Model):
    _inherit = "res.company"

    use_shiprocket = fields.Boolean("Use Shiprocket?")
    api_token = fields.Text("API Token")

    def get_auth_api(self):
        
        shiprocket_username = tools.config.get("shiprocket_username_%s"%(self.id)) or False
        shiprocket_password = tools.config.get("shiprocket_password_%s"%(self.id)) or False
        if not shiprocket_username:
            self.write(
                    {
                        "api_token": False
                    }
                )
            return False
        if not shiprocket_password:
            self.write(
                    {
                        "api_token": False
                    }
                )
            return False
        if shiprocket_username and shiprocket_password:
            data = {
                "email": shiprocket_username.strip(),
                "password": shiprocket_password.strip(),
            }
            shiprocket = ShipRocket(self)
            response_dict = shiprocket._authenticate_login(data)
            if response_dict and "token" in response_dict:
                self.write(
                    {'api_token':"Bearer "+ response_dict['token']}
                )
            elif response_dict and "message" in response_dict:
                self.write(
                    {"api_token": False}
                )
            else:
                self.write(
                    {"api_token": False}
                )
        return True

    def get_import_all_channels(self):
        if not self.api_token:
            return
        ShiprocketChannel = self.env["shiprocket.channel"]
        shiprocket = ShipRocket(self)
        response_dict = shiprocket._import_all_channels()
        if response_dict and "data" in response_dict:
            for rec in response_dict.get("data"):
                vals = {
                    "channel_id": rec["id"],
                    "name": rec["name"],
                    "channel_status": rec["status"],
                    "base_channel_code": rec["base_channel_code"],
                    "brand_name": rec["brand_name"],
                }
                channel_exist = ShiprocketChannel.search(
                    [("channel_id", "=", str(rec["id"]))]
                )
                if channel_exist:
                    ShiprocketChannel.write(vals)
                else:
                    ShiprocketChannel.create(vals)
        elif "message" in response_dict:
            raise UserError(response_dict.get("message"))
        elif "errors" in response_dict:
            raise UserError(response_dict.get("errors"))
        else:
            raise UserError(response_dict)
        return True

    def get_import_all_picking_address(self):
        if not self.api_token:
            return
        ShiprocketPickupLocation = self.env["shiprocket.pickup.location"]
        shiprocket = ShipRocket(self)
        response_dict = shiprocket._import_picking_address()
        if response_dict and "data" in response_dict:
            for rec in response_dict.get("data")["shipping_address"]:
                vals = {
                    "pickup_location_id": rec["id"],
                    "pickup_location": rec["pickup_location"],
                    "name": rec["name"],
                    "email": rec["email"],
                    "phone": rec["phone"],
                    "alternate_phone": rec["alternate_phone"],
                    "address": rec["address"],
                    "address2": rec["address_2"],
                    "pin_code": rec["pin_code"],
                    "city": rec["city"],
                }
                country, state = self.get_country_state_id(rec["country"], rec["state"])
                vals.update(
                    {
                        "country_id": country.id,
                        "state_id": state.id,
                    }
                )
                pickup_location_exist = ShiprocketPickupLocation.search(
                    [("pickup_location_id", "=", str(rec["id"]))]
                )
                if pickup_location_exist:
                    ShiprocketPickupLocation.write(vals)
                else:
                    ShiprocketPickupLocation.create(vals)
        elif "message" in response_dict:
            raise UserError(response_dict.get("message"))
        elif "errors" in response_dict:
            raise UserError(response_dict.get("errors"))
        else:
            raise UserError(response_dict)
        return True

    def get_country_state_id(self, country_name, state_name):
        ResCountry = self.env["res.country"]
        ResState = self.env["res.country.state"]
        country = ResCountry.search([("name", "=", country_name)], limit=1)
        if country:
            state = ResState.search(
                [("name", "=", state_name), ("country_id", "=", country.id)], limit=1
            )
        else:
            state = ResState.search([("name", "=", state_name)], limit=1)
        return country, state

    @api.model
    def action_update_auth_token(self):
        """Auto Update Auth Token For All Companies"""
        companies = self.env["res.company"].search(
            [
                ("use_shiprocket", "=", True)
            ]
        )
        for company in companies:
            company.get_auth_api()
        return True
