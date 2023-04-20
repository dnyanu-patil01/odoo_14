# -*- coding: utf-8 -*-


from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import logging
from datetime import timedelta
from datetime import datetime
import json
import pytz
from io import StringIO,BytesIO
import base64
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools import date_utils
try:
    import xlwt
except ImportError:
    xlwt = None


class SaleExcelReport(models.TransientModel):
    _name = 'sales.excel.report'
    _description = 'Sales Excel Report'
    
    def _default_start_date(self):
        user_tz = pytz.timezone('Asia/Kolkata')
        hour_from=datetime.strptime("00:00:00","%H:%M:%S").time()
        from_date=user_tz.localize(datetime.combine(fields.Datetime.now().date(), hour_from)).astimezone(pytz.UTC).replace(tzinfo=None)
        return from_date

    def _default_end_date(self):
        user_tz = pytz.timezone('Asia/Kolkata')
        hour_from=datetime.strptime("23:00:00","%H:%M:%S").time()
        to_date=user_tz.localize(datetime.combine(fields.Datetime.now().date(), hour_from)).astimezone(pytz.UTC).replace(tzinfo=None)
        return to_date
    
    def get_sellers(self):
        if self.user_has_groups('seller_management.group_sellers_management_manager'):
            return self.env['res.partner'].search([('seller','=',True),('active','=',True),('parent_id','=',False)]).ids
        else:
            return self.env.user.partner_id.ids


    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True) 
    filedata = fields.Binary('File', readonly=True)
    filename = fields.Char('Filename', readonly=True)
    seller_ids = fields.Many2many('res.partner',default=get_sellers,domain="[('seller','=',True),('active','=',True),('parent_id','=',False)]")
    
    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, configs=False):
        """ Serialise the orders of the day information

        params: date_start, date_stop string representing the datetime of order
        """
        orders = self.env['sale.order'].search([
            ('date_order', '>=', self.start_date),
            ('date_order', '<=', self.end_date),
            ('seller_id','in',self.seller_ids.ids)
            ],order="date_order asc")
        order_data = []
        for order in orders:  
            lines=[]
            for line in order.order_line:
                props = []
                for prop in line.shopify_custom_field_ids:
                    props.append({
                        'property_name':prop.property_name,
                        'property_value':prop.property_value,
                    })

                lines.append({
                    'product':line.product_id.name,
                    'quantity':line.product_uom_qty,
                    'qty_delivered':line.qty_delivered,
                    'qty_invoiced':line.qty_invoiced,
                    'uom':line.product_uom.name,
                    'price_unit':line.price_unit,
                    'price_total':line.price_total,
                    'price_tax':line.price_tax,
                    'taxes':line.tax_id.mapped('name'),
                    'props': props,
                })
            order_data.append({
                'order_reference':order.name,
                'customer':order.partner_id.name,
                'date_ordered':order.date_order,
                'amount_untaxed':order.amount_untaxed,
                'amount_tax':order.amount_tax,
                'amount_total':order.amount_total,
                'lines':lines})
        return order_data

           
    def generate_worksheet(self, worksheet, sheet_headers, line_headers, rows):
        header_style = xlwt.easyxf('font: bold on')
        title_style = xlwt.easyxf('font: bold on,height 280;align: wrap on,vert centre, horiz center;')
        style = xlwt.easyxf(num_format_str='#,##0.00')
        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'dd-mm-yyyy'
        title="Sales Report From %s To %s" %(self.start_date.strftime("%d-%b-%Y"),self.end_date.strftime("%d-%b-%Y"))
        worksheet.write_merge(0,1,0,9,title,title_style)
        row_index = 3
        index=0
        for cell_index, head in enumerate(sheet_headers+line_headers): 
                worksheet.write(row_index, cell_index, head, header_style)
        for rec in rows:
            row_index = row_index + 1
            worksheet.write(row_index , index , rec.get('date_ordered').strftime("%d-%m-%Y %H:%M:%S") if rec.get('date_ordered') else None,date_format)
            worksheet.write(row_index , index + 1, rec.get('order_reference'),style)
            worksheet.write(row_index , index + 2, rec.get('customer'),style)
            # for cell_index, head in enumerate(line_headers): 
            #     worksheet.write(row_index, cell_index, head, header_style)
            for line in rec.get('lines'):
                worksheet.write(row_index , index+3, line.get('product'),style)
                worksheet.write(row_index , index + 4, line.get('quantity'),style)
                worksheet.write(row_index , index + 5, line.get('qty_delivered'),style)
                worksheet.write(row_index , index + 6, line.get('qty_invoiced'),style)
                worksheet.write(row_index , index + 7, line.get('price_unit'),style)
                worksheet.write(row_index , index + 8, line.get('taxes'),style)
                worksheet.write(row_index , index + 9, line.get('price_total'),style)
                if line.get('props'):
                    props_row = row_index
                    for ind , prop in enumerate(line.get('props')):
                        props_row = props_row + 1
                        worksheet.write(props_row,index,prop.get('property_name'),style)
                        worksheet.write(props_row,index + 1,prop.get('property_value'),style) 
                    row_index = props_row
                row_index = row_index + 1
            # worksheet.write(row_index,index + 6,'Order Total',header_style)
            # worksheet.write(row_index,index + 7,rec.get('amount_untaxed'),style)
            # worksheet.write(row_index,index + 8,rec.get('amount_tax'),style)
            # worksheet.write(row_index,index + 9,rec.get('amount_total'),style)
            # row_index = row_index + 1
        return
    
    def generate_xlsx(self):
        data = {'date_start': self.start_date, 'date_stop': self.end_date}
        rows=[]
        if not xlwt:
            raise Warning("Please Install XLWT")
        else:
            rec=self.get_sale_details(date_start=self.start_date, date_stop=self.end_date)
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('sale-report')
            sheet_headers=['Date','Order ID','Customer']
            line_headers = ['Product','Order Qty','Delivered Qty','Invoiced Qty','Unit Price','Taxes','Total']
            self.generate_worksheet(worksheet, sheet_headers, line_headers,rec)
            fp = BytesIO()
            workbook.save(fp)
            fp.seek(0)
            out = base64.b64encode(fp.read())
            fp.close()
            self.write({'filedata': out, 'filename': 'sales_report.xls'})
            self.create_log()
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sales.excel.report',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id'    : self.id,
                'target': 'new',
            }


    def create_log(self):
        self.env['seller.report.log'].create({
            'name':'Report Log on '+ datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            'report_type':'sale',
            'user_id': self.env.user.id,
            'report_taken_at':datetime.now(),
            'seller_id': self.env.user.partner_id.id if not self.user_has_groups('seller_management.group_sellers_management_manager') else False,
        })
        return True