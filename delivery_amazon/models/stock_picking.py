# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
import requests
import json
import phonenumbers
from odoo.exceptions import UserError, AccessError
from werkzeug.urls import url_join
from datetime import datetime
from .amzn_shipment_request import AmznShipment

class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = "id desc"

    package_unit = fields.Selection([('INCH', 'INCH'), ('CENTIMETER', 'CENTIMETER')], default='CENTIMETER', string='Package Unit')
    amz_payment_method = fields.Selection([("Prepaid", "Prepaid"), ("COD", "COD")], default="Prepaid")
    charge_type = fields.Selection([('Tax', 'Tax'), ('Discount', 'Discount')])
    channel_types = fields.Selection([('AMAZON', 'AMAZON'), ('EXTERNAL', 'EXTERNAL')], default='EXTERNAL')
    product_pack = fields.Many2one('product.packaging', string="Package")
    pack_shipping_weight = fields.Float('Package Shipping Weight', compute='compute_package_weight')
    service_matrix_ids = fields.One2many('amazon.shipment.service.list', 'picking_id', string="Amazon Service Matrix")
    service_id = fields.Many2one('amazon.shipment.service.list', domain="[('picking_id', '=', id)]")
    request_token = fields.Char('Request Token')
    tracking_id = fields.Char('Tracking ID')
    shipment_id = fields.Char('Shipment ID')
    is_shipment_purchased = fields.Boolean('Is Shipment Purchased?')
    is_get_rates = fields.Boolean('Is Get Rates?')
    is_documents_generated = fields.Boolean('Is Documents Ready?')
    event_code = fields.Char('Event Code')
    tracking_status = fields.Selection([('PreTransit', 'PreTransit'), ('InTransit', 'InTransit'),
                                        ('Delivered', 'Delivered'), ('Lost', 'Lost'), ('OutForDelivery', 'OutForDelivery'),
                                        ('Rejected', 'Rejected'), ('Undeliverable', 'Undeliverable'),
                                        ('DeliveryAttempted', 'DeliveryAttempted'), ('PickupCancelled', 'PickupCancelled')
                                        ], 'Tracking Status')
    barcode = fields.Binary()
    barcode_file_name = fields.Char('File Name', default="Shipment Document")

    def _convert_phone_number(self, number, country_code):
        """Used to remove country code and format it as 10 digits int as per shiprocket standard
        :param number: phone number string
        :param country_code: Country Code Ex: IN
        :return: 10 digits integer of phone number.
        """
        if not number or not country_code:
            return False
        try:
            phone_nbr = phonenumbers.parse(
                number, region=country_code, keep_raw_input=True
            )
        except phonenumbers.phonenumberutil.NumberParseException:
            return False
        if not phonenumbers.is_possible_number(
            phone_nbr
        ) or not phonenumbers.is_valid_number(phone_nbr):
            return False
        return str(phone_nbr.national_number)
    def _prepare_address(self):
        """prepare dict of address details to pass in _prepare_order function
        :param: stock.picking object
        :return: dict of shipping,billing address fields
        """
        address_val = dict()
        if self.sale_id:
            partner = self.sale_id.partner_invoice_id
            address_val.update(
                {
                    "name": partner.name,
                    "addressLine1": partner.street,
                    "addressLine2": partner.street2,
                    "addressLine3": ' ',
                    "companyName": partner.name,
                    "stateOrRegion": partner.state_id.name,
                    "city": partner.city,
                    "countryCode": partner.country_id.code,
                    "postalCode": partner.zip,
                    "email": partner.email or partner.parent_id.email,
                }
            )
            if partner.phone:
                address_val.update({"phoneNumber": self._convert_phone_number(
                        partner.phone, partner.country_id.code
                    )})
            else:
                address_val.update({"phoneNumber": self._convert_phone_number(
                        partner.parent_id.phone, partner.parent_id.country_id.code
                    )})

        else:
            partner = self.partner_id
            address_val.update(
                {
                    "name": partner.name,
                    "addressLine1": partner.street,
                    "addressLine2": partner.street2,
                    "addressLine3": ' ',
                    "companyName": partner.name,
                    "stateOrRegion": partner.state_id.name,
                    "city": partner.city,
                    "countryCode": partner.country_id.code,
                    "postalCode": partner.zip,
                    "email": partner.email or partner.parent_id.email,
                }
            )
            if partner.phone:
                address_val.update({"phoneNumber": self._convert_phone_number(
                        partner.phone, partner.country_id.code
                    )})
            else:
                address_val.update({"phoneNumber": self._convert_phone_number(
                        partner.parent_id.phone, partner.parent_id.country_id.code
                    )})
        return address_val

    def _get_package_info(self):
        packages = []
        for rec in self.package_ids:
            dimensions = {
                'length': rec.packaging_id.flength,
                'width': rec.packaging_id.fwidth,
                'height': rec.packaging_id.fheight,
                'unit': self.package_unit,
            }
            pack_weight = {
                'value': self.pack_shipping_weight,
                'unit': 'KILOGRAM',
            }
            company = self.env.company
            currency = company.currency_id.name
            insuredValue = {
                "unit": currency,
                "value": self.sale_id.amount_total
            }
            charges_amount = {'value': self.sale_id.amount_tax,
                             'unit': currency}
            charges = [{'amount': charges_amount ,
                        'charge_type': 'TAX'}]

            # To get list of items
            items_list = []
            for sale_order in self.sale_id:
                for line in sale_order.order_line:
                    itemValue = {'value': line.price_total,
                                 'unit': currency}
                    weight = {
                        'value': 0,
                        'unit': 'KILOGRAM',
                    }
                    items = {
                             'itemValue': itemValue,
                             'description': line.product_id.name,
                             'quantity': line.product_uom_qty,
                             'weight': weight,
                             }
                    items_list.append(items)
            packages.append({'dimensions': dimensions,
                             'weight': pack_weight,
                             'charges': charges,
                             'insuredValue': insuredValue,
                             'sellerDisplayName': self.seller_id.name,
                             'items': items_list,
                             'packageClientReferenceId': str(self.id)
                        })
        return packages

    def _prepare_order(self):
        pickup = self.pickup_location
        shipFrom = {
            "name": pickup.name,
            "addressLine1": pickup.address,
            "addressLine2": pickup.address2,
            "addressLine3": pickup.seller_id.name,
            "companyName": pickup.name,
            "stateOrRegion": pickup.state_id.name,
            "city": pickup.city,
            "countryCode": pickup.country_id.code,
            "postalCode": pickup.pin_code,
            "email": pickup.email or pickup.parent_id.email,
            "phoneNumber": self._convert_phone_number(pickup.phone, pickup.country_id.code),
        }
        shipTo = self._prepare_address()
        channelDetails = {'channelType': self.channel_types}
        data = {
            'shipFrom': shipFrom,
            'shipTo': shipTo,
            'returnTo': shipFrom,
            'shipDate': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            'packages': self._get_package_info(),
            'taxDetails': [{"taxType": "GST",
                            "taxRegistrationNumber": self.seller_id.vat}],
            'channelDetails': channelDetails,
        }
        return data

    def amzn_get_rates(self):
        if not self.seller_id:
            raise UserError('Please provide the Seller.')
        amznshipment = AmznShipment(self.env.company)
        # API Call To Get Rates
        data = self._prepare_order()
        response_data = amznshipment._check_rates(data)
        if "payload" in response_data and response_data['payload']['rates']:
            self.request_token = response_data["payload"]['requestToken']
            payload = response_data["payload"]["rates"]
            for rec in payload:
                service = self.env['amazon.service'].create({'name': rec['serviceName'],
                                                             'service_code': rec['serviceId']})
                promise_pickup_date = rec['promise']['pickupWindow']
                promise_delivery_date = rec['promise']['deliveryWindow']
                vals ={'picking_id': self.id,
                       'billed_weight': rec['billedWeight']['value'],
                       'rate_id': rec['rateId'],
                       'carrier_id': rec['carrierId'],
                       'carrier_name': rec['carrierName'],
                       'rate': rec['totalCharge']['value'],
                       'service_id': service.id,
                       'service_code': rec['serviceId'],
                       'est_pickup_startdate': promise_pickup_date['start'],
                       'est_pickup_enddate': promise_pickup_date['end'],
                       'est_delivery_startdate': promise_delivery_date['start'],
                       'est_delivery_enddate': promise_delivery_date['end']
                       }
                self.env['amazon.shipment.service.list'].create(vals)
                self.is_get_rates = True
        elif "payload" in response_data and response_data['payload']['ineligibleRates']:
            no_rates = response_data['payload']['ineligibleRates'][0]['ineligibilityReasons']
            raise UserError(no_rates[0]['message'])
        elif "errors" in response_data:
            raise UserError(response_data['errors'][0]['details'])
        else:
            raise UserError(response_data)
        return True


    def amzn_get_shipment_document(self):
        amznshipment = AmznShipment(self.env.company)
        # API Call To Get Shipment Document
        response_data = amznshipment._get_shipment_document(self)

        if "payload" in response_data:
            content = response_data['payload']['packageDocumentDetail']['packageDocuments'][0]
            self.barcode = content['contents']
            self.is_documents_generated = True
        elif "errors" in response_data:
            raise UserError(response_data['errors'][0]['details'])
        else:
            raise UserError(response_data)
        return True

    def amzn_tracking_shipment(self):
        amznshipment = AmznShipment(self.env.company)
        # API Call To Track Shipment
        response_data = amznshipment._get_tracking_shipment(self)
        if "payload" in response_data:
            payload = response_data["payload"]['eventHistory']
            for rec in payload:
                self.event_code = rec['eventCode']
            self.tracking_status = response_data["payload"]['summary']['status']
        elif "errors" in response_data:
            raise UserError(response_data['errors'][0]['details'])
        elif "message" in response_data:
            raise UserError(response_data['errors'][0]['message'])
        else:
            raise UserError(response_data)
        return True

    def amzn_cancel_shipment(self):
        if self.tracking_status and self.tracking_status != 'PreTransit':
            raise UserError('The shipment has already been picked up, you cannot cancel it.')
        amznshipment = AmznShipment(self.env.company)
        # API Call To Cancel Shipment
        response_data = amznshipment._cancel_shipment(self)
        if "payload" in response_data:
            self.service_matrix_ids.unlink()
            self.write({'service_id': None,
                        'product_pack': None,
                        'request_token': None,
                        'tracking_id': None,
                        'shipment_id': None,
                        'is_shipment_purchased': None,
                        'is_get_rates': None,
                        'is_documents_generated': None,
                        'event_code': None,
                        'tracking_status': None,
                        'barcode': None
                        })
        elif "errors" in response_data:
            raise UserError(response_data['errors'][0]['details'])
        elif "message" in response_data:
            raise UserError(response_data['errors'][0]['message'])
        else:
            raise UserError(response_data)
        return True
