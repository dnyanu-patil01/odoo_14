{
    "name": "Track Fields",
    "version": "14.0",
    "author": "Ajay Chinta & Hardik Shah",
    "category": "SRCM Modules",
    "website": "http://www.sahajmarg.org",
    "description": """
    Custom Modules for Shri Ram Chandra Mission

    This module has model mail.track.all which can be inherited along with
    mail.thread to provide tracking to all fields.

    e.g. _inherit = ['mail.track.all', 'mail.thread' ]

    Note the sequence is important.

    It also adds JSON values of tracked fields to mail.message for future reporting needs.

    """,
    'depends': ['mail'],
    'data':[
    ],
    'installable': True,
    'active': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: