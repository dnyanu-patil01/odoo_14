# -*- coding: utf-8 -*-
{
    'name': "Document Preview",
    'summary': """Document Preview allows users to preview a document without downloading it.""",
    "category": "Tools",
    'license': 'LGPL-3',   
    'images': ['static/description/banners/banner1.gif'],
    'version': '14.0',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'views/preview_templates.xml',
    ],
    'qweb': ['static/src/xml/binary_preview.xml',
    ],
}
