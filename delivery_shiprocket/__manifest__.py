{
    "name": """Delivery Shiprocket""",
    "summary": """Delivery Shiprocket""",
    "category": "Operations/Inventory/Delivery",
    "version": "14.0.0",
    "application": False,

    "author": "Heartfulness Team",
    "depends": [
        'delivery','stock','queue_job'
    ],
    "data": [
        "data/mail_template_data.xml",
        "data/ir_config.xml",
        "data/ir_cron.xml",
        "data/shiprocket.courier.csv",
        "data/shiprocket.order.status.csv",
        "security/ir.model.access.csv",
        "wizard/message_box_views.xml",
        "wizard/set_courier_wizard_views.xml",
        "wizard/barcodes_read_views.xml",
        "views/company_views.xml",
        "views/shiprocket_views.xml",
        "views/delivery_shiprocket_views.xml",
        "views/stock_location_views.xml",
        "views/stock_picking_views.xml",
        "views/res_partner_views.xml",
        "views/shiprocket_bulk_process_views.xml",
        "report/pickup_slip_reports.xml",
        "report/pickup_slip_templates.xml",
    ],

    "auto_install": False,
    "installable": True,
}
