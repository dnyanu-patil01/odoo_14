from odoo import fields, api, models


class AccountMove(models.Model):

    _inherit = "account.move"

    checkin_date = fields.Date(compute='_compute_folio_dates', store=True)
    checkout_date = fields.Date(compute='_compute_folio_dates', store=True)

    @api.depends('invoice_line_ids')
    def _compute_folio_dates(self):
        for record in self:
            folio = self.env['hotel.folio'].search([('hotel_invoice_id', '=', record.id)], limit=1)
            record.checkin_date = folio.checkin_date if folio else None
            record.checkout_date = folio.checkout_date if folio else None
