from odoo import _, api, fields, models

class SellerReportLog(models.Model):
    _name = "seller.report.log"
    _description = "Seller Report Log"

    name = fields.Char('Name')
    report_type = fields.Selection([('sale','Sales Excel Report'),('invoice','Invoice Excel Report')])
    seller_id = fields.Many2one('res.partner','Seller')
    report_taken_at = fields.Datetime('Report Taken At')
    user_id = fields.Many2one('res.users','Report Taken By')
    