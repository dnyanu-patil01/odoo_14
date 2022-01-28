# -*- coding: utf-8 -*-
{
    "name": "Non Moving Report",
    "version": "14.0.0.1.0",
    "author": "leelapriskila",
    'license': 'AGPL-3',
    'depends': ['stock'],
    'summary': "Get Non Moving Stock Report In Excel",
    'category': 'stock',
    "description": """
    Inventory ---> Reporting ---> Non Moving Stock Report
    """,
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'data/ir_config.xml',
        'wizard/inventory_report_view.xml',
    ]
}
