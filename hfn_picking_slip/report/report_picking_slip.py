# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class ReportPickingSlip(models.AbstractModel):
    _name = 'report.hfn_picking_slip.report_picking_slip'

    def get_products(self, docs,data):
        from_date = datetime.combine(datetime.strptime(data['start_date'],"%Y-%m-%d"), datetime.min.time())
        to_date = datetime.combine(datetime.strptime(data['end_date'],"%Y-%m-%d"), datetime.max.time())
        self.env.cr.execute(
            '''
            select product_id as product,sm.name as product_name,sum(product_uom_qty) as qty_to_be_delivered from stock_move sm
            join stock_picking sp on (sp.id = sm.picking_id) 
            where sm.state not in ('cancel','done') and 
            sp.scheduled_date between '%s' and '%s' and 
            product_uom_qty > 0 and
            sp.carrier_id in (select id from delivery_carrier where delivery_type = 'shiprocket') and 
            sm.location_dest_id in (select id from stock_location 
            where usage='customer') and sm.picking_type_id in (select id from stock_picking_type 
            where code='outgoing') GROUP BY product_id,sm.name
            '''%(from_date,to_date)
        )
        records = self.env.cr.dictfetchall()
        product_list = []
        for rec in records:
            product_obj = self.env['product.product'].browse(int(rec['product']))
            vals = {'product_name': product_obj.name,
                    'qty_to_be_delivered': rec['qty_to_be_delivered'],
                    'qty_available':product_obj.qty_available,
                    }
            product_list.append(vals)
        return product_list

    @api.model
    def _get_report_values(self, docids, data=None):
        """we are overwriting this function because we need to show values from other models in the report
        we pass the objects in the docargs dictionary"""
        docs = self.env['picking.slip.wizard'].browse(data['wizard_id'])
        return {
            'doc_ids': self.ids,
            'docs': docs,
            'products':self.get_products(docs,data),
            'start_date': datetime.strptime(data['start_date'],"%Y-%m-%d").strftime("%d-%b-%Y"),
            'end_date': datetime.strptime(data['end_date'],"%Y-%m-%d").strftime("%d-%b-%Y"),
        }
