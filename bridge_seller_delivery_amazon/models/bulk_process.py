# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from odoo.exceptions import UserError, AccessError
from PyPDF2 import PdfFileMerger
import base64
from io import BytesIO

class BulkProcessInherit(models.Model):
    _inherit = "shiprocket.bulk.process"
    _order = "id desc"

    state = fields.Selection(selection_add=[('Document Generated', 'Document Generated')])
    amzn_state = fields.Selection(related='state')
    carrier_id = fields.Many2one('delivery.carrier')
    delivery_type = fields.Selection(related="carrier_id.delivery_type", string='Delivery Type')
    amzn_stock_picking_ids = fields.Many2many("stock.picking","amzn_stock_picking", "picking_id", "bulk_process_id", string="Delivery Orders",domain="[('pickup_location','=',pickup_location_id),('delivery_type','=','amazon_shipment'),('state','=','done'), ('is_shipment_purchased', '=', True)]")
    is_document_generated = fields.Boolean(string='Is Document Generated?')

    def _check_amzn_stock_picking_ids(self):
        for record in self:
            if not record.stock_picking_ids:
                raise UserError(('Please Select Atleast One Picking Line To Proceed'))

    def track_shipment(self):
        self._check_amzn_stock_picking_ids()
        for picking in self.amzn_stock_picking_ids:
            picking.amzn_tracking_shipment()

    def generate_amzn_shipment_document(self):
        self._check_amzn_stock_picking_ids()
        merged_pdf = PdfFileMerger()
        pickings = self.stock_picking_ids.filtered(lambda r: r.carrier_id.name == 'amazon')
        if not pickings:
            raise UserError(('No Amazon Pickings To Proceed'))
        else:
            for picking in pickings:
                picking.amzn_get_shipment_document()
                # Attach the PDF to the bulk process attachments
                pdf_attachment = self._attach_pdf_from_picking(picking)
                # Merge the PDF into the merged_pdf object
                pdf_content = base64.b64decode(pdf_attachment.datas)
                merged_pdf.append(fileobj=BytesIO(pdf_content))
                pdf_attachment.unlink()  # Remove the temporary PDF attachment
            # Write the merged PDF to a new attachment
            merged_pdf_bytes = BytesIO()
            merged_pdf.write(merged_pdf_bytes)
            merged_pdf_bytes.seek(0)
            merged_pdf_content = base64.b64encode(merged_pdf_bytes.getvalue())
            merged_pdf_bytes.close()
            self.env['ir.attachment'].create({
                'name': 'Amazon Label Document',
                'datas': merged_pdf_content,
                'res_model': "shiprocket.bulk.process",
                'res_id': self.id,
            })
            merged_pdf.close()  # Close the merged PDF object
            self.is_document_generated = True
            self.state = 'Document Generated'

    def _attach_pdf_from_picking(self, picking):
        if picking.barcode:
            attachment = self.env['ir.attachment'].create({
                'name': picking.name,
                'datas': picking.barcode,
                'res_model': "shiprocket.bulk.process",
                'res_id': self.id,
            })
            return attachment
