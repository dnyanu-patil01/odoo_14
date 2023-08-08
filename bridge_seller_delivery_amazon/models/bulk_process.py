# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from odoo.exceptions import UserError, AccessError

class BulkProcessInherit(models.Model):
    _inherit = "shiprocket.bulk.process"
    _order = "id desc"

    state = fields.Selection(selection_add=[('Document Generated', 'Document Generated')])
    amzn_state = fields.Selection(related='state')
    carrier_id = fields.Many2one('delivery.carrier')
    delivery_type = fields.Selection(related="carrier_id.delivery_type", string='Delivery Type')
    amzn_stock_picking_ids = fields.Many2many("stock.picking","amzn_stock_picking", "picking_id", "bulk_process_id", string="Delivery Orders",domain="[('pickup_location','=',pickup_location_id),('delivery_type','=','amazon_shipment'),('state','=','done'), ('is_shipment_purchased', '=', True)]")
    is_document_generated = fields.Boolean(string='Is Document Generated?')

    @api.onchange('carrier_id')
    def check_carrier_delivery_type(self):
        if self.carrier_id.delivery_type == 'amazon_shipment':
            self.channel_id = None
            self.shiprocket_courier_priority = None

    def _check_amzn_stock_picking_ids(self):
        for record in self:
            if record.delivery_type == 'amazon_shipment'and not record.amzn_stock_picking_ids:
                raise UserError(('Please Select Atleast One Picking Line To Proceed'))

    def generate_amzn_shipment_document(self):
        self._check_amzn_stock_picking_ids()
        for picking in self.amzn_stock_picking_ids:
            picking.amzn_get_shipment_document()
        self.is_document_generated = True
        self.state = 'Document Generated'

    def track_shipment(self):
        self._check_amzn_stock_picking_ids()
        for picking in self.amzn_stock_picking_ids:
            picking.amzn_tracking_shipment()