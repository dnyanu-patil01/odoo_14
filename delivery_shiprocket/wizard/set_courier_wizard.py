from odoo import api, fields, models, _
from ..models.shiprocket_request import ShipRocket


class SetCourier(models.TransientModel):
    _name = "set.courier"
    _description = " Set Courier"

    selected_courier_id = fields.Many2one(
        "shiprocket.serviceability.matrix", "Select Courier ID"
    )
    picking_id = fields.Many2one("stock.picking", "Picking", invisible=True)

    def set_courier_in_picking(self):
        if self.picking_id and self.selected_courier_id:
            self.picking_id.write(
                {
                    "courier_id": self.selected_courier_id.courier_company_id.id,
                    "courier_rate": self.selected_courier_id.rate,
                }
            )
        if self.picking_id and self.env.context.get("reassign"):
            vals = {
                "courier_id": int(self.selected_courier_id.courier_company_id.code),
                "shipment_id": int(self.picking_id.shiprocket_shipping_id),
                "status": "reassign",
            }
            shiprocket = ShipRocket(self.env.company)
            # API Call To Reassign AWB
            response_data = shiprocket._create_awb(vals, self)
            if response_data:
                self.picking_id.write(response_data)
        return {"type": "ir.actions.act_window_close"}
