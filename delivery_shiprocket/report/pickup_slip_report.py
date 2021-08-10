# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from itertools import groupby


class PickupSummaryReport(models.AbstractModel):
    _name = "report.delivery_shiprocket.report_pickup_slip"
    _description = "Pickup Slip Report"

    def _get_product_lines(self, obj):
        stock_move_lines = self.env["stock.move.line"].search(
            [("picking_id", "in", obj.stock_picking_ids.ids)]
        )
        product_ids = stock_move_lines.mapped("product_id")
        lines = []
        for product in product_ids:
            qty = sum(
                stock_move_lines.filtered(
                    lambda move: move.product_id == product
                ).mapped("qty_done")
            )
            lines.append(
                {
                    "product": product.name,
                    "internal_reference": product.default_code,
                    "qty": qty,
                }
            )
        return lines

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["shiprocket.bulk.process"].browse(docids)
        return {
            "doc_ids": docids,
            "doc_model": "shiprocket.bulk.process",
            "docs": docs,
            "report_type": data.get("report_type") if data else "",
            "product_lines": self._get_product_lines(docs),
        }
