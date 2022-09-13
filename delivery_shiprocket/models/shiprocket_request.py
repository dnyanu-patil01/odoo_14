# -*- coding: utf-8 -*-
import requests
import json
import phonenumbers
from odoo.exceptions import UserError,AccessError
from werkzeug.urls import url_join

API_BASE_URL = "https://apiv2.shiprocket.in/v1/external/"

ERROR_MAP = {
'400': 'Bad Request	The request was invalid or cannot be otherwise served',
'401': 'Unauthorized	There is some error in validation. You need to check your token or credentials',
'404': 'Not Found	The URI requested is invalid or the resource requested does not exist',
'405': 'Method Not Allowed	The API was accessed using the wrong method. Check your HTTP method',
'422': 'Unprocessable Entity - It means the request contains invalid date or incorrect syntax or cannot be fulfilled. Try checking your code for errors',
'429': 'Too Many Requests - You have exceeded the API call rate limit',
'500': 'Server Errors - Some server error occurred. Some APIs may show this due to syntax or parameter errors',
'502': 'Server Errors - Some server error occurred. Some APIs may show this due to syntax or parameter errors',
'503': 'Server Errors - Some server error occurred. Some APIs may show this due to syntax or parameter errors',
'504': 'Server Errors - Some server error occurred. Some APIs may show this due to syntax or parameter errors',
}

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
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_dict = response.json()
            return response_dict
        except requests.exceptions.HTTPError as errh:
            raise AccessError(('An Http Error occurred: %s'%(errh)))
        except requests.exceptions.ConnectionError as errc:
            raise AccessError(('An Error Connecting to the API occurred:Please Check Your Internet And Try Again'))
        except requests.exceptions.Timeout as errt:
            raise AccessError(("A Timeout Error occurred: %s"%(repr(errt))))
        except requests.exceptions.RequestException as err:
            raise AccessError(("An Unknown Error occurred: %s"%(repr(err))))

    def _import_all_channels(self):
        """Request to pull channels from shiprocket to Odoo.
        :return: response dict of get channel api call
        """
        channel_url = "channels"
        url = url_join(API_BASE_URL, channel_url)
        try:
            response = requests.get(url, headers=self.headers, data={})
            if response.status_code == 200:
                response_dict = response.json()
                return response_dict
            elif response.status_code == 404:
                raise AccessError("No Channels Found!")
        except requests.exceptions.HTTPError as errh:
            raise AccessError(('An Http Error occurred: %s'%(errh)))
        except requests.exceptions.ConnectionError as errc:
            raise AccessError(('An Error Connecting to the API occurred:Please Check Your Internet And Try Again'))
        except requests.exceptions.Timeout as errt:
            raise AccessError(("A Timeout Error occurred: %s"%(repr(errt))))
        except requests.exceptions.RequestException as err:
            raise AccessError(("An Unknown Error occurred: %s"%(repr(err))))

    def _import_picking_address(self):
        """Request to pull pickup address from shiprocket to Odoo.
        :return: response dict contains parameters need to create pickup address
        in odoo or error message.
        """
        get_pickup_address_url = "settings/company/pickup"
        url = url_join(API_BASE_URL, get_pickup_address_url)
        try:
            response = requests.get(url, headers=self.headers, data={})
            if response.status_code == 200:
                response_dict = response.json()
                return response_dict
            elif response.status_code == 404:
                raise AccessError("No Channels Found!")
        except requests.exceptions.HTTPError as errh:
            raise AccessError(('An Http Error occurred: %s'%(errh)))
        except requests.exceptions.ConnectionError as errc:
            raise AccessError(('An Error Connecting to the API occurred:Please Check Your Internet And Try Again'))
        except requests.exceptions.Timeout as errt:
            raise AccessError(("A Timeout Error occurred: %s"%(repr(errt))))
        except requests.exceptions.RequestException as err:
            raise AccessError(("An Unknown Error occurred: %s"%(repr(err))))

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
                return(
                    "The Pickup/Seller Address Fields is missing or wrong (Missing field(s) :  \n %s)"
                    % ", ".join(res).replace("_id", "")
                )
            if not self._convert_phone_number(
                pickup_location.phone, pickup_location.country_id.code
            ):
                return("Pickup/Seller Phone number is invalid.")
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
                        parent_res.insert(0,picking.name if picking else "")
                        raise UserError(
                            "The Customer/Partner Address Fields is missing or wrong (Missing field(s) :  \n %s)"
                            % ", ".join(parent_res).replace("_id", "")
                        )
                else:
                    res.insert(0,picking.name if picking else "")
                    raise UserError(
                            "The Customer/Partner Address Fields is missing or wrong (Missing field(s) :  \n %s)"
                            % ", ".join(res).replace("_id", "")
                        )
            #Trying To Get phone number from receipt if not trying to get it from parent
            if not self._convert_phone_number(
                recipient.phone, recipient.country_id.code
            ):
                if not recipient.parent_id:
                    raise UserError("%s Phone number is invalid."%(recipient.name))
                else:
                    if recipient.parent_id.phone and recipient.parent_id.country_id:
                        if not self._convert_phone_number(recipient.parent_id.phone, recipient.parent_id.country_id.code):
                            raise UserError("%s - Phone number is invalid."%(recipient.parent_id.name))
                    else:
                        raise UserError("%s Phone number is invalid."%(recipient.name))
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
                raise UserError("%s - Please provide at least one item to ship."%(order.name))
            for line in order.order_line.filtered(
                lambda line: not line.product_id.weight
                and not line.is_delivery
                and line.product_id.type not in ["service", "digital"]
                and not line.display_type
            ):
                raise UserError(
                    "%s - The estimated price cannot be computed because the weight of your product is missing."%(order.name)
                )

        # check required value for picking
        if picking:
            if not picking.move_lines:
                raise UserError("%s - Please provide at least one item to ship."%(picking.name))
            if not picking.shipping_weight:
                raise UserError(
                    "%s - The estimated price cannot be computed because the weight of your product is missing."%(picking.name)
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
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))
            return response.json()
        except requests.exceptions.HTTPError as errh:
            raise AccessError(('An Http Error occurred: %s'%(errh)))
        except requests.exceptions.ConnectionError as errc:
            raise AccessError(('An Error Connecting to the API occurred:Please Check Your Internet And Try Again'))
        except requests.exceptions.Timeout as errt:
            raise AccessError(("A Timeout Error occurred: %s"%(repr(errt))))
        except requests.exceptions.RequestException as err:
            raise AccessError(("An Unknown Error occurred: %s"%(repr(err))))

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
            "payment_method": picking.payment_method,
        }
        order_items,sub_total = self.prepare_order_items(picking)
        data.update({
            "order_items": order_items,
            "sub_total": sub_total,
        })
        print(data)
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
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))
            response_dict = response.json()
            if response.status_code == 422:
                if "errors" in response_dict:
                    raise UserError(self.format_error_message(response_dict["errors"]))
                if "message" in response_dict:
                    raise UserError(self.format_error_message(response_dict["message"]))
            if response.status_code == 200:
                response_data = {
                    "shiprocket_order_id": response_dict["order_id"],
                    "shiprocket_shipping_id": response_dict["shipment_id"],
                }
                return response_data
            if response.status_code not in (200,422):
                if ERROR_MAP.get(str(response.status_code)):
                    raise AccessError('%s Error Occured! %s'%(str(response.status_code),ERROR_MAP.get(str(response.status_code))))
            return False
        except requests.exceptions.HTTPError as errh:
            raise AccessError(('An Http Error occurred: %s'%(errh)))
        except requests.exceptions.ConnectionError as errc:
            raise AccessError(('An Error Connecting to the API occurred:Please Check Your Internet And Try Again'))
        except requests.exceptions.Timeout as errt:
            raise AccessError(("A Timeout Error occurred: %s"%(repr(errt))))
        except requests.exceptions.RequestException as err:
            raise AccessError(("An Unknown Error occurred: %s"%(repr(err))))

    def create_channel_specific_order(self, picking):
        """Create Order In Shiprocket
        :param picking: stock.picking object
        """
        if not picking.package_ids:
            picking._pre_put_in_pack_hook(picking.move_line_ids)
        data = self.prepare_order_data(picking, "forward")
        if not picking.pickup_location:
            picking.write({'response_comment':"Please Select Shiprocket Pickup Location Before Validate"})
            return False
        if not picking.channel_id:
            picking.write({'response_comment':"Please Select Shiprocket Channel Before Validate."})
            return False
        payload = json.dumps(data)
        order_creation_url = "orders/create/adhoc"
        url = url_join(API_BASE_URL, order_creation_url)
        try:
            response = requests.post(url, headers=self.headers, data=payload)
            response_dict = response.json()
            if response.status_code == 400:
                if "errors" in response_dict:
                    picking.write({'response_comment':self.format_error_message(response_dict["errors"])})
                    return False
                if "message" in response_dict:
                    picking.write({'response_comment':response_dict["message"]})
                    return False
            if response.status_code == 422:
                if "errors" in response_dict:
                    picking.write({'response_comment':self.format_error_message(response_dict["errors"])})
                    return False
                if "message" in response_dict:
                    picking.write({'response_comment':response_dict["message"]})
                    return False
            if response.status_code == 200:
                if 'order_id' in response_dict and 'shipment_id' in response_dict:
                    response_data = {
                        "shiprocket_order_id": response_dict["order_id"],
                        "shiprocket_shipping_id": response_dict["shipment_id"],
                        "shiprocket_order_status_id":1,
                        "response_comment":'Order Placed Successfully In Shiprocket',
                    }
                    return response_data
                else:
                    picking.write({"response_comment":response_dict})
            if response.status_code not in (200,422):
                if ERROR_MAP.get(str(response.status_code)):
                    return {'response_comment':'%s Error Occured! %s'%(str(response.status_code),ERROR_MAP.get(str(response.status_code)))}
            else:
                picking.write({"response_comment":response_dict})
            return False
        except requests.exceptions.HTTPError as errh:
            raise AccessError(('An Http Error occurred: %s'%(errh)))
        except requests.exceptions.ConnectionError as errc:
            raise AccessError(('An Error Connecting to the API occurred:Please Check Your Internet And Try Again'))
        except requests.exceptions.Timeout as errt:
            raise AccessError(("A Timeout Error occurred: %s"%(repr(errt))))
        except requests.exceptions.RequestException as err:
            raise AccessError(("An Unknown Error occurred: %s"%(repr(err))))

    def prepare_order_items(self, picking):
        """Prepare Order Line Items Need For Order Creation Request
        :param picking: stock.picking object
        :return: order items dict
        """
        order_items = []
        order_value = 0
        for line in picking.move_lines:
            order_line_vals = {
                "name": line.product_id.name,
                "sku": line.product_id.default_code,
                "units": line.quantity_done,
                "selling_price": line.sale_line_id.price_unit,
                "discount": "",
                "hsn": line.product_id.l10n_in_hsn_code or "",
                "tax": "",
            }
            order_value += (line.quantity_done * line.sale_line_id.price_unit)
            order_items.append(order_line_vals)
        return order_items,order_value

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
        # self.check_required_value(
        #     recipient=partner, shipper=False, order=False, picking=picking
        # )
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
            # self.check_required_value(
            #     recipient=partner, shipper=False, order=False, picking=picking
            # )
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
            # self.check_required_value(
            #     recipient=partner, shipper=False, order=False, picking=picking
            # )
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
            # self.check_required_value(
            #     recipient=partner, shipper=False, order=False, picking=picking
            # )
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
            msg_format = "%s : %s \n" % (str(error), str(message))
            message_format += msg_format
        return message_format

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
        try:
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
            elif response.status_code in (422,404):
                if "errors" in response_dict:
                    return {
                        "response_comment": self.format_error_message(
                            response_dict["errors"]
                        )
                    }
                if "message" in response_dict:
                    return {"response_comment": self.format_error_message(response_dict["message"])}
            if response.status_code not in (200,422):
                if ERROR_MAP.get(str(response.status_code)):
                    return {'response_comment':'%s Error Occured! %s'%(str(response.status_code),ERROR_MAP.get(str(response.status_code)))}
                else:
                    return {"response_comment":response_dict}
            return False
        except requests.exceptions.HTTPError as errh:
            raise AccessError(('An Http Error occurred: %s'%(errh)))
        except requests.exceptions.ConnectionError as errc:
            raise AccessError(('An Error Connecting to the API occurred:Please Check Your Internet And Try Again'))
        except requests.exceptions.Timeout as errt:
            raise AccessError(("A Timeout Error occurred: %s"%(repr(errt))))
        except requests.exceptions.RequestException as err:
            raise AccessError(("An Unknown Error occurred: %s"%(repr(err))))

    def _create_awb(self, data, picking):
        """Request To Create AWB for current order.
        :param data: Dict of courier_id and shipment_id
        :param picking:stock.picking object
        :return: response dict
        """
        create_awb_url = "courier/assign/awb"
        url = url_join(API_BASE_URL, create_awb_url)
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))
            response_dict = response.json()
            if response.status_code in (400,422):
                return {
                    "response_comment": response.text
                }
            if response.status_code not in (400,422,500):
                if ERROR_MAP.get(str(response.status_code)):
                    return {'response_comment':'%s Error Occured! %s'%(str(response.status_code),ERROR_MAP.get(str(response.status_code)))}
            if response.status_code == 200 and 'response' in response_dict:
                if 'awb_code' in response_dict["response"]["data"] and response_dict["response"]["data"]["awb_code"] != False:
                    response_data = {
                        "shiprocket_awb_code": response_dict["response"]["data"]["awb_code"],
                        "carrier_tracking_ref":response_dict["response"]["data"]["awb_code"],
                        "response_comment":'AWB Assigned Successfully!',
                        "is_awb_generated":True,
                    }
                    #Some Courier Partner like Amazon Shipping Are Creating AWB Request While Generating AWB
                    status_code = self._get_order_status(picking)
                    if 'order_status_code' in status_code and status_code['order_status_code'] == '4':
                        response_data.update({'is_pickup_request_done':True,'pickup_request_note':'Automatically Pickup Requested While Creating AWB'})
                    return response_data
                else:
                    return {"response_comment": response_dict}
            else:
                return {"response_comment": response_dict}
        except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError):
            return {"response_comment":"The url that this service requested returned an error.Please check your internet connectivity and try again once after few minutes."}

    def _generate_pickup_request(self, shipping_id):
        """To Create Pickup Request For AWB Generated Records
        :param shipping_id: list of shipping ids
        :retun : response dict
        """
        generate_pickup_url = "courier/generate/pickup"
        url = url_join(API_BASE_URL, generate_pickup_url)
        payload = {"shipment_id": shipping_id}
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(payload))
            response_dict = response.json()
            if "errors" in response_dict:
                return {
                    "response_comment": self.format_error_message(response_dict["errors"])
                }
            if "message" in response_dict:
                return {"response_comment": response_dict["message"]}
            if response.status_code == 200 and "response" in response_dict and response_dict['pickup_status'] == 1:
                note = "%s" % (
                    response_dict["response"]["data"],
                )
                return {"pickup_request_note": note,"shiprocket_order_status_id":3,"response_comment": 'Pickup Request Created Successfully'}
            return {"response_comment": response_dict}
        except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError):
            return {"response_comment":"The url that this service requested returned an error.Please check your internet connectivity and try again once after few minutes."}


    def _generate_manifest_request(self, shipping_id):
        """To Create Manifest For Pickup Request Generated Records
        :param shipping_id: list of shipping ids
        :retun : response dict
        """
        generate_manifest_url = "manifests/generate"
        url = url_join(API_BASE_URL, generate_manifest_url)
        payload = {"shipment_id": shipping_id}
        try:
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
        except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError):
            return {"response_comment":"The url that this service requested returned an error.Please check your internet connectivity and try again once after few minutes."}


    def _generate_label_request(self, shipping_id):
        """To Generate Label For AWB Generated Records
        :param shipping_id: list of shipping ids
        :retun : response dict
        """
        generate_label_url = "courier/generate/label"
        url = url_join(API_BASE_URL, generate_label_url)
        payload = {"shipment_id": shipping_id}
        try:
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
                response_data = {"label_url": response_dict["label_url"],"response_comment": 'Label Generated Successfully'}
                return response_data
            return False
        except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError):
            return {"response_comment":"The url that this service requested returned an error.Please check your internet connectivity and try again once after few minutes."}


    def _print_manifest_request(self, order_ids):
        """To Print Manifest Request For Manifest Generated Records
        :param order_ids: list of order ids
        :retun : response dict
        """
        print_manifest_url = "manifests/print"
        url = url_join(API_BASE_URL, print_manifest_url)
        payload = {"order_ids": order_ids}
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(payload))
            response_dict = response.json()
            if "errors" in response_dict:
                return {
                    "response_comment": self.format_error_message(response_dict["errors"])
                }
            if "message" in response_dict:
                return {"response_comment": response_dict["message"]}
            if response.status_code == 200 and "manifest_url" in response_dict:
                response_data = {"manifest_url": response_dict["manifest_url"],"response_comment": 'Manifest Generated Successfully'}
                return response_data
            return False
        except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError):
            return {"response_comment":"The url that this service requested returned an error.Please check your internet connectivity and try again once after few minutes."}


    def _cancel_order_request(self, order_ids):
        """To Cancel Order In Shiprocket
        :param order_ids: list of order ids
        :retun : response dict
        """
        cancel_order_url = "orders/cancel"
        url = url_join(API_BASE_URL, cancel_order_url)
        payload = json.dumps({"ids": order_ids})
        try:
            response = requests.post(url, headers=self.headers, data=payload)
            response_dict = response.json()
            if response.status_code in (200,204):
                return response.status_code
            elif "errors" in response_dict or "message" in response_dict:
                return self.format_error_message(response_dict)
            else:
                return response_dict
        except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError):
            return {"response_comment":"The url that this service requested returned an error.Please check your internet connectivity and try again once after few minutes."}

        
    def _get_order_status(self, picking):
        """To Get Status Of Current Record
        :param picking: stock.picking object
        :retun : response dict
        """
        order_status_url = "orders/show/"
        url = url_join(API_BASE_URL, order_status_url)
        request_url = url_join(url, str(picking.shiprocket_order_id))
        payload = {}
        try:
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
        except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError):
            return {"response_comment":"The url that this service requested returned an error.Please check your internet connectivity and try again once after few minutes."}


    def bulk_awb_creation_request(self,picking,bulk_process):
        check_serviceability_vals = {
            "pickup_postcode": int(picking.pickup_location.pin_code),
            "delivery_postcode": int(picking.partner_id.zip),
            "order_id": int(picking.shiprocket_order_id),
        }
        check_serviceability_url = "courier/serviceability/"
        url = url_join(API_BASE_URL, check_serviceability_url)
        response_data_error = None
        serviceability_response_dict = None
        selected_courier_dict = None
        try:
            serviceability_response = requests.get(url, headers=self.headers, data=json.dumps(check_serviceability_vals))
        except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError):
            response_data_error = "The url that this service requested returned an error.Please check your internet connectivity and try again once after few minutes."
        try:
            serviceability_response_dict = serviceability_response.json()
        except json.JSONDecodeError:
            response_data_error = "Invaild JSON in Response - %s"%(serviceability_response.text)
        if response_data_error:
            picking.write({'response_comment':response_data_error})
            return False
        if serviceability_response.status_code in (422,404):
            picking.write({'response_comment':serviceability_response.text})
            return False
        if serviceability_response.status_code not in (200,422,404):
            if ERROR_MAP.get(str(serviceability_response.status_code)):
                picking.write({'response_comment':'%s Error Occured! %s'%(str(serviceability_response.status_code),ERROR_MAP.get(str(serviceability_response.status_code)))})
                return False
        if serviceability_response.status_code == 200 and "data" in serviceability_response_dict:
            available_courier_list = serviceability_response_dict["data"]["available_courier_companies"]
            if available_courier_list:
                if bulk_process.shiprocket_courier_priority == 'rate':
                    selected_courier_dict = max(available_courier_list, key=lambda d: d['rating'])
                if bulk_process.shiprocket_courier_priority == 'price':
                    selected_courier_dict = min(available_courier_list, key=lambda d: d['rate'])
                if bulk_process.shiprocket_courier_priority == 'fast':
                    selected_courier_dict = min(available_courier_list, key=lambda d: d['etd_hours'])
                if bulk_process.shiprocket_courier_priority == 'custom':
                    selected_courier_dict = [x for x in available_courier_list if x["courier_company_id"] == serviceability_response_dict['data']['recommended_courier_company_id']][-1]
                if bulk_process.shiprocket_courier_priority == 'recommend':
                    selected_courier_dict = [x for x in available_courier_list if x["courier_company_id"] == serviceability_response_dict['data']['shiprocket_recommended_courier_id']][-1]
                if selected_courier_dict:
                    data_vals = {
                        "courier_id": int(selected_courier_dict["courier_company_id"]),
                        "shipment_id": int(picking.shiprocket_shipping_id),
                    }
                    response_data = self._create_awb(data_vals, picking)
                    response_data.update({
                        'courier_id':picking.get_courier_id(selected_courier_dict["courier_company_id"], selected_courier_dict["courier_name"]),
                        'courier_rate':selected_courier_dict['rate'],
                        'bulk_order_id':bulk_process.id,
                    })
                    picking.write(response_data)
        return True
    
    def _get_order_details(self, picking):
        """To get order details from shiprocket to update awb and other flags
        :param picking: stock.picking object
        """
        order_url = "orders/show/"
        url = url_join(API_BASE_URL, order_url)
        request_order_url = url_join(url, str(picking.shiprocket_order_id))
        payload = {}
        try:
            response = requests.get(
                request_order_url, headers=self.headers, data=payload
            )
            response_dict = response.json()
            picking_vals = {}
            if response.status_code in (400,404):
                picking_vals.update({'response_comment':response_dict})
            if response.status_code not in (200,400,404):
                if ERROR_MAP.get(str(response.status_code)):
                    picking_vals.update({'response_comment':'%s Error Occured! %s'%(str(response.status_code),ERROR_MAP.get(str(response.status_code)))})
            if response.status_code == 200 and 'data' in response_dict:
                if 'shipments' in response_dict['data']:
                    awb_code = response_dict['data']['shipments']['awb'] or False
                    courier_name = response_dict['data']['shipments']['courier'] or False
                    courier_code = response_dict['data']['shipments']['courier_id'] or False
                    if awb_code and courier_code and courier_name:
                        picking_vals.update({
                            'shiprocket_awb_code':awb_code,
                            'carrier_tracking_ref':awb_code,
                            'courier_id':picking.get_courier_id(str(courier_code),str(courier_name)),
                            'courier_rate':response_dict['data']['awb_data']['charges']['freight_charges'],
                            'is_awb_generated':True
                        })
                    if response_dict['data']['shipments']['manifest_id']:
                        picking_vals.update({'is_manifest_generated':True,'is_pickup_request_done':True})
                else:
                    picking_vals.update({'response_comment':'No Shipment Details Found To Update AWB Details'})
            else:
                picking_vals.update({'response_comment':'No Data Found In Response To AWB Details'})
            self._get_order_status(picking)
            picking.write(picking_vals)
            return True
        except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError):
            picking.write({"response_comment":"The url that this service requested returned an error.Please check your internet connectivity and try again once after few minutes."})
            return True


    def _update_pickup_location(self,picking_ids,pickup_location):
        """To Update Pickup Location In Shiprocket
        :param picking_ids: stock.picking objects
        :param pickup_location: new picking_location
        """
        update_pickup_location_url = "orders/address/pickup/"
        url = url_join(API_BASE_URL, update_pickup_location_url)
        for picking in picking_ids:
            payload = json.dumps({
                "order_id":[int(picking.shiprocket_order_id)],
                "pickup_location":str(pickup_location.pickup_location)
            })
            response = requests.request("PATCH", url, headers=self.headers, data=payload)
            vals = {"response_comment": self.format_error_message(response.json())}
            if response.status_code == 200:
                vals.update({'pickup_location':pickup_location.id})
            elif response.status_code == 400:
                vals.update({'response_comment':'Pickup Code does not exist or Order Id does not exists'})
            else:
                vals.update({'Invalid Arguments supplied!'})
            picking.write(vals)
        return True

    def create_wrapper_order(self, picking):
        """Wrapper API Call To Create, Ship and Generate Label and Manifest for Order
        :param picking: stock.picking object
        """
        if not picking.package_ids:
            picking._pre_put_in_pack_hook(picking.move_line_ids)
        data = self.prepare_order_data(picking, "forward")
        if not picking.pickup_location:
            picking.write({'response_comment':"Please Select Shiprocket Pickup Location Before Validate"})
            return False
        if not picking.channel_id:
            picking.write({'response_comment':"Please Select Shiprocket Channel Before Validate."})
            return False
        if data:
            data.update({ 
                "vendor_details": {
                "email": picking.pickup_location.email,
                "phone": int(picking.pickup_location.phone),
                "name": picking.pickup_location.name,
                "address": picking.pickup_location.address,
                "city": picking.pickup_location.city,
                "state": picking.pickup_location.state_id.name,
                "country": picking.pickup_location.country_id.name,
                "pin_code": int(picking.pickup_location.pin_code),
                "pickup_location": picking.pickup_location.pickup_location,},
                "pickup_location": picking.pickup_location.pickup_location,
})
        
        payload = json.dumps(data)
        order_creation_url = "shipments/create/forward-shipment"
        url = url_join(API_BASE_URL, order_creation_url)
        try:
            response = requests.post(url, headers=self.headers, data=payload)
            response_dict = response.json()
            if "errors" in response_dict:
                picking.write({'response_comment':self.format_error_message(response_dict)})
                return
            if "status" in response_dict and response_dict['status'] == 0:
                picking.write({'response_comment':self.format_error_message(response_dict)})
                return
            if response.status_code == 400:
                if "errors" in response_dict:
                    picking.write({'response_comment':self.format_error_message(response_dict["errors"])})
                    return False
                if "message" in response_dict:
                    picking.write({'response_comment':response_dict["message"]})
                    return False
            if response.status_code == 200 and response_dict['status'] == 1:
                response_data = {}
                if 'order_id' in response_dict['payload'] and 'shipment_id' in response_dict['payload']:
                    response_data.update({
                        "shiprocket_order_id": response_dict['payload']["order_id"],
                        "shiprocket_shipping_id": response_dict['payload']["shipment_id"],
                        "shiprocket_order_status_id":1,
                    })
                if response_dict['payload']['awb_generated'] == 1 and 'awb_code' in response_dict['payload'] and response_dict['payload']['awb_code']:
                    response_data.update({
                        'shiprocket_awb_code':response_dict['payload']["awb_code"],
                        'is_awb_generated':True,
                        'courier_id':picking.get_courier_id(str(response_dict['payload']['courier_company_id']),str(response_dict['payload']['courier_name']))
                    })
                if response_dict['payload']['label_generated'] == 1 and 'label_url' in response_dict['payload']:
                    response_data.update({
                        'label_url':response_dict['payload']['label_url']
                    })
                if response_dict['payload']['pickup_generated'] == 1 and 'pickup_token_number' in response_dict['payload'] and response_dict['payload']['pickup_token_number'] != False:
                    response_data.update({
                        'pickup_request_note':response_dict['payload']['pickup_token_number'],
                        'is_pickup_request_done':True,
                        "shiprocket_order_status_id":4,
                    })
                if response_dict['payload']['manifest_generated'] == 1 and 'manifest_url' in response_dict['payload']:
                    response_data.update({
                        'manifest_url':response_dict['payload']['manifest_url'],
                        'is_manifest_generated':True
                    })
                return response_data
            else:
                picking.write({"response_comment":self.format_error_message(response_dict)})
            return False
        except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError):
            picking.write({"response_comment":"The url that this service requested returned an error.Please check your internet connectivity and try again once after few minutes."})
            return False

    def format_ndr_data(self,response_dict):
        response_values = []
        if 'data' in response_dict and response_dict.get('data') != []:
            for value in response_dict['data']:
                ndr_values = {}
                if 'id' in value:
                    ndr_values.update({'id':str(value['id'])})
                else:
                    ndr_values.update({"id":False})
                if 'shipment_id' in value:
                    ndr_values.update({'shipment_id':str(value['shipment_id'])})
                else:
                    ndr_values.update({"shipment_id":False})
                if 'awb_code' in value:
                    ndr_values.update({'awb_code':str(value['awb_code'])})
                else:
                    ndr_values.update({"awb_code":False})
                if 'ndr_raised_at' in value:
                    ndr_values.update({'ndr_raised_at':str(value['ndr_raised_at'])})
                else:
                    ndr_values.update({"ndr_raised_at":False})
                if 'attempts' in value:
                    ndr_values.update({'attempts':str(value['attempts'])})
                else:
                    ndr_values.update({"attempts":False})
                if 'reason' in value:
                    ndr_values.update({'reason':str(value['reason'])})
                else:
                    ndr_values.update({"reason":False})
                if 'escalation_status' in value:
                    ndr_values.update({'escalation_status':str(value['escalation_status'])})
                else:
                    ndr_values.update({"escalation_status":False})
                if 'shipment_channel_id' in value:
                    ndr_values.update({'shipment_channel_id':str(value['shipment_channel_id'])})
                else:
                    ndr_values.update({"shipment_channel_id":False})
                if 'courier' in value:
                    ndr_values.update({'courier':str(value['courier'])})
                else:
                    ndr_values.update({"courier":False})
                if 'history' in value:
                    ndr_values.update({'history':value['history']})
                else:
                    ndr_values.update({"history":False})
                response_values.append(ndr_values)
        return response_values

    def _get_specific_ndr_shipments(self,awb_code):
        """To Get Specific NDR Shipment Informations
        :param:awb_code of particular shipment"""
        payload = {}
        ndr_url = "ndr/%s"%('D82183221')
        url = url_join(API_BASE_URL, ndr_url)
        try:
            response = requests.get(url, headers=self.headers, data=payload)
            if response.status_code == 200:
                response_dict = response.json()
                return self.format_ndr_data(response_dict)
            else:
                if ERROR_MAP.get(str(response.status_code)):
                    return {'response_comment':'%s Error Occured! %s'%(str(response.status_code),ERROR_MAP.get(str(response.status_code)))}
                else:
                    return {"response_comment":response.text}
        except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError):
            return {"response_comment":"The url that this service requested returned an error.Please check your internet connectivity and try again once after few minutes."}


    def _get_all_ndr_shipments(self):
        """To Get All NDR Shipment Informations"""
        payload = {}
        all_ndr_url = "ndr/all"
        url = url_join(API_BASE_URL, all_ndr_url)
        all_ndr_values = []
        response = requests.get(url, headers=self.headers, data=payload)
        next_url = False
        response_dict = response.json()
        if response.status_code == 200:
            all_ndr_values.extend(self.format_ndr_data(response_dict))
            if 'meta' in response_dict and response_dict['meta'] != False:
                if 'pagination' in response_dict['meta']:
                    if "links" in  response_dict['meta']['pagination']:
                        if "next" in response_dict['meta']['pagination']['links']:
                            next_url = response_dict['meta']['pagination']['links']['next']
        else:
            if ERROR_MAP.get(str(response.status_code)):
                return {'response_comment':'%s Error Occured! %s'%(str(response.status_code),ERROR_MAP.get(str(response.status_code)))}
            else:
                return {"response_comment":response_dict}
        while next_url:
            next_response = requests.get(next_url, headers=self.headers, data=payload)    
            next_response_dict = next_response.json()
            if next_response.status_code == 200:
                all_ndr_values.extend(self.format_ndr_data(next_response_dict))
                if 'meta' in next_response_dict and next_response_dict['meta'] != False:
                    if 'pagination' in next_response_dict['meta']:
                        if "links" in  next_response_dict['meta']['pagination']:
                            if "next" in next_response_dict['meta']['pagination']['links']:
                                next_url = next_response_dict['meta']['pagination']['links']['next']             
            else:
                if ERROR_MAP.get(str(next_response.status_code)):
                    return {'response_comment':'%s Error Occured! %s'%(str(next_response.status_code),ERROR_MAP.get(str(next_response.status_code)))}
                else:
                    return {"response_comment":next_response_dict}
        if all_ndr_values != []:
            return all_ndr_values
        else:
            return {"response_comment":"No NDR Details Found!"}

    def _action_ndr(self,data,awb_code):
        action_ndr_url = "ndr/%s/action"%(awb_code)
        url = url_join(API_BASE_URL, action_ndr_url)
        payload = json.dumps(data)
        try:
            response = requests.post(url, headers=self.headers, data=payload)
            response_dict = response.json()
            if response.status_code in (200,204):
                return response.status_code
            elif "errors" in response_dict or "message" in response_dict:
                return self.format_error_message(response_dict)
            else:
                return response_dict
        except (ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout, requests.exceptions.HTTPError):
            return {"response_comment":"The url that this service requested returned an error.Please check your internet connectivity and try again once after few minutes."}
