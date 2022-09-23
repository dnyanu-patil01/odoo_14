# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# NOTE Use black to automatically format this code.

from odoo import api, fields, models, _


class Coupon(models.Model):
    _inherit = "coupon.coupon"

    source_pos_order_id = fields.Many2one(
        "pos.order",
        string="PoS Order Reference",
        help="PoS order where this coupon is generated.",
    )
    pos_order_id = fields.Many2one(
        "pos.order",
        string="Applied on PoS Order",
        help="PoS order where this coupon is consumed/booked.",
    )

    def _check_coupon_code(self, order_date, partner_id, **kwargs):
        if self.program_id.id in kwargs.get("reserved_program_ids", []):
            return {
                "error": _("A coupon from the same program has already been reserved for this order.")
            }
        return super()._check_coupon_code(order_date, partner_id, **kwargs)

    def _get_default_template(self):
        if self.source_pos_order_id:
            return self.env.ref('pos_coupon.mail_coupon_template', False)
        return super()._get_default_template()

    @api.model
    def _generate_code(self):
        """
        Modify the generated barcode to be compatible with the default
        barcode rule in this module. See `data/default_barcode_patterns.xml`.
        """
        code = super()._generate_code()
        return '043' + code[3:]
    
    def _check_coupon_code(self, order_date, partner_id, **kwargs):
        """ Check the validity of this single coupon.
            :param order_date Date:
            :param partner_id int | boolean:
        """
        self.ensure_one()
        message = {}
        if self.state == 'used':
            message = {'error': _('This coupon has already been used (%s).') % (self.code)}
        elif self.state == 'reserved':
            message = {'error': _('This coupon %s exists but the origin sales order is not validated yet.') % (self.code)}
        elif self.state == 'cancel':
            message = {'error': _('This coupon has been cancelled (%s).') % (self.code)}
        elif self.state == 'expired' or (self.expiration_date and self.expiration_date < order_date):
            message = {'error': _('This coupon is expired (%s).') % (self.code)}
        elif not self.program_id.active:
            message = {'error': _('The coupon program for %s is in draft or closed state') % (self.code)}
        elif self.partner_id and self.partner_id.id != partner_id:
            message = {'error': _('Invalid partner.')}
        return message
