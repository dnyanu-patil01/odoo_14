from odoo import api, fields, models, _


class ApplicationRejectionReason(models.TransientModel):
    _name = "order.cancel.reason"
    _description = "Order Cancellation Reason"

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
                order.action_cancel()
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
        return True
