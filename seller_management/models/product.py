from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ['product.template','mail.thread']

    seller_id = fields.Many2one("res.partner",'Seller',index=True, copy=False,default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id.seller else False,domain="[('seller','=',True),('active','=',True),('parent_id','=',False)]")
    # state = fields.Selection([('draft','Draft'),('to_approve','Waiting For Approval'),('approve','Approved'),('reject','Rejected')],string='State',default='draft',copy=False)
    rejection_reason = fields.Text('Reason For Rejection')
    #added to make storable type as default
    type = fields.Selection(selection_add=[],default="product")
    product_price_line = fields.One2many("product.pricelist.item","product_tmpl_id","Prices")

    # def button_approve(self):
    #     return self.write({'state': 'approve'})

    def button_reject(self):
        product_ids = self.env.context.get('active_ids') or False
        if not product_ids:
            ctx = {"product_ids": self.id}
        else:
            ctx = {"product_ids": product_ids}
        return {
            "name": ("Reject Product Details Updates"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "cancel.reason",
            "target": "new",
            "context":ctx,
        }

    # def button_draft(self):
    #     return self.write({'state': 'draft'})
    
    # def button_submit(self):
    #     return self.write({'state':'to_approve'})
    
    # To Show Update Quantity Wizard Instead Of Direct Change in QTY
    def seller_update_stock_quantity(self):
        default_product_id = self.env.context.get('default_product_id', len(self.product_variant_ids) == 1 and self.product_variant_id.id)
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_change_product_quantity")
        action['context'] = dict(
            self.env.context,
            default_product_id=default_product_id,
            default_product_tmpl_id=self.id,
            seller_update = True
        )
        return action
    
    def open_seller_pricelist_rules(self):
        self.ensure_one()
        domain = ['|',
            ('product_tmpl_id', '=', self.id),
            ('product_id', 'in', self.product_variant_ids.ids)]
        return {
            'name': ('Price'),
            'view_mode': 'tree',
            'views': [(self.env.ref('seller_management.seller_product_pricelist_item_tree_view_from_product').id, 'tree'), (self.env.ref('seller_management.seller_product_pricelist_item_form_view').id, 'form')],
            'res_model': 'product.pricelist.item',
            'type': 'ir.actions.act_window',
            'target': 'current',
            # 'flags': {'tree_view_initial_mode': 'view'},
            'domain': domain,
            'context': {
                'default_product_tmpl_id': self.id,
                'default_applied_on': '1_product',
                'product_without_variants': self.product_variant_count == 1,
                'form_view_initial_mode':'view',
            },
        }
    
    # def write(self, vals):
    #     """
    #     This method use to restrict adding new attribute to variants in templates.
    #     :parameter: self, vals
    #     """
    #     if 'attribute_line_ids' in vals.keys():
    #         attribute_line_string = str(vals['attribute_line_ids'])
    #         if 'attribute_id' in attribute_line_string:
    #             message = "Please Contact Administrator To Add New Attribute To The Product : %s"%(self.name)
    #             raise UserError(message)
    #     return super(ProductTemplate, self).write(vals)

    @api.model
    def create(self, vals):
        """
        This method is to make product price '0' if the product has variants
        """
        if 'attribute_line_ids' in vals.keys():
            vals['list_price'] = 0
        return super(ProductTemplate, self).create(vals)

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _is_inventory_mode(self):
        if self.user_has_groups('seller_management.group_sellers_management_user'):
            return True
        else:
            return self.env.context.get('inventory_mode') is True and self.user_has_groups('stock.group_stock_manager')

class ProdductProduct(models.Model):
    _name = "product.product"
    _inherit = ['product.product','mail.thread']

    seller_id = fields.Many2one(related="product_tmpl_id.seller_id", readonly=False,store=True, index=True, copy=False,domain="[('seller','=',True),('active','=',True),('parent_id','=',False)]")
    # state = fields.Selection(related='product_tmpl_id.state', store=True, readonly=False,copy=False)
