from odoo import fields, models


class ResidentsDocumentsDownloadsHistory(models.Model):
    _name = "residents.documents.downloads.history"
    _description = "Residents Documents Downloads History"
    _rec_name="downloaded_by"
    
    downloaded_by = fields.Many2one('res.users',string="Downloaded By", readonly=True)
    downloaded_datetime = fields.Datetime(string='Downloaded Date time', readonly=True)
    partner_ids = fields.One2many('res.partner', 'residents_documents_downloads_history_id', string="Partners", readonly=True)
    