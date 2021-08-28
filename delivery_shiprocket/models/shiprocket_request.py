# -*- coding: utf-8 -*-
import requests
import json
import phonenumbers
from odoo.exceptions import UserError
from werkzeug.urls import url_join

API_BASE_URL = "https://apiv2.shiprocket.in/v1/external/"


class ShipRocket:
    """
    Class used to handle all the shiprocket API Request and Response
    """

    def __init__(self, company):
        """Initialize header for all API request.
        :param company: An res.comapny record
        :return: headers dict with parameters values
        """
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": company.api_token,
        }

    def _authenticate_login(self, data):
        """Request to get authentication token.
        :param data: Dict of email and password of API user
        :return: authentication response dict
        """
        auth_token_url = "auth/login"
        url = url_join(API_BASE_URL, auth_token_url)
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_dict = response.json()
        return response_dict

    def _import_all_channels(self):
        """Request to pull channels from shiprocket to Odoo.
        :return: response dict of get channel api call
        """
        channel_url = "channels"
        url = url_join(API_BASE_URL, channel_url)
        response = requests.get(url, headers=self.headers, data={})
        response_dict = response.json()
        return response_dict

    def _import_picking_address(self):
        """Request to pull pickup address from shiprocket to Odoo.
        :return: response dict contains parameters need to create pickup address
        in odoo or error message.
        """
        get_pickup_address_url = "settings/company/pickup"
        url = url_join(API_BASE_URL, get_pickup_address_url)
        response = requests.get(url, headers=self.headers, data={})
        response_dict = response.json()
        return response_dict

    def check_required_address_value(self, pickup_location):
        """Check the required fields need to create pickup location in shiprocket and check phone number format.
        :param pickup_location: shiprocket.pickup.location record
        :return: True
        """
        required_fields = [
            "pickup_location_id",
            "pickup_location",
            "name",
            "email",
            "phone",
            "address",
            "address2",
            "city",
            "pin_code",
            "state_id",
            "country_id",
        ]
        if pickup_location:
            res = [field for field in required_fields if not pickup_location[field]]
            if res:
                raise UserError(
                    "The Pickup/Seller Address Fields is missing or wrong (Missing field(s) :  \n %s)"
                    % ", ".join(res).replace("_id", "")
                )
            if not self._convert_phone_number(
                pickup_location.phone, pickup_location.country_id.code
            ):
                raise UserError("Pickup/Seller Phone number is invalid.")
        return True

    def check_required_value(
        self, recipient=False, shipper=False, order=False, picking=False
    ):
        """Check the required fields need to create values for shipping and billing address.
        :param recipient: res.partner record(Billing Address Of Partner)
        :param shipper  : res.partner record(Delivery Address Of Partner)
        :param order    : sale.order record
        :picking        : stock.picking record
        :return: True
        """
        recipient_required_fields = [
            "name",
            "email",
            "phone",
            "street",
            "city",
            "zip",
            "state_id",
            "country_id",
        ]
        shipper_required_fields = recipient_required_fields.extend(["street2"])
        if recipient:
            res = [field for field in recipient_required_fields if not recipient[field]]
            if res:
                # Checking if it has parent and parent contains all fields
                if recipient.parent_id:
                    parent_res = [field for field in recipient_required_fields if not recipient.parent_id[field]]
                    if parent_res:
                        raise UserError(
                            "The Customer/Partner Address Fields is missing or wrong (Missing field(s) :  \n %s)"
                            % ", ".join(res).replace("_id", "")
                        )
                else:
                    raise UserError(
                            "The Customer/Partner Address Fields is missing or wrong (Missing field(s) :  \n %s)"
                            % ", ".join(res).replace("_id", "")
                        )
            #Trying To Get phone number from receipt if not trying to get it from parent
            if not self._convert_phone_number(
                recipient.phone, recipient.country_id.code
            ):
                if not recipient.parent_id:
                    raise UserError("Phone number is invalid.")
                else:
                    if recipient.parent_id.phone and recipient.parent_id.country_id:
                        if not self._convert_phone_number(recipient.parent_id.phone, recipient.parent_id.country_id.code):
                            raise UserError("Phone number is invalid.")
                    else:
                        raise UserError("Phone number is invalid.")
        if shipper:
            res = [field for field in shipper_required_fields if not shipper[field]]
            if res:
                raise UserError(
                    "The fields required to create pickup location in shiprocket is missing or wrong (Missing field(s) :  \n %s)"
                    % ", ".join(res).replace("_id", "")
                )
            if not self._convert_phone_number(shipper.phone, shipper.country_id.code):
                raise UserError("Phone number is invalid.")
        # check required value for order
        if order:
            if not order.order_line:
                raise UserError("Please provide at least one item to ship.")
            for line in order.order_line.filtered(
                lambda line: not line.product_id.weight
                and not line.is_delivery
                and line.product_id.type not in ["service", "digital"]
                and not line.display_type
            ):
                raise UserError(
                    "The estimated price cannot be computed because the weight of your product is missing."
                )

        # check required value for picking
        if picking:
            if not picking.move_lines:
                raise UserError("Please provide at least one item to ship.")
            if picking.move_lines.filtered(lambda line: not line.weight):
                raise UserError(
                    "The estimated price cannot be computed because the weight of your product is missing."
                )
        return True

    def create_new_pickup_location(self, partner):
        """Request To Create New Pickup Location In Shiprocket.
        :partner: res.partner object
        :return: response dict from create new pickup location request
        """
        data = self.prepare_pickup_location(partner)
        add_pickup_url = "settings/company/addpickup"
        url = url_join(API_BASE_URL, add_pickup_url)
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        return response.json()

    def prepare_pickup_location(self, partner):
        """Request To Create New Pickup Location In Shiprocket.
        :param partner: res.partner object
        :return:  dict to pass in create_new_pickup_location request.
        """
        self.check_required_value(
            recipient=False, shipper=partner, order=False, picking=False
        )
        return {
            "pickup_location": partner.pickup_location_name,
            "name": partner.name,
            "email": partner.email,
            "phone": self.format_phone_number(partner.phone),
            "address": partner.street,
            "address_2": "" or partner.street2,
            "city": partner.city,
            "state": partner.state_id.name,
            "country": partner.country_id.name,
            "pin_code": int(partner.zip),
        }

    def prepare_order_data(self, picking, mode):
        """Returns Order Creation Specific Fields.
        :param picking: stock.picking object
        :para mode: 'forward' for normal order
                    'return' to create return order in shiprocket
        :return: dict to pass in order creation request.
        """
        data = {
            "order_id": str(picking.name).replace("/", ""),
            "order_date": picking.scheduled_date.strftime("%Y-%m-%d %H:%M"),
            "channel_id": int(picking.channel_id.channel_id),
            "order_items": self.prepare_order_items(picking),
            "sub_total": picking.sale_id.amount_total,
            "payment_method": picking.payment_method,
        }
        dimension_values = self._prepare_parcel(picking)
        data.update(dimension_values)
        if mode == "forward":
            address_val = self._prepare_address(picking)
            data.update(address_val)
            data.update(
                {
                    "pickup_location": picking.pickup_location.pickup_location,
                    "comment": picking.comment,
                    "order_type": picking.order_type,
                    "shipping_charges": picking.shipping_charges,
                    "giftwrap_charges": picking.giftwrap_charges,
                    "transaction_charges": picking.transaction_charges,
                }
            )
            return data
        if mode == "return":
            return_address_vals = self._prepare_return_address(picking)
            data.update(return_address_vals)
            return data

    def create_return_order(self, picking):
        """Create Return Order In Shiprocket
        :param picking: stock.picking object
        """
        if not picking.pickup_location:
            raise UserError("Please Select Shiprocket Pickup Location Before Validate.")
        if not picking.channel_id:
            raise UserError("Please Select Shiprocket Channel Before Validate.")
        data = self.prepare_order_data(picking, "return")
        return_order_url = "orders/create/return"
        url = url_join(API_BASE_URL, return_order_url)
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        response_dict = response.json()
        if "errors" in response_dict:
            raise UserError(self.format_error_message(response_dict["errors"]))
        if "message" in response_dict:
            raise UserError(response_dict["message"])
        if response.status_code == 200:
            response_data = {
                "shiprocket_order_id": response_dict["order_id"],
                "shiprocket_shipping_id": response_dict["shipment_id"],
            }
            return response_data
        return False

    def create_channel_specific_order(self, picking):
        """Create Order In Shiprocket
        :param picking: stock.picking object
        """
        if not picking.pickup_location:
            raise UserError("Please Select Shiprocket Pickup Location Before Validate.")
        if not picking.channel_id:
            raise UserError("Please Select Shiprocket Channel Before Validate.")
        data = self.prepare_order_data(picking, "forward")
        payload = json.dumps(data)
        order_creation_url = "orders/create/adhoc"
        url = url_join(API_BASE_URL, order_creation_url)
        response = requests.post(url, headers=self.headers, data=payload)
        response_dict = response.json()
        if "errors" in response_dict:
            raise UserError(self.format_error_message(response_dict["errors"]))
        if "message" in response_dict:
            raise UserError(response_dict["message"])
        if response.status_code == 200:
            response_data = {
                "shiprocket_order_id": response_dict["order_id"],
                "shiprocket_shipping_id": response_dict["shipment_id"],
            }
            return response_data
        return False

    def get_tracking_link(self, picking):
        """To get tracking link from shiprocket
        :param picking: stock.picking object
        """
        tracking_url = "courier/track/awb/"
        url = url_join(API_BASE_URL, tracking_url)
        request_tracking_url = url_join(url, str(picking.shiprocket_shipping_id))
        payload = {}
        response = requests.get(
             request_tracking_url, headers=self.headers, data=payload
        )
        response_dict = response.json()
        if (
            "track_url" in response_dict["tracking_data"]
            and response.status_code == 200
        ):
            return {
                "carrier_tracking_ref": response_dict["tracking_data"][
                    "shipment_track"
                ][0]["awb_code"],
                "carrier_tracking_url": response_dict["tracking_data"]["track_url"],
            }
        return False

    def prepare_order_items(self, picking):
        """Prepare Order Line Items Need For Order Creation Request
        :param picking: stock.picking object
        :return: order items dict
        """
        order_items = []
        for line in picking.move_lines:
            order_line_vals = {
                "name": line.product_id.name,
                "sku": line.product_id.default_code,
                "units": line.quantity_done,
                "selling_price": line.product_id.list_price,
                "discount": "",
                "hsn": line.product_id.l10n_in_hsn_code or "",
                "tax": "",
            }
            order_items.append(order_line_vals)
        return order_items

    def _prepare_parcel(self, picking):
        """Prepare data related to package dimensions
        :param picking: stock.picking object
        :return: dict
        """
        if not picking.package_ids:
            raise UserError("No Package Details Found")
        package_count = len(picking.package_ids)
        if package_count != 1:
            raise UserError("Error Package Count Need To Be One Per Shiprocket Order")

        packaging = picking.package_ids[:1].packaging_id
        # compute move line weight in package
        move_lines = picking.move_line_ids.filtered(
            lambda ml: ml.result_package_id == packaging
        )
        if picking.is_return_picking:
            weight = sum(
                [
                    ml.product_id.weight
                    * ml.product_uom_id._compute_quantity(
                        ml.product_qty, ml.product_id.uom_id, rounding_method="HALF-UP"
                    )
                    for ml in move_lines
                ]
            )
        else:
            weight = picking.shipping_weight
        return {
            "height": packaging.height,
            "breadth": packaging.width,
            "length": packaging.packaging_length,
            "weight": weight,
        }

    def _prepare_return_address(self, picking):
        """prepare dict of return address details
        :param: stock.picking object
        :return: dict of shipping,pickup address fields
        """
        address_val = dict()
        pickup = picking.pickup_location
        self.check_required_address_value(pickup)
        address_val.update(
            {
                "shipping_customer_name": pickup.name,
                "shipping_address": pickup.address,
                "shipping_address_2": pickup.address2,
                "shipping_city": pickup.city,
                "shipping_pincode": pickup.pin_code,
                "shipping_country": pickup.country_id.name,
                "shipping_state": pickup.state_id.name,
                "shipping_email": pickup.email,
                "shipping_phone": self._convert_phone_number(
                    pickup.phone, pickup.country_id.code
                ),
            }
        )
        partner = picking.partner_id
        self.check_required_value(
            recipient=partner, shipper=False, order=False, picking=False
        )
        address_val.update(
            {
                "pickup_location_id": picking.pickup_location.pickup_location_id,
                "pickup_customer_name": partner.name,
                "pickup_address": partner.street,
                "pickup_address_2": partner.street2,
                "pickup_city": partner.city,
                "pickup_pincode": partner.zip,
                "pickup_country": partner.country_id.name,
                "pickup_state": partner.state_id.name,
                "pickup_email": partner.email or partner.parent_id.email,
            }
        )
        if partner.phone:
            address_val.update({"pickup_phone": self._convert_phone_number(
                    partner.phone, partner.country_id.code
                ),})
        else:
            address_val.update({"pickup_phone": self._convert_phone_number(
                    partner.parent_id.phone, partner.parent_id.country_id.code
                ),})
        return address_val

    def _prepare_address(self, picking):
        """prepare dict of address details to pass in order creation request
        :param: stock.picking object
        :return: dict of shipping,billing address fields
        """
        address_val = dict()
        if not picking.sale_id:
            partner = picking.sale_id.partner_invoice_id
            self.check_required_value(
                recipient=partner, shipper=False, order=False, picking=False
            )
            address_val.update(
                {
                    "billing_customer_name": partner.name,
                    "billing_last_name": "",
                    "billing_address": partner.street,
                    "billing_address_2": partner.street2,
                    "billing_city": partner.city,
                    "billing_pincode": partner.zip,
                    "billing_state": partner.state_id.name,
                    "billing_country": partner.country_id.name,
                    "billing_email": partner.email or partner.parent_id.email,
                    "shipping_is_billing": True,
                }
            )
            if partner.phone:
                address_val.update({"billing_phone": self._convert_phone_number(
                        partner.phone, partner.country_id.code
                    )})
            else:
                address_val.update({"billing_phone": self._convert_phone_number(
                        partner.parent_id.phone, partner.parent_id.country_id.code
                    )})
        if picking.sale_id.partner_invoice_id:
            partner = picking.sale_id.partner_invoice_id
            self.check_required_value(
                recipient=partner, shipper=False, order=False, picking=False
            )
            address_val.update(
                {
                    "billing_customer_name": partner.name,
                    "billing_last_name": "",
                    "billing_address": partner.street,
                    "billing_address_2": partner.street2,
                    "billing_city": partner.city,
                    "billing_pincode": partner.zip,
                    "billing_state": partner.state_id.name,
                    "billing_country": partner.country_id.name,
                    "billing_email": partner.email or partner.parent_id.email,
                }
            )
            if partner.phone:
                address_val.update({"billing_phone": self._convert_phone_number(
                        partner.phone, partner.country_id.code
                    )})
            else:
                address_val.update({"billing_phone": self._convert_phone_number(
                        partner.parent_id.phone, partner.parent_id.country_id.code
                    )})
        if (
            picking.sale_id.partner_invoice_id.id
            == picking.sale_id.partner_shipping_id.id
        ):
            address_val.update({"shipping_is_billing": True})
        else:
            partner = picking.sale_id.partner_shipping_id
            self.check_required_value(
                recipient=partner, shipper=False, order=False, picking=False
            )
            address_val.update(
                {
                    "shipping_is_billing": False,
                    "shipping_customer_name": partner.name,
                    "shipping_address": partner.street,
                    "shipping_address_2": partner.street2,
                    "shipping_city": partner.city,
                    "shipping_pincode": partner.zip,
                    "shipping_country": partner.country_id.name,
                    "shipping_state": partner.state_id.name,
                    "shipping_email": partner.email or partner.parent_id.email,
                }
            )
            if partner.phone:
                address_val.update({"shipping_phone": self._convert_phone_number(
                        partner.phone, partner.country_id.code
                    )})
            else:
                address_val.update({"shipping_phone": self._convert_phone_number(
                        partner.parent_id.phone, partner.parent_id.country_id.code
                    )})
        return address_val

    def format_error_message(self, errors):
        """Helps to format error dict to user format.
        :param errors: error dictionary from request calls
        :return: formatted message string
        """
        message_format = """"""
        for error, message in errors.items():
            msg_format = "%s : %s \n" % (error, message[-1])
            message_format = msg_format
        return message_format

    def _convert_phone_number(self, number, country_code):
        """Used to remove country code and format it as 10 digits int as per shiprocket standard
        :param number: phone number string
        :param country_code: Country Code Ex: IN
        :return: 10 digits integer of phone number.
        """
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
        return int(phone_nbr.national_number)

    def _check_courier_serviceability(self, picking):
        """To check the courier serviceability still available
        before the generation of manifest in bulk generation of manifest
        :param picking: stock.picking objects
        :return: Bool
        """
        data = {
            "pickup_postcode": int(picking.pickup_location.pin_code),
            "delivery_postcode": int(picking.partner_id.zip),
            "order_id": int(picking.shiprocket_order_id),
        }
        if picking.is_return_picking:
            data.update({"is_return": 1})
        check_serviceability_url = "courier/serviceability/"
        url = url_join(API_BASE_URL, check_serviceability_url)
        response = requests.get(url, headers=self.headers, data=json.dumps(data))
        response_dict = response.json()
        is_serviceable = False
        if response.status_code == 200 and "data" in response_dict:
            available_courier = [
                True
                for elem in response_dict["data"]["available_courier_companies"]
                if int(picking.courier_id.id) in elem.values()
            ]
            if any(available_courier):
                is_serviceable = True
            else:
                is_serviceable = False
        else:
            is_serviceable = False
        return is_serviceable

    def _get_courier_serviceability(self, data, picking):
        """To Get Available Courier Services For The Particular Request.
        :param data:dict contains order_id,pickup_postcode,devilery_postcode 
        and reassign passed only incase of reassigning of courier partner
        :param picking:stock.picking object
        :return: reponse_dict
        """
        if picking.is_return_picking:
            data.update({"is_return": 1})
        check_serviceability_url = "courier/serviceability/"
        url = url_join(API_BASE_URL, check_serviceability_url)
        response = requests.get(url, headers=self.headers, data=json.dumps(data))
        response_dict = response.json()
        if response.status_code == 200 and "data" in response_dict:
            courier_list = []
            for rec in response_dict["data"]["available_courier_companies"]:
                courier_data = (
                    0,
                    0,
                    {
                        "courier_company_id": picking.get_courier_id(
                            rec["courier_company_id"], rec["courier_name"]
                        ),
                        "courier_name": rec["courier_company_id"],
                        "rate": rec["rate"],
                        "rating": rec["rating"],
                        "etd_hours": rec["etd_hours"],
                        "etd": rec["etd"],
                        "estimated_delivery_days": rec["estimated_delivery_days"],
                        "picking_id": picking.id,
                    },
                )
                courier_list.append(courier_data)
            response_data = {
                "recommended_courier_company_id": picking.get_courier_id(
                    response_dict["data"]["recommended_courier_company_id"], False
                ),
                "shiprocket_recommended_courier_id": picking.get_courier_id(
                    response_dict["data"]["shiprocket_recommended_courier_id"], False
                ),
                "shiprocket_serviceability_matrix": courier_list,
            }
            return response_data
        else:
            if "errors" in response_dict:
                return {
                    "response_comment": self.format_error_message(
                        response_dict["errors"]
                    )
                }
            if "message" in response_dict:
                return {"response_comment": response_dict["message"]}
        return False

    def _create_awb(self, data, picking):
        """Request To Create AWB for current order.
        :param data: Dict of courier_id and shipment_id
        :param picking:stock.picking object
        :return: response dict
        """
        create_awb_url = "courier/assign/awb"
        url = url_join(API_BASE_URL, create_awb_url)
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        response_dict = response.json()
        if "errors" in response_dict:
            return {
                "response_comment": self.format_error_message(response_dict["errors"])
            }
        if "message" in response_dict:
            return {"response_comment": response_dict["message"]}
        else:
            if response.status_code == 200:
                response_data = {
                    "shiprocket_awb_code": response_dict["response"]["data"]["awb_code"]
                }
                return response_data
        return False

    def _generate_pickup_request(self, shipping_id):
        """To Create Pickup Request For AWB Generated Records
        :param shipping_id: list of shipping ids
        :retun : response dict
        """
        generate_pickup_url = "courier/generate/pickup"
        url = url_join(API_BASE_URL, generate_pickup_url)
        payload = {"shipment_id": shipping_id}
        response = requests.post(url, headers=self.headers, data=json.dumps(payload))
        response_dict = response.json()
        if "errors" in response_dict:
            return {
                "response_comment": self.format_error_message(response_dict["errors"])
            }
        if "message" in response_dict:
            return {"response_comment": response_dict["message"]}
        if response.status_code == 200 and "response" in response_dict:
            note = "%s" % (
                response_dict["response"]["data"],
            )
            return {"pickup_request_note": note}
        return False

    def _generate_manifest_request(self, shipping_id):
        """To Create Manifest For Pickup Request Generated Records
        :param shipping_id: list of shipping ids
        :retun : response dict
        """
        generate_manifest_url = "manifests/generate"
        url = url_join(API_BASE_URL, generate_manifest_url)
        payload = {"shipment_id": shipping_id}
        response = requests.post(url, headers=self.headers, data=json.dumps(payload))
        response_dict = response.json()
        if "errors" in response_dict:
            return {
                "response_comment": self.format_error_message(response_dict["errors"])
            }
        if "message" in response_dict:
            return {"response_comment": response_dict["message"]}
        if response.status_code == 200 and "manifest_url" in response_dict:
            return {"manifest_url": response_dict["manifest_url"],"is_manifest_generated":True}
        return False

    def _generate_label_request(self, shipping_id):
        """To Generate Label For AWB Generated Records
        :param shipping_id: list of shipping ids
        :retun : response dict
        """
        generate_label_url = "courier/generate/label"
        url = url_join(API_BASE_URL, generate_label_url)
        payload = {"shipment_id": shipping_id}
        response = requests.post(url, headers=self.headers, data=json.dumps(payload))
        response_dict = response.json()
        if "not_created" in response_dict and response_dict['not_created'] != []:
            return {
                "response_comment": "Lables are not created for the following %s"%(response_dict['not_created'])
            }

        if "errors" in response_dict:
            return {
                "response_comment": self.format_error_message(response_dict["errors"])
            }
        if "message" in response_dict:
            return {"response_comment": response_dict["message"]}
        if response.status_code == 200 and "label_url" in response_dict:
            response_data = {"label_url": response_dict["label_url"]}
            return response_data
        return False

    def _print_manifest_request(self, order_ids):
        """To Print Manifest Request For Manifest Generated Records
        :param order_ids: list of order ids
        :retun : response dict
        """
        print_manifest_url = "manifests/print"
        url = url_join(API_BASE_URL, print_manifest_url)
        payload = {"order_ids": order_ids}
        response = requests.post(url, headers=self.headers, data=json.dumps(payload))
        response_dict = response.json()
        if "errors" in response_dict:
            return {
                "response_comment": self.format_error_message(response_dict["errors"])
            }
        if "message" in response_dict:
            return {"response_comment": response_dict["message"]}
        if response.status_code == 200 and "manifest_url" in response_dict:
            response_data = {"manifest_url": response_dict["manifest_url"]}
            return response_data
        return False

    def _cancel_order_request(self, order_ids):
        """To Cancel Order In Shiprocket
        :param order_ids: list of order ids
        :retun : response dict
        """
        cancel_order_url = "orders/cancel"
        url = url_join(API_BASE_URL, cancel_order_url)
        payload = json.dumps({"ids": order_ids})
        response = requests.post(url, headers=self.headers, data=payload)
        response_dict = response.json()
        if "errors" in response_dict:
            return self.format_error_message(response_dict["errors"])
        if "message" in response_dict:
            return response_dict["message"]
        return response_dict

    def _get_order_status(self, picking):
        """To Get Status Of Current Record
        :param picking: stock.picking object
        :retun : response dict
        """
        order_status_url = "orders/show/"
        url = url_join(API_BASE_URL, order_status_url)
        request_url = url_join(url, str(picking.shiprocket_order_id))
        payload = {}
        response = requests.get(
            request_url, headers=self.headers, data=payload
        )
        response_dict = response.json()
        if "errors" in response_dict:
            return {
                "response_comment": self.format_error_message(response_dict["errors"])
            }
        if "message" in response_dict:
            return {"response_comment": response_dict["message"]}
        if "data" in response_dict and response.status_code == 200:
            return {"order_status_code": str(response_dict["data"]["status_code"])}
        return False
