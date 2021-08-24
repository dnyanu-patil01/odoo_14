from odoo import tools
from odoo import api, fields, models


class BulkOrderInvoiceReport(models.AbstractModel):
    _name = 'report.delivery_shiprocket.report_shiprocket_invoice'
    _description = 'Shiprocket Invoice Report'
    
    def get_invoice_ids(self,obj):
        invoice_lines = []
        for picking in obj.stock_picking_ids:
            if picking.sale_id:
                invoice_lines.extend(picking.sale_id.invoice_ids.filtered(lambda l : l.state == 'posted').ids)
        invoice_objects = self.env['account.move'].browse(list(set(invoice_lines)))
        return invoice_objects

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['shiprocket.bulk.process'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'shiprocket.bulk.process',
            'docs': docs,
            'invoice_lines':self.get_invoice_ids(docs)
        }