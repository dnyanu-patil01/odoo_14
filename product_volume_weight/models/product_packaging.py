from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class ProductPackaging(models.Model):
    _name = "product.packaging"
    _inherit = ['mail.thread','product.packaging']
    
    #Redefined fields to change Int to Float
    height = fields.Float('Height',required=True)
    width = fields.Float('Breadth',required=True)
    packaging_length = fields.Float('Length',required=True)
    volumetric_weight = fields.Float(
        "Volumetric Weight",
        digits=(8, 3),
        compute="_compute_volumetric_weight",
        readonly=True,
        store=True,
        help="The Packaging volume",
    )

    @api.depends(
        "packaging_length", "width", "height"
    )
    def _compute_volumetric_weight(self):
        for pack in self:
            pack.volumetric_weight = self._calculate_volumetric_weight(
                pack.packaging_length,
                pack.height,
                pack.width
            )

    def _calculate_volumetric_weight(
        self, packaging_length, height, width
    ):
        volume = 0
        if packaging_length and height and width:
            volume = (packaging_length * height * width)/5000
        return volume
    
    def name_get(self):
        result = []
        for pack in self:
            if pack.packaging_length and pack.height and pack.width:
                name = pack.name+'-'+str(pack.packaging_length) + ' * ' + str(pack.width)+' * '+ str(pack.height)
            else:
                name = pack.name
            result.append((pack.id, name))
        return result

class ChooseDeliveryPackage(models.TransientModel):
    _inherit = 'choose.delivery.package'
    
    shipping_weight = fields.Float('Volumetric Weight',related="delivery_packaging_id.volumetric_weight",readonly=False)
    shipping_actual_weight = fields.Float('Actual Weight')

    def action_put_in_pack(self):
        picking_move_lines = self.picking_id.move_line_ids
        if not self.picking_id.picking_type_id.show_reserved and not self.env.context.get('barcode_view'):
            picking_move_lines = self.picking_id.move_line_nosuggest_ids

        move_line_ids = picking_move_lines.filtered(lambda ml:
            float_compare(ml.qty_done, 0.0, precision_rounding=ml.product_uom_id.rounding) > 0
            and not ml.result_package_id
        )
        if not move_line_ids:
            move_line_ids = picking_move_lines.filtered(lambda ml: float_compare(ml.product_uom_qty, 0.0,
                                 precision_rounding=ml.product_uom_id.rounding) > 0 and float_compare(ml.qty_done, 0.0,
                                 precision_rounding=ml.product_uom_id.rounding) == 0)\

        delivery_package = self.picking_id._put_in_pack(move_line_ids)
        # write shipping weight and product_packaging on 'stock_quant_package' if needed
        if self.delivery_packaging_id:
            delivery_package.packaging_id = self.delivery_packaging_id
        # shipping_weight = 0
        # for move in move_line_ids:
        #     if move.product_id.weight > move.product_id.volumetric_weight:
        #         shipping_weight+=move.product_id.weight * move.qty_done
        #     else:
        #         shipping_weight += move.product_id.volumetric_weight * move.qty_done
        # if self.shipping_weight:
        #     delivery_package.shipping_weight = self.shipping_weight + shipping_weight
        # else:
        #     delivery_package.shipping_weight = shipping_weight
        if self.shipping_weight > self.shipping_actual_weight:
            delivery_package.shipping_weight = self.shipping_weight
        else:
            delivery_package.shipping_weight = self.shipping_actual_weight



class StockPicking(models.Model):
    _inherit='stock.picking'

    #redefined to have digits
    shipping_weight = fields.Float("Weight for Shipping",digits=(8, 3), compute='_compute_shipping_weight',
            help="Total weight of packages and products not in a package. Packages with no shipping weight specified will default to their products' total weight. This is the weight used to compute the cost of the shipping.")
    shipping_actual_weight = fields.Float('Shipping Actual Weight',readonly=True)