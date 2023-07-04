from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError


class ApplicationRejectionReason(models.TransientModel):
    _name = "sale.delivery.order.cancel.reason"
    _description = "SO / DO Cancellation Reason"

    reason = fields.Text("Reason For Cancellation", required=True)

    def update_cancel_reason(self):
        """ Get Cancellation Reason"""
        order_ids = self.env.context.get("order_ids") or False
        model_name = self.env.context.get("active_model") or False
        if order_ids and model_name == 'sale.order':
            for order in order_ids:
                order = self.env["sale.order"].browse(order)
                order.write({"cancellation_reason": self.reason, "cancel_reason_check": True})
                template = self.env.ref('seller_management.mail_template_seller_so_cancellation')
                if template:
                    mail_id = template.send_mail(order.id)
                    Mail = self.env['mail.mail'].sudo().browse(mail_id)
                    Mail.send()
                if len(order.picking_ids) > 1:
                    raise ValidationError('You cannot cancel this Sale Order.\n This Order has multiple Delivery Orders.')
                else:
                    order.picking_ids.write({"note": self.reason, "cancel_reason_check": True})
                    return order.action_cancel()

        if order_ids and model_name == 'stock.picking':
            for order in order_ids:
                order = self.env["stock.picking"].browse(order)
                order.write({"note": self.reason, "cancel_reason_check": True})
                template = self.env.ref('seller_management.mail_template_seller_do_cancellation')
                if template:
                    mail_id = template.send_mail(order.id)
                    Mail = self.env['mail.mail'].sudo().browse(mail_id)
                    Mail.send()
                order.action_cancel()
                sale_order = self.env["sale.order"].search([('name','=', order.origin)])
                sale_order.write({"cancellation_reason": self.reason, "cancel_reason_check": True})
                return sale_order.action_cancel()
        return True
