# -*- coding: utf-8 -*-
import requests
import json
import phonenumbers
from odoo.exceptions import UserError, AccessError
from werkzeug.urls import url_join
from datetime import datetime

API_BASE_URL = "https://sellingpartnerapi-eu.amazon.com/shipping/v2/"

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


class AmznShipment:
    """
    Class used to handle all the AMAZON API Request and Response
    """

    def __init__(self, company):
        """Initialize header for all API request.
        :param company: An res.comapny record
        :return: headers dict with parameters values
        """
        self.headers = {
            'Content-Type': 'application/json',
            'X-amzn-shipping-business-id': 'AmazonShipping_IN',
            'x-amz-access-token': company.amzn_access_token if company.amzn_access_token else None,
            'authorization': "Bearer "+ company.amzn_access_token if company.amzn_access_token else None
        }
        self.currency = company.currency_id.name

    def _verify_response(self, response_dict):
        try:
            return response_dict
        except requests.exceptions.HTTPError as errh:
            raise AccessError(('An Http Error occurred: %s' % (errh)))
        except requests.exceptions.ConnectionError as errc:
            raise AccessError(('An Error Connecting to the API occurred:Please Check Your Internet And Try Again'))
        except requests.exceptions.Timeout as errt:
            raise AccessError(("A Timeout Error occurred: %s" % (repr(errt))))
        except requests.exceptions.RequestException as err:
            raise AccessError(("An Unknown Error occurred: %s" % (repr(err))))

    def _generate_access_token(self, params):
        """Request to get access token.
        :param data: Dict of client id, client secret, refresh token of API user
        :return: authentication response dict
        """
        url = "https://api.amazon.com/auth/O2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   }
        response = requests.post(url, headers=headers, data=params, auth=None)
        response_dict = response.json()
        return self._verify_response(response_dict)


    def _check_rates(self, data):
        get_rates_url = "shipments/rates"
        url = url_join(API_BASE_URL, get_rates_url)
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        response_dict = response.json()
        return self._verify_response(response_dict)

    def _get_purchase_shipment(self, data):
        get_rates_url = "shipments"
        url = url_join(API_BASE_URL, get_rates_url)
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        response_dict = response.json()
        return self._verify_response(response_dict)

    def _get_shipment_document(self, picking):
        get_rates_url = "shipments/" + picking.shipment_id + "/documents?packageClientReferenceId=" + str(picking.id) + "&format=PDF&dpi=300"
        url = url_join(API_BASE_URL, get_rates_url)
        response = requests.get(url, headers=self.headers, data=None)
        response_dict = response.json()
        return self._verify_response(response_dict)

    def _get_tracking_shipment(self, picking):
        get_rates_url = "tracking?carrierId=" + picking.service_id.carrier_id + "&trackingId=" + picking.tracking_id
        url = url_join(API_BASE_URL, get_rates_url)
        response = requests.get(url, headers=self.headers, data=None)
        response_dict = response.json()
        return self._verify_response(response_dict)

    def _cancel_shipment(self, picking):
        get_rates_url = "shipments/" + picking.shipment_id + "/cancel"
        url = url_join(API_BASE_URL, get_rates_url)
        response = requests.put(url, headers=self.headers, data=None)
        response_dict = response.json()
        return self._verify_response(response_dict)




