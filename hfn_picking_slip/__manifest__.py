# -*- coding: utf-8 -*-

{
    'name': 'Picking Slip Report',
    'version': '14.0',
    'sequence': 25,
    'summary': 'Picking Slip Report For Shiprocket',
    'description': 'Picking Slip Report For Shiprocket',
    'depends': ['delivery_shiprocket'],
    'data': [
             'security/ir.model.access.csv',
             'report/report_picking_slip.xml',
             'report/picking_slip_pdf.xml',
             'wizard/picking_slip_wizard.xml',
            ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
