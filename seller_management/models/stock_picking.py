from odoo import _, api, fields, models
from datetime import datetime, timedelta
from urllib.parse import urljoin

class StockPicking(models.Model):
    _inherit = "stock.picking"

    seller_id = fields.Many2one("res.partner",string="Seller",copy=False,domain="[('seller','=',True),('active','=',True),('parent_id','=',False)]")
    mobile = fields.Char(related="partner_id.mobile",readonly=True) 
    phone = fields.Char(related="partner_id.phone",readonly=True)
    active = fields.Boolean('Active',default=True, help="If unchecked, it will allow you to hide the delivery order without removing it.")
    cancel_reason_check = fields.Boolean(string='Cancel Reason Check')


    @api.model
    def create(self, vals):
        #To Pass Seller ID While Creating Backorders
        if 'backorder_id' in vals and vals['backorder_id'] != False:
            orgin = self.browse(int(vals['backorder_id']))
            if orgin.seller_id:
                vals.update({'seller_id':orgin.seller_id.id})
        return super(StockPicking ,self).create(vals)

    def action_cancel(self):
        """To Trigger Mail To Fulfillment Team On The Cancellation Of SO"""
        template = self.env.ref('seller_management.mail_template_seller_do_cancellation')
        if template:
            mail_id = template.send_mail(self.id)
            Mail = self.env['mail.mail'].sudo().browse(mail_id)
        Mail.send()
        return super().action_cancel()

    def cancel_order(self):
        order_ids = False
        if self.env.context.get('active_model') == 'stock.picking':
            order_ids = self.env.context.get('active_ids') or False
        if not order_ids:
            ctx = {'order_ids': self.ids}
        else:
            ctx = {"order_ids": order_ids}
        return {
            "name": ("Cancel Sale & Delivery Order"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "sale.delivery.order.cancel.reason",
            "target": "new",
            "context": ctx,
        }

    def delivery_escalation_for_hfn_seller(self):
        """To Trigger Mail To HFN Seller if the delivery is not processed for 72 hrs"""
        sellers = self.env['res.partner'].search([('seller', '=', True),('escalation_mail', '=', True)])
        esc_date = datetime.now().date() - timedelta(days=3)
        for rec in sellers:
            delivery_orders = self.env['stock.picking'].search([('scheduled_date', '<=', esc_date),
                                                                ('state', 'not in', ['done','cancel']),
                                                                ('seller_id', '=', rec.id)
                                                                ], order='create_date asc')
            if delivery_orders:
                ctx = dict(self.env.context)
                ctx['numbers'] = len(delivery_orders)
                ctx['email_to'] = rec.email
                ctx['seller_name'] = rec.name
                orders = []
                for line in delivery_orders:
                    hrs = datetime.now() - line.scheduled_date
                    total_hrs = (hrs.total_seconds())/3600
                    orders.append({'name': line.name,
                                   'sale_order': line.origin,
                                   'id': line.id,
                                   'hours': int(total_hrs)})
                ctx['orders'] = orders
                ############################
                template = self.env.ref('seller_management.escalation_email_alert_to_seller')
                template.with_context(ctx).send_mail(self.id, force_send=True)
                

    def delivery_escalation_to_fulfillment_team(self):
        """To Trigger Mail To Fulfillment team if the delivery is not processed for 96 hrs"""
        sellers = self.env['res.partner'].search([('seller', '=', True),('escalation_mail', '=', True)])
        esc_date = datetime.now().date() - timedelta(days=4)
        delivery_orders = self.env['stock.picking'].search([('scheduled_date', '<=', esc_date),
                                                            ('state', 'not in', ['done','cancel']),
                                                            ('seller_id', 'in', sellers.ids),
                                                            ], order='create_date asc')
        if delivery_orders:
            ctx = dict(self.env.context)
            ctx['numbers'] = len(delivery_orders)
            ctx['email_to'] = self.env["ir.config_parameter"].sudo().get_param("fulfillment_team_recipients")
            orders = []
            for line in delivery_orders:
                hrs = datetime.now() - line.scheduled_date
                so = self.env['sale.order'].search([('name','=',line.origin)])
                total_hrs = (hrs.total_seconds())/3600
                orders.append({'name': line.name,
                               'sale_order': so.name,
                               'id': line.id,
                               'seller_name': line.seller_id.name,
                               'so_id': so.id,
                               'shopify_order': so.shopify_order_number,
                               'shopify_order_link': so.shopify_order_id,
                               'hours': int(total_hrs)})
            ctx['orders'] = orders
            ############################
            template = self.env.ref('seller_management.escalation_email_alert_to_fulfillment_team')
            template.with_context(ctx).send_mail(self.id, force_send=True)
