from odoo import _, api, fields, models

class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    #Overide To Fetch Taxes Based On Seller
    def map_tax(self, taxes, product=None, partner=None):
        result = super(AccountFiscalPosition,self).map_tax(taxes)
        seller_state_id = False
        partner_state_id = False
        company_state_id = self.env.user.company_id.state_id
        if product and product.seller_id:
            seller_state_id = self.get_seller_state(product.seller_id)
        if partner:
            partner_state_id = partner.state_id
        if partner_state_id:
            result = self.get_correspond_tax(taxes,partner_state_id,seller_state_id,company_state_id)
        return result

    def get_seller_state(self,seller):
        if seller and seller.state_id:
            return seller.state_id
        else:
            return False
            
    def get_correspond_tax(self,taxes,partner_state,seller_state,company_state):
        if seller_state:
            if seller_state.id == partner_state.id:
                return taxes.filtered(lambda t:t.gst_type in ('intra','none'))
            else:
                return taxes.filtered(lambda t:t.gst_type in ('inter','none'))
        elif company_state:
            if company_state.id == partner_state.id:
                return taxes.filtered(lambda t:t.gst_type in ('intra','none'))
            else:
                return taxes.filtered(lambda t:t.gst_type in ('inter','none'))
        else:
            return taxes

class AccountTax(models.Model):
    _name = 'account.tax'
    _inherit = ["mail.thread","account.tax"]
    gst_type = fields.Selection([
                                ('intra','Intrastate Supply'),
                                ('inter','Interstate Supply'),
                                ('none','Non-GST')],
                                required=True,
                                ondelete={
                                    'inter':'set null',
                                    'intra':'set null',
                                    'none':'set null',
                                },
                                string="Applicable Between")

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_computed_taxes(self):
        taxes = super(AccountMoveLine,self)._get_computed_taxes()
        fpos = self.env['account.fiscal.position']
        seller_state_id = False
        partner_state_id = False
        company_state_id = self.env.user.company_id.state_id
        if self.product_id and self.product_id.seller_id:
            seller_state_id = self.product_id.seller_id.state_id
        if self.partner_id:
            partner_state_id = self.partner_id.state_id
        if partner_state_id:
            result = fpos.get_correspond_tax(taxes,partner_state_id,seller_state_id,company_state_id)
            if result:
                return result
        return taxes
    
class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('partner_shipping_id', 'partner_id', 'company_id')
    def onchange_taxes_partner_shipping_id(self): 
        for move in self:
            for line in move.invoice_line_ids:
                line._onchange_product_id()
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountMove,self)._onchange_partner_id()
        for move in self:
            for line in move.invoice_line_ids:
                line._onchange_product_id()
        return res