from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal
from datetime import datetime
import re
from odoo.addons.website.controllers.main import Website


class Website(Website):

    #Requires Login To View Home Page
    @http.route(auth="user")
    def index(self, **kw):
        return super(Website, self).index(**kw)
    

class WebsiteSale(WebsiteSale):
    
    # Inherit To Load payment_mode_list in shop/payment page
    def _get_shop_payment_values(self, order, **kwargs):
        values = super(WebsiteSale, self)._get_shop_payment_values(order, **kwargs)
        values['payment_mode_list'] = request.env['customer.payment.mode'].search([])
        return values
    
    #Requires Login To View Shop Page
    @http.route(auth="user")
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        return super(WebsiteSale, self).shop(page=page, category=category, search=search, ppg=ppg, **post)
    
    @http.route(auth="user")
    def cart(self, access_token=None, revive='', **post):
        return super(WebsiteSale, self).cart(access_token=access_token, revive=revive, **post)

    #create a route to get and validate additional fields
    @http.route(['/shop/additional_customer_details'], type='json', auth="public", methods=['POST'], website=True)
    def validate_customer_details(self, **post):
        if not post['customer_name']:
            return{
                'errors':('Please Enter Customer Name')
            }
        if not post['customer_contact_no']:
            return{
                'errors':('Please Enter Customer Contact No')
            }
        if post['customer_email']:
            regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
            p = re.compile(regex)
            if not (re.search(p, post['customer_email'])):
                return {
                    'errors':( "Invalid Email Format")
                }
        order = request.website.sale_get_order()
        if order and order.id:
            order.write({
                'customer_name': post.get('customer_name'),
                'customer_contact_no':post.get('customer_contact_no'),
                'customer_email':post.get('customer_email'),
                'is_website_order':True,
                })
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection
        return True
    
    #Inherit to skip payment
    @http.route()
    def payment_get_status(self, sale_order_id, **post):
        if not request.website.checkout_skip_payment:
            return super(WebsiteSale, self).payment_get_status(
                sale_order_id, **post)
        return {
            'recall': True,
            'message': request.website._render(
                'bnm_distribution_system.order_state_message'),
        }

    #Inherit to confirm the payment from backend
    @http.route()
    def payment_confirmation(self, **post):
        if not request.website.checkout_skip_payment:
            return super().payment_confirmation(**post)
        order = request.env['sale.order'].sudo().browse(
            request.session.get('sale_last_order_id'))
        # order.action_confirm()
        # if not order.force_quotation_send():
            # return request.render(
            #     'bnm_distribution_system.confirmation_order_error')
        try:
            order.action_quotation_sent()
        except Exception:
            return request.render(
                "bnm_distribution_system.confirmation_order_error"
            )
        request.website.sale_reset()
        return request.render("website_sale.confirmation", {'order': order})
    
    # @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    # def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
    #     res = super(WebsiteSale,self).cart_update(product_id, add_qty=add_qty, set_qty=set_qty, **kw)
    #     if kw.get('no_redirect_to_cart'):
    #         return request.redirect('/shop')
    #     return request.redirect('/shop/cart')

class CustomerPortal(CustomerPortal):
    @http.route(['/my/orders/<int:order_id>/addpaymentdetails'], type='http',
                auth="public", methods=['POST'], website=True)
    def add_payment_request(self, order_id, access_token=None, **post):
        order_obj = request.env['sale.order']
        order = order_obj.browse(order_id).sudo()
        order.write({
            'payment_reference':post.get('payment_reference'),
            'payment_amount':float(post.get('payment_amount')),
            'payment_mode_id':int(post.get('payment_mode_id')),
            'payment_date': datetime.strptime(post.get('payment_date'), "%d-%m-%Y"),
            'state':'payment_confirmation',
        })
        return request.redirect("/my/quotes")