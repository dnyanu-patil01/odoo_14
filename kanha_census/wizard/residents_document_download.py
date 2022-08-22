from odoo import models, _, fields
from odoo.exceptions import MissingError
from werkzeug.urls import url_encode



class ResidentsDocumentDownload(models.TransientModel):
    _name = 'residents.document.download'
    _description = 'Residents Document Download'

    partner_ids = fields.Many2many('res.partner', 'res_partner_residents_document_download', string="Residents")

    def download_document(self):
        partner_ids = self.partner_ids.ids
        if partner_ids:
            self.env.cr.execute("""
                        SELECT id
                          FROM ir_attachment
                         WHERE res_id IN %s AND res_field IN 
                         ('adhar_card', 'adhar_card_back_side', 'age_proof', 'address_proof', 'kanha_voter_id_image','kanha_voter_id_back_image', 'declaration_form', 'passport_photo')
                    """, [tuple(partner_ids)])
            ir_attachments = self.env.cr.fetchall()
        else:
            raise MissingError(_("Please select the Residents."))
        
        if(ir_attachments):
            partner_ids = ",".join(map(str, partner_ids))
            return {
                'name': 'Download zip', 
                'type': 'ir.actions.act_url',
                'url': '/web/attachment/download_zip?partner_ids=%s' % (partner_ids),
                'target': 'self',
            }
        else:
            raise MissingError(_("Attachments does not exist."))
        