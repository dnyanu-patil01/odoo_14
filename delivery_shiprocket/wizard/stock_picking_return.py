from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _create_returns(self):
        res = super(ReturnPicking, self)._create_returns()
        if self.picking_id.carrier_id.delivery_type == "shiprocket":
            new_picking_id, pick_type_id = res
            new_picking = self.env["stock.picking"].browse(new_picking_id)
            new_picking.write(
                {
                    "pickup_location": self.picking_id.pickup_location.id,
                    "channel_id": self.picking_id.channel_id.id,
                    "carrier_id": self.picking_id.carrier_id.id,
                }
            )
        return res
