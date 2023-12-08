# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class HotelReservation(http.Controller):
    @http.route('/my/home/reservation_list', type="http", auth='public', website=True)
    def get_reservation(self, **kw):
        selected_state = request.params.get('state', 'all')
        reservation_details = request.env['hotel.reservation'].sudo().search([])

        vals = {
            'my_details': reservation_details,
            'page_name': 'reservation_details',
            'selected_state': selected_state,
        }
        return request.render('nthub_hotel_sys.reservation_details_page', vals)

    @http.route('/my/home/reservation_list/<string:state>', type="http", auth='public', website=True)
    def get_reservation_filtered(self, state=None, **kw):
        if state and state != 'all':
            domain = [('state', '=', state)]
            reservation_details = request.env['hotel.reservation'].sudo().search(domain)
        else:
            reservation_details = request.env['hotel.reservation'].sudo().search([])

        vals = {
            'my_details': reservation_details,
            'page_name': 'reservation_details',
            'selected_state': state,
        }
        return request.render('nthub_hotel_sys.reservation_details_page', vals)

    @http.route('/my/home/reservation/form', type="http", auth='public', website=True, csrf=True)
    def reservation_form_view(self, **kwargs):
        customer_ids = request.env['res.partner'].sudo().search([])
        room_ids = request.env['hotel.room'].sudo().search([])
        vals = {
            'customers': customer_ids,
            'rooms': room_ids,
            'page_name': 'reservation_form'
        }
        return request.render('nthub_hotel_sys.customer_reservation_form', vals)

    @http.route('/my/home/reservation/create', type="http", auth='public', website=True, csrf=True)
    def request_submit(self, **kwargs):
        customer_id = int(kwargs.get('customer_id'))
        room_id = int(kwargs.get('room_id'))
        res_start_date = kwargs.get('res_start_date')
        res_end_date = kwargs.get('res_end_date')

        if not customer_id or not room_id or not res_start_date or not res_end_date:
            return request.render('nthub_hotel_sys.error_message', {'error_message': "Missing required data"})

        start_date = datetime.strptime(res_start_date, "%Y-%m-%d")
        end_date = datetime.strptime(res_end_date, "%Y-%m-%d")
        duration = (end_date - start_date).days + 1

        reservation_data = {
            'customer_id': customer_id,
            'room_id': room_id,
            'res_start_date': res_start_date,
            'res_end_date': res_end_date,
            'duration': duration,
        }

        reservation = request.env['hotel.reservation'].sudo().create(reservation_data)

        # Optionally, check room availability and perform additional actions here

        return request.redirect('/my/home/reservation_list')

    @http.route(['/desired_reservation/<int:order_id>'], type="http", website=True, auth='public')
    def get_customer_form(self, order_id, **kw):
        order = request.env['hotel.reservation'].sudo().browse(order_id)
        vals = {
            "order": order,
            'page_name': 'desired_reservation'
        }
        return request.render('nthub_hotel_sys.customer_details_form_shown_link', vals)
