from odoo import fields, models, api,_
# from odoo.exceptions import UserError, ValidationError


class WorkProfile(models.Model):
    _name = "work.profile"
    _description = "Work Profile"

    name = fields.Char('Name', index=True, required=True)
    active = fields.Boolean('Active', default=True)
    