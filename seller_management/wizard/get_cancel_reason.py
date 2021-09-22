from odoo import api, fields, models, _

class CancelReason(models.TransientModel):
    _name = "cancel.reason"
    _description = "Cancel Reason"

    reason = fields.Text("Reason For Rejection", required=True)

    def update_cancel_reason(self):
        """ Get Rejection Reason"""
        product_ids = self.env.context.get('product_ids') or False
        if product_ids:
            product_records = self.env['product.template'].browse(product_ids)
            product_records.write({'rejection_reason':self.reason,'state':'reject'})
        return {"type": "ir.actions.act_window_close"}