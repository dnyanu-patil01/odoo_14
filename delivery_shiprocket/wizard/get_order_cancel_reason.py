from odoo import api, fields, models, _

class OrderCancelReason(models.TransientModel):
    _name = "order.cancel.reason"
    _description = "Order Cancel Reason"

    reason = fields.Text("Cancellation Reason", required=True)

    def update_cancel_reason(self):
        """ Get Order Cancellation Reason"""
        picking_ids = self.env.context.get('picking_ids') or False
        if picking_ids:
            picking_records = self.env['stock.picking'].browse(picking_ids)
            picking_records.with_delay().shiprocket_cancel_shipment()
            picking_records.write({'cancel_reason':self.reason})
        return {"type": "ir.actions.act_window_close"}