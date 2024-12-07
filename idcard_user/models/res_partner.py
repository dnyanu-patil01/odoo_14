##############################################################################
# models/res_partner.py
##############################################################################
from odoo import models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_print_id_card(self):
        # Logic for printing ID card, e.g., generating a PDF or sending to a printer
        return self.env.ref('id_card_printer.report_id_card').report_action(self)
