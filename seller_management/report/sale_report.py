# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models
import odoo


class SaleReport(models.Model):
    _inherit = "sale.report"

    seller_id = fields.Many2one("res.partner", "Seller", copy=False, readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        """ Inherit the query here to add the seller_id in group by.
        """
        fields['seller_id'] = ", s.seller_id as seller_id"
        groupby += ', s.seller_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)

    def seller_sale_report(self):
        action = self.env.ref('seller_management.seller_action_order_report_all').read()[0]
        return action
