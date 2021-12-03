# -*- coding: utf-8 -*-
from odoo import models, fields

class PickingSlipWizard(models.TransientModel):
    _name = 'picking.slip.wizard'
    _description="Wizard To Print Picking Slip"

    def print_pickup_slip(self):
        data={
            'wizard_id':self.id
        }
        return self.env.ref('hfn_picking_slip.action_report_picking_slip').report_action(self, data=data)

