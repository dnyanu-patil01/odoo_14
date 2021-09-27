{
    "name": "Split And Group Delivery Order Based On Sellers",
    "version": "14.0.1.0.0",
    "category": "Delivery",
    "author": "Heartfulness ERP Team",
    "depends": ["seller_management","product","sale_stock"],
    "data": [
        'security/security.xml',
        "security/ir.model.access.csv",
        "views/seller_group_view.xml",
        "views/seller_view.xml",
            ],
    "installable": True,
}
