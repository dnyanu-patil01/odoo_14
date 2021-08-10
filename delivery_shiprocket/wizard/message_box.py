from odoo import api, fields, models, _


class MessageBox(models.TransientModel):
    _name = "message.box"

    message = fields.Html("Message", readonly=True)

    def action_ok(self):
        """ close wizard"""
        return {"type": "ir.actions.act_window_close"}
