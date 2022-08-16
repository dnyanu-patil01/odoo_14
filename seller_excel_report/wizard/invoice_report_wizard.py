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


class InvoiceExcelReport(models.TransientModel):
    _name = 'invoice.excel.report'
    _description = 'Invoice Excel Report'

    def get_sellers(self):
        if self.user_has_groups('seller_management.group_sellers_management_manager'):
            return self.env['res.partner'].search([('seller','=',True),('active','=',True),('parent_id','=',False)]).ids
        else:
            return self.env.user.partner_id.ids
    
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True) 
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
        orders = self.env['account.move'].search([
            ('invoice_date', '>=', self.start_date),
            ('invoice_date', '<=', self.end_date),
            ('seller_id','in',self.seller_ids.ids)
            ],order="invoice_date asc")
        order_data = []
        for order in orders:  
            lines=[]
            for line in order.invoice_line_ids:
                lines.append({
                    'product':line.product_id.name,
                    'quantity':line.quantity,
                    'price_unit':line.price_unit,
                    'uom':line.product_uom_id.name,
                    'price_subtotal':line.price_subtotal,
                    'price_tax':line.price_total - line.price_subtotal,
                    'total':line.price_total,
                    'taxes':line.tax_ids.mapped('name')
                })
            order_data.append({
                'name':order.name,
                'customer':order.partner_id.name,
                'invoice_date':order.invoice_date,
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
        for rec in rows:
            row_index = row_index + 1
            for cell_index, head in enumerate(sheet_headers+line_headers): 
                worksheet.write(row_index, cell_index, head, header_style)
            print(rec)
            row_index = row_index + 1
            worksheet.write(row_index , index , rec.get('invoice_date').strftime("%d-%m-%Y") if rec.get('invoice_date') else None,date_format)
            worksheet.write(row_index , index + 1, rec.get('name'),style)
            worksheet.write(row_index , index + 2, rec.get('customer'),style)
            # for cell_index, head in enumerate(line_headers): 
            #     worksheet.write(row_index, cell_index, head, header_style)
            for line in rec.get('lines'):
                worksheet.write(row_index , index+3, line.get('product'),style)
                worksheet.write(row_index , index + 4, line.get('quantity'),style)
                worksheet.write(row_index , index + 5, line.get('uom'),style)
                worksheet.write(row_index , index + 6, line.get('price_unit'),style)
                worksheet.write(row_index , index + 7, line.get('taxes'))
                worksheet.write(row_index , index + 8, line.get('total'),style)
                row_index = row_index + 1
            worksheet.write(row_index,index + 5,'Invoice Total',header_style)
            worksheet.write(row_index,index + 6,rec.get('amount_untaxed'),style)
            worksheet.write(row_index,index + 7,rec.get('amount_tax'),style)
            worksheet.write(row_index,index + 8,rec.get('amount_total'),style)
            row_index = row_index + 1
        return
    
    def generate_xlsx(self):
        data = {'date_start': self.start_date, 'date_stop': self.end_date}
        rows=[]
        if not xlwt:
            raise Warning("Please Install XLWT")
        else:
            rec=self.get_sale_details(date_start=self.start_date, date_stop=self.end_date)
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('invoice-report')
            sheet_headers=['Date','Invoice Ref','Customer']
            line_headers = ['Product','Quantity','UoM','Price','Taxes','Total']
            self.generate_worksheet(worksheet, sheet_headers, line_headers,rec)
            fp = BytesIO()
            workbook.save(fp)
            fp.seek(0)
            out = base64.b64encode(fp.read())
            fp.close()
            self.write({'filedata': out, 'filename': 'invoice_report.xls'})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'invoice.excel.report',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id'    : self.id,
                'target': 'new',
            }