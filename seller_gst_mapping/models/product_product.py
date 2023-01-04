# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date


class ProductChangeRequest(models.Model):
    _inherit = "product.change.request"

    seller_tax_id = fields.Many2one('seller.gst.mapping',string="Taxes")

    @api.model
    def create(self, values):
        if values.get('seller_tax_id'):
            seller_tax = self.env['seller.gst.mapping'].browse(values.get('seller_tax_id')).tax_ids.ids
            values['taxes_id'] = [(6,0,seller_tax)]
        return super(ProductChangeRequest, self).create(values)

    def write(self, values):
        if values.get('seller_tax_id'):
            seller_tax = self.env['seller.gst.mapping'].browse(values.get('seller_tax_id')).tax_ids.ids
            values['taxes_id'] = [(6,0,seller_tax)]
            if self.product_tmpl_id:
                self.product_tmpl_id.write({'seller_tax_id':values.get('seller_tax_id')})
        return super(ProductChangeRequest, self).write(values)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    seller_tax_id = fields.Many2one('seller.gst.mapping',string="Taxes")

    @api.model
    def create(self, values):
        if values.get('seller_tax_id'):
            seller_tax = self.env['seller.gst.mapping'].browse(values.get('seller_tax_id')).tax_ids.ids
            values['taxes_id'] = [(6,0,seller_tax)]
        return super(ProductTemplate, self).create(values)

    def write(self, values):
        if values.get('seller_tax_id'):
            seller_tax = self.env['seller.gst.mapping'].browse(values.get('seller_tax_id')).tax_ids.ids
            values['taxes_id'] = [(6,0,seller_tax)]
        return super(ProductTemplate, self).write(values)
    
    def prepare_change_request_vals(self):
        vals = super(ProductTemplate,self).prepare_change_request_vals()
        if self.seller_tax_id:
            vals.update({'seller_tax_id':self.seller_tax_id.id})
        return vals

class SellerGSTMapping(models.Model):
    _name = "seller.gst.mapping"
    _description = "Seller GST Mapping Table"

    name = fields.Char("Tax Name")
    tax_ids = fields.Many2many("account.tax",string="Taxes")