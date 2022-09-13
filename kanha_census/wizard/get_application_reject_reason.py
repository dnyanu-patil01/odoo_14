from odoo import api, fields, models, _


class ApplicationRejectionReason(models.TransientModel):
    _name = "application.reject.reason"
    _description = "Application Rejection Reason"

    reason = fields.Text("Reason For Rejection", required=True)

    def update_reason(self):
        """ Get Rejection Reason"""
        partner_ids = self.env.context.get("application_ids") or False
        if partner_ids:
            partner_records = self.env["res.partner"].browse(partner_ids)
            partner_records.write({"rejection_reason": self.reason, "application_status": "rejected"})
            partner_records.send_rejection_reason_in_mail()
        return True
