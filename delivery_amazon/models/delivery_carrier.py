# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from odoo.exceptions import UserError, AccessError
from .amzn_shipment_request import AmznShipment

class ShipmentMethodInherit(models.Model):
    _name = "delivery.carrier"
    _inherit = ['mail.thread', 'delivery.carrier']

    delivery_type = fields.Selection(selection_add=[('amazon_shipment', 'Amazon Delivery')],
                                     ondelete={'amazon_shipment': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})

    def amazon_shipment_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            picking.amzn_get_rates()
            amznshipment = AmznShipment(self.env.company)
            # API Call To Get Purchase Shipment
            data = {
                "requestToken": picking.request_token,
                "rateId": picking.service_id.rate_id,
                "requestedDocumentSpecification": {
                    "format": "PDF",
                    "size": {
                        "width": 4,
                        "length": 6,
                        "unit": "INCH"
                    },
                    "dpi": 300,
                    "pageLayout": "DEFAULT",
                    # "needFileJoining": false,
                    "requestedDocumentTypes": [
                        "LABEL"
                    ]
                }
            }
            response_data = amznshipment._get_purchase_shipment(data)
            if response_data:
                response_data.update(
                    {
                        "exact_price": 0,
                        "tracking_number": "",
                    }
                )
                res.append(response_data)
            else:
                response_data.update(
                    {
                        "exact_price": 0,
                        "tracking_number": "",
                    }
                )
            if "payload" in response_data:
                payload = response_data["payload"]['packageDocumentDetails']
                for rec in payload:
                    picking.tracking_id = rec['trackingId']
                picking.shipment_id = response_data["payload"]['shipmentId']
                picking.is_shipment_purchased = True
            elif "errors" in response_data:
                raise UserError(response_data['errors'][0]['details'])
            else:
                raise UserError(response_data)
        return res