# -*- coding: utf-8 -*-
from odoo import models, fields

class PickingSlipWizard(models.TransientModel):
    _name = 'picking.slip.wizard'
    _description="Wizard To Print Picking Slip"

    start_date = fields.Date('Start Date',required=True)
    end_date = fields.Date('End Date',required=True)

    def print_pickup_slip(self):
        data={
            'wizard_id':self.id,
            'start_date':self.start_date,
            'end_date':self.end_date,
        }
        return self.env.ref('hfn_picking_slip.action_report_picking_slip').report_action(self, data=data)

