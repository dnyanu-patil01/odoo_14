from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    seller_id = fields.Many2one('res.partner','Seller', index=True, copy=False,domain="[('seller','=',True),('active','=',True),('parent_id','=',False)]")
    seller_shopify_sequence = fields.Char(readonly=True)
    mobile = fields.Char(related="partner_shipping_id.mobile",readonly=True) 
    phone = fields.Char(related="partner_shipping_id.phone",readonly=True)
    active = fields.Boolean('Active',default=True, help="If unchecked, it will allow you to hide the sale order without removing it.")


    @api.model
    def create(self, vals):
        if 'seller_id' in vals and vals['seller_id'] != False:
            seller_obj = self.env['res.partner'].browse(vals['seller_id'])
            if seller_obj.seller_sale_sequence_id:
                vals['name'] = seller_obj.seller_sale_sequence_id._next()
        return super(SaleOrder, self).create(vals)
        
    def _prepare_invoice(self):
        """This method used set seller info in customer invoice.
        """
        invoice_val = super(SaleOrder, self)._prepare_invoice()
        if self.seller_id:
            invoice_val.update({'seller_id': self.seller_id.id})
        if self.seller_id.seller_invoice_sequence_id:
            invoice_val.update({'name':self.seller_id.seller_invoice_sequence_id._next()})
        return invoice_val

    def action_view_seller_delivery(self):
        action = self.env["ir.actions.actions"]._for_xml_id("seller_management.seller_stock_transfer_action")
        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('seller_management.view_seller_stock_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        # Prepare the context.
        picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = pickings[0]
        action['context'] = dict(self._context, default_seller_id=self.seller_id.id, default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.name, default_group_id=picking_id.group_id.id)
        return action
    
    def action_view_seller_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("seller_management.action_sellers_invoices")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('seller_management.view_seller_invoice_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_seller_id': self.seller_id.id,
                'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.name,
            })
        action['context'] = context
        return action
    
    @api.onchange('partner_shipping_id', 'partner_id', 'company_id')
    def onchange_taxes_partner_shipping_id(self): 
        for order in self:
            for line in order.order_line:
                line.product_id_change()

    @api.onchange('partner_shipping_id', 'partner_id')
    def onchange_partner_shipping_id(self):
        res = super(SaleOrder, self).onchange_partner_shipping_id()
        for order in self:
            for line in order.order_line:
                line.product_id_change()
        return res

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    seller_id = fields.Many2one('res.partner','Seller', index=True, copy=False)

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id and self.product_id.seller_id:
            self.seller_id = self.product_id.seller_id.id
        return res

    #To Pass Seller To Stock Move
    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        if self.order_id.seller_id:
            res.update({'seller_id':self.order_id.seller_id.id})
        return res
