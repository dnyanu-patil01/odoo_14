# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
import requests
import json
from odoo.exceptions import UserError
from .amzn_shipment_request import AmznShipment


class ResCompany(models.Model):
    _inherit = "res.company"

    use_amazon = fields.Boolean("Use Amazon?")
    amzn_access_token = fields.Text("Amazon Access Token")

    def get_amzn_access_token_api(self):
        client_id = tools.config.get("client_id") or False
        client_secret = tools.config.get("client_secret") or False
        refresh_token = tools.config.get("refresh_token") or False
        if not client_id or not client_secret or not refresh_token:
            self.write(
                {
                    "amzn_access_token": False
                }
            )
            return False
        if client_id and client_secret and refresh_token:
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": 'refresh_token',
                "refresh_token": refresh_token
            }
            amznship = AmznShipment(self)
            response_dict = amznship._generate_access_token(data)
            if response_dict and "access_token" in response_dict:
                self.write(
                    {'amzn_access_token': response_dict['access_token']}
                )
            elif response_dict and "error" in response_dict:
                self.write(
                    {"amzn_access_token": False}
                )
            else:
                self.write(
                    {"amzn_access_token": False}
                )
        return True

    @api.model
    def action_update_access_token(self):
        """Auto Update Access Token For All Companies"""
        companies = self.env["res.company"].search(
            [
                ("use_amazon", "=", True)
            ]
        )
        for company in companies:
            company.get_amzn_access_token_api()
        return True
