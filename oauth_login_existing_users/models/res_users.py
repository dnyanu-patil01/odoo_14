# -*- coding: utf-8 -*-

import logging

from odoo import models, api

logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        # data sent is {'@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#users/$entity', 'businessPhones': [], 'displayName': 'Hardik Shah', 'givenName': 'Hardik', 'jobTitle': 'Software Architect', 'mail': 'hshah@cantaloupe.com', 'mobilePhone': None, 'officeLocation': 'Consultant', 'preferredLanguage': None, 'surname': 'Shah', 'userPrincipalName': 'hshah@cantaloupe.com', 'id': '61ebb23a-416c-43c3-a790-b498f6b49598', 'user_id': '61ebb23a-416c-43c3-a790-b498f6b49598'}
        user_email = validation['email']
        oauth_uid = validation['user_id']
        print(validation)
        if user_email and oauth_uid:
            user = self.search([("login", "=", user_email)])
            if user:
                user.write({'oauth_uid': oauth_uid, 'oauth_provider_id': provider})
        return super(ResUsers, self)._auth_oauth_signin(provider, validation, params)
