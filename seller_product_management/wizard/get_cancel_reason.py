from odoo import api, fields, models, _


class CancelReason(models.TransientModel):
    _name = "cancel.reason"
    _description = "Cancel Reason"

    reason = fields.Text("Reason For Rejection", required=True)

    def update_cancel_reason(self):
        """ Get Rejection Reason"""
        product_ids = self.env.context.get("product_ids") or False
        if product_ids:
            product_records = self.env["product.template"].browse(product_ids)
            product_records.write({"rejection_reason": self.reason, "state": "reject"})
        request_id = self.env.context.get("request_obj") or False
        print("---------------------")
        print(request_id)
        if request_id:
            req_obj = self.env["product.change.request"].browse(request_id)
            print(req_obj)
            req_obj.write({"state": "reject", "rejection_reason": self.reason})
            req_obj.product_tmpl_id.state = 'reject'
            action = {
                "name": req_obj.product_tmpl_id.name,
                "view_mode": "form",
                "res_model": "product.template",
                "view_id": self.env.ref(
                    "seller_management.view_seller_product_template_form"
                ).id,
                "type": "ir.actions.act_window",
                "res_id": req_obj.product_tmpl_id.id,
                "target": "main",
            }
            return action
