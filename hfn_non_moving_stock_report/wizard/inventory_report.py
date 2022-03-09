from odoo import api, fields, models

try:
    import xlwt
except ImportError:
    xlwt = None
from io import BytesIO
import base64
from itertools import groupby, product
from operator import itemgetter
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class InventoryNonMovingStockReport(models.TransientModel):

    _name = "inventory.non.moving.stock.report"
    _description = "Inventory Non Moving Stock Report"

    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.user.company_id,
        help="You can select multiple companies, \
                                       if you are not selecting any company \
                                       than it will prepare result for \
                                       all companies",
    )
    start_date = fields.Date(
        "Start Date",
        help="Select Start date which is mandatory \
                                 field for period range",
    )
    end_date = fields.Date(
        "End Date",
        help="Select end date which is mandatory field \
                               for period range",
    )
    filedata = fields.Binary("Download file", readonly=True)
    filename = fields.Char("Filename", size=64, readonly=True)

    def _get_product_detail(self):
        product_obj = self.env["product.product"]
        final_data = []
        start_date = self.start_date
        end_date = self.end_date
        if start_date and end_date:
            cr = self._cr
            cr.execute(
                """
select product_id,sl.name as location,sum(quantity) as quantity from stock_quant sq
join stock_location sl on (sq.location_id = sl.id)
join product_product pp on (sq.product_id = pp.id)
where pp.active = 't' and sq.company_id = %s and product_id not in (
    SELECT distinct product_id FROM STOCK_MOVE 
    WHERE state = 'done' and 
    date::date >= %s and 
    date::date <= %s)
    and usage = 'internal' and  (quantity > 0 or quantity < 0)
    group by sq.product_id,sl.name
""",
                (self.company_id.id, start_date, end_date),
            )
            data_list = cr.dictfetchall()
            if data_list:
                for data in data_list:
                    product = product_obj.browse(data["product_id"])
                    final_data.append(
                        {
                            "product_name": product.name,
                            "product_id": product.id,
                            "default_code": product.default_code,
                            "barcode": product.barcode,
                            "location": data["location"],
                            "quantity": data["quantity"],
                        }
                    )
        return final_data


    def generate_worksheet(self, worksheet, sheet_headers,rows):
        header_style = xlwt.easyxf('font: bold on')
        style = xlwt.easyxf(num_format_str='#,##0.00')
        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'yyyymmdd'
        title="Non Moving Stock Report From %s To %s" %(self.start_date.strftime("%d-%b-%Y"),self.end_date.strftime("%d-%b-%Y"))
        worksheet.write_merge(0,0,0,8,title,header_style)
        for cell_index, head in enumerate(sheet_headers): 
            worksheet.write(2, cell_index, head, header_style)
        row_index = 2
        index=0
        product_data_list = self._get_product_detail()
        for data in product_data_list:
            line_index = row_index 
            line_index = line_index + 1
            worksheet.write(line_index , index , data.get('product_name'),style)
            worksheet.write(line_index , index + 1, data.get('default_code') or "",style)
            worksheet.write(line_index , index + 2, data.get('barcode') or "",style)
            worksheet.write(line_index , index + 3, data.get('location'),style)
            worksheet.write(line_index , index + 4, data.get('quantity'),style)
            row_index = line_index
        return 

    def generate_xlsx(self):
        rows=[]
        if not xlwt:
            raise Warning("Please Install XLWT")
        else:
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('Non Moving Stock-report')
            sheet_headers=['Product Name','Internal Referene','Barcode','Location','On Hand Qty']
            self.generate_worksheet(worksheet, sheet_headers,rows)
            fp = BytesIO()
            workbook.save(fp)
            fp.seek(0)
            out = base64.b64encode(fp.read())
            fp.close()
            title="Non Moving Stock Report From %s To %s.xls" %(self.start_date.strftime("%d-%b-%Y"),self.end_date.strftime("%d-%b-%Y"))
            self.write({'filedata': out, 'filename': title})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'inventory.non.moving.stock.report',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id'    : self.id,
                'target': 'new',
            }


class StockMove(models.Model):
    _inherit = 'stock.move'                   
    
    @api.model
    def cron_send_nonmoving_stock_report(self):
        company_list = self.env['res.company'].search([]) 
        for company in company_list:
            get_no_of_months = "non_moving_stock_periods_in_month_"+str(company.id)
            no_of_month = self.env["ir.config_parameter"].sudo().get_param(get_no_of_months)
            end_date = datetime.today().date()
            start_date = end_date + relativedelta(months=-int(no_of_month))
            values={'company_id': company.id,
                    'start_date':start_date.strftime("%Y-%m-%d"),
                    'end_date':end_date.strftime("%Y-%m-%d")
                    }

            report_obj = self.env['inventory.non.moving.stock.report'].create(values)
            report_obj.generate_xlsx()
            subject = str(company.name) +' Non Moving Stock Report for '+str(start_date.strftime('%d-%b-%Y')) +' To '+str(end_date.strftime('%d-%b-%Y'))
            attach_id=self.env['ir.attachment'].create({
                                            'name': subject,
                                            'datas': report_obj.filedata,
                                            'res_model': 'inventory.non.moving.stock.report',
                                            'res_id': report_obj.id,
                                            'mimetype': 'application/octet-stream',
                                            })
            ctx = dict(self.env.context)
            ctx['subject'] = subject
            ctx['start_date'] = str(start_date.strftime('%d-%b-%Y'))
            ctx['end_date'] = str(end_date.strftime('%d-%b-%Y'))
            get_email_receipients = "non_moving_stock_email_recipients_"+str(company.id)
            ctx['email_to'] = self.env["ir.config_parameter"].sudo().get_param(get_email_receipients)
            ctx['email_from'] = company.email
            template = self.env.ref('hfn_non_moving_stock_report.mail_template_non_moving_stock')
            if template:
                mail_id = template.with_context(ctx).send_mail(self.id)
                Mail = self.env['mail.mail'].browse(mail_id)
                Mail.write({'attachment_ids': [(6, 0, attach_id.ids)]})
                Mail.send()
        return True
            

