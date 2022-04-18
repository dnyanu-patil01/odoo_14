# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools
import requests
import json
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = "res.company"

    api_token = fields.Text("API Token")

    def get_auth_api(self):
        
        client_id = tools.config.get("client_id_%s"%(self.id)) or False
        client_secret = tools.config.get("client_secret_%s"%(self.id)) or False
        if not client_id:
            self.write(
                    {
                        "api_token": False
                    }
                )
            return False
        if not client_secret:
            self.write(
                    {
                        "api_token": False
                    }
                )
            return False
        if client_secret and client_secret:
            data = {
                "grant_type" : "client_credentials",
                "client_id": client_id.strip(),
                "client_secret": client_secret.strip(),
            }
            url="https://profile.srcm.net/o/token/"
            response = requests.post(url,data=data)
            if response.status_code == 200:
                response_dict = response.json()
                if response_dict and "access_token" in response_dict:
                    self.write(
                        {'api_token':"Bearer "+ response_dict['access_token']}
                    )
                else:
                    self.write(
                        {"api_token": False}
                    )
        return True

    @api.model
    def action_update_auth_token(self):
        """Auto Update Auth Token For All Companies"""
        companies = self.env["res.company"].search([])
        for company in companies:
            company.get_auth_api()
        return True
