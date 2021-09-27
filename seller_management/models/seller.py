from odoo import _, api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    seller = fields.Boolean("Seller")
    seller_code = fields.Char("Seller Code",size=5)
    fulfilment_type = fields.Selection([
        ('self_fulfilment', 'Self Fulfilment'),
        ('shiprocket','By Shiprocket'),
    ], string='Fulfilment Type')
    seller_sale_sequence_id = fields.Many2one('ir.sequence', string='Order Sequence',
        help="This sequence is automatically created by Odoo but you can change it "
        "to customize the reference numbers of your orders.", copy=False)
    seller_invoice_sequence_id = fields.Many2one('ir.sequence', string='Invoice Sequence', 
        help="This sequence is automatically created by Odoo but you can change it "
        "to customize the reference numbers of your orders.", copy=False)
    auto_approve_product = fields.Boolean("Auto Approve Product")
    location_line = fields.One2many('stock.location','seller_id',"Stock Location")
    seller_sale_order_count = fields.Integer(compute='_compute_seller_sale_order_count', string='Seller Order Count')
    seller_sale_order_ids = fields.One2many('sale.order', 'seller_id', 'Sellers Order')
    seller_invoice_count = fields.Integer(compute='_compute_seller_invoice_count', string='Seller Invoice Count')
    seller_product_count = fields.Integer(compute='_compute_seller_product_count', string='Seller Product Count')
    seller_signature_image = fields.Binary(string='Seller Signature')
    
    _sql_constraints = [
        ("seller_code_uniq", "unique(seller_code)", "Seller Code Must Be Unique")
    ]
    
    def _compute_seller_sale_order_count(self):
        # retrieve all children all_sellers and prefetch 'parent_id' on them
        all_sellers = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_sellers.read(['parent_id'])

        seller_sale_order_groups = self.env['sale.order'].read_group(
            domain=[('seller_id', 'in', all_sellers.ids)],
            fields=['seller_id'], groupby=['seller_id']
        )
        sellers = self.browse()
        for group in seller_sale_order_groups:
            seller = self.browse(group['seller_id'][0])
            while seller:
                if seller in self:
                    seller.seller_sale_order_count += group['seller_id_count']
                    sellers |= seller
                seller = seller.parent_id
        (self - sellers).seller_sale_order_count = 0

    def action_view_seller_orders(self):
        action = self.env["ir.actions.actions"]._for_xml_id("seller_management.seller_sale_order_action")
        action['context'] = {
            'default_seller_id':self.id,
        }
        action['domain'] = [('seller_id', 'child_of', self.id)]
        return action

    def _compute_seller_invoice_count(self):
        # retrieve all children all_sellers and prefetch 'parent_id' on them
        all_sellers = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_sellers.read(['parent_id'])

        seller_sale_order_groups = self.env['account.move'].read_group(
            domain=[('seller_id', 'in', all_sellers.ids),
                    ('move_type', 'in', ('out_invoice', 'out_refund'))],
            fields=['seller_id'], groupby=['seller_id']
        )
        sellers = self.browse()
        for group in seller_sale_order_groups:
            seller = self.browse(group['seller_id'][0])
            while seller:
                if seller in self:
                    seller.seller_invoice_count += group['seller_id_count']
                    sellers |= seller
                seller = seller.parent_id
        (self - sellers).seller_invoice_count = 0

    def action_view_seller_invoices(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("seller_management.action_sellers_invoices")
        action['domain'] = [
            ('move_type', 'in', ('out_invoice', 'out_refund')),
            ('seller_id', 'child_of', self.id),
        ]
        action['context'] = {'default_move_type':'out_invoice', 'move_type':'out_invoice', 'journal_type': 'sale', 'search_default_unpaid': 1}
        return action

    def _compute_seller_product_count(self):
        # retrieve all children all_sellers and prefetch 'parent_id' on them
        all_sellers = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_sellers.read(['parent_id'])

        seller_product_groups = self.env['product.template'].read_group(
            domain=[('seller_id', 'in', all_sellers.ids),
                    ('active', '=', True)],
            fields=['seller_id'], groupby=['seller_id']
        )
        sellers = self.browse()
        for group in seller_product_groups:
            seller = self.browse(group['seller_id'][0])
            while seller:
                if seller in self:
                    seller.seller_product_count += group['seller_id_count']
                    sellers |= seller
                seller = seller.parent_id
        (self - sellers).seller_product_count = 0

    def action_view_seller_product(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("seller_management.seller_product_view_action")
        action['domain'] = [
            ('active', '=', True),
            ('seller_id', 'child_of', self.id),
        ]
        action['context'] = {'default_seller_id':self.id}
        return action