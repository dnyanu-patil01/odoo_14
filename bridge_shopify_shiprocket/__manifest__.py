{
    # App information
    'name': 'Bridge Between Shopify And Shiprocket',
    'version': '14.0',
    'category': 'Sales',
    'summary': 'Bridge Between Shopify And Shiprocket',
    'license': 'OPL-1',

    # Author
    'author': 'Leelapriskila',

    # Dependencies
    'depends': ['delivery_shiprocket','shopify_ept','seller_management','product_volume_weight','common_connector_library'],

    # Views
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'view/delivery_carrier_view.xml',
        'view/product_packaging.xml',
        'view/product_template_view.xml',
        "view/seller_delivery_order_view.xml",
        "view/seller_pickup_location.xml",
        "view/res_partner_view.xml",
        "view/sale_workflow_process_ept.xml",
        "wizard/update_delivery_carrier_view.xml",
    ],
}
