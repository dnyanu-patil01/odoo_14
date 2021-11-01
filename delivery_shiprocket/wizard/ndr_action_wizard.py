from odoo import api, fields, models, _
from ..models.shiprocket_request import ShipRocket


class NDRActionWizard(models.TransientModel):
    _name = "ndr.action.wizard"
    _description = "To Get Data For NDR Action Call"

    action = fields.Selection([
        ('return', 'Return'),
        ('re-attempt', 'Re-Attempt')
    ], string='Action',required=True)
    comments = fields.Text("Comments",required=True)

    def action_ndr(self):
        shiprocket = ShipRocket(self.env.company)
        data={
            'action':str(self.action),
            'comments':str(self.comments)
        }
        picking_ids = self.env.context.get('picking_ids') or False
        if picking_ids:
            picking_records = self.env['stock.picking'].browse(picking_ids)
            for picking in picking_records:
                response_data = shiprocket._action_ndr(data,picking.shiprocket_awb_code)
                if response_data in (200,204):
                    picking.write({'response_comment':'NDR Action Taken Successfully!'})
                else:
                    picking.write(response_data)
        message_id = self.env['message.box'].create({'message':"NDR Action Response Updated Under Shiprocket Details Tab"})
        return {
            "name": "Information",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "message.box",
            "res_id": message_id.id,
            "target": "new",
        }

        
