from email.policy import default
from itertools import product
from odoo import _, api, fields, models
import json

fields_name = {
    "name": "Name",
    "description": "Description",
    "description_sale": "Sales Description",
    "list_price": "Sales Price",
    "taxes_id": "Customer Tax",
    "l10n_in_hsn_code": "HSN/SAC Code",
    "l10n_in_hsn_description": "HSN/SAC Description",
    "variant_change_request_line": "Variants",
}


class ProductChangeRequest(models.Model):
    _name = "product.change.request"
    _inherit = ["mail.thread"]
    _description = "Product Change Request"

    name = fields.Char("Name", index=True, required=True)
    description = fields.Text("Description", translate=True)
    description_sale = fields.Text(
        "Sales Description",
        translate=True,
        help="A description of the Product that you want to communicate to your customers. "
        "This description will be copied to every Sales Order, Delivery Order and Customer Invoice/Credit Note",
    )
    list_price = fields.Float(
        "Sales Price",
        default=1.0,
        digits="Product Price",
        help="Price at which the product is sold to customers.",
    )
    taxes_id = fields.Many2many(
        "account.tax",
        "product_request_taxes_rel",
        "prod_id",
        "tax_id",
        help="Default taxes used when selling the product.",
        string="Customer Taxes",
        default=lambda self: self.env.company.account_sale_tax_id,
    )
    l10n_in_hsn_code = fields.Char(
        string="HSN/SAC Code",
        help="Harmonized System Nomenclature/Services Accounting Code",
    )
    l10n_in_hsn_description = fields.Char(
        string="HSN/SAC Description",
        help="HSN/SAC description is required if HSN/SAC code is not provided.",
    )
    changes_text = fields.Text()
    variant_changes_text = fields.Text()
    product_tmpl_id = fields.Many2one("product.template")
    rejection_reason = fields.Text("Reason For Rejection")
    active = fields.Boolean()
    state = fields.Selection(
        [("draft", "Draft"), ("approve", "Approved"), ("reject", "Rejected")],
        string="State",
        default="draft",
        copy=False,
    )
    change_request_note = fields.Html()
    is_variants = fields.Boolean()
    variant_change_request_line = fields.One2many(
        "variant.change.request", "change_request_id"
    )

    def button_approve(self):
        if self.product_tmpl_id:
            changes_dict = json.loads(self.changes_text)
            for field in fields_name:
                if (
                    field in changes_dict.keys()
                    and field != "variant_change_request_line"
                ):
                    self.product_tmpl_id.write({field: changes_dict.get(field)})
            self.approve_variant_change()
            self.product_tmpl_id.write({"state": "approve"})
            self.write({"state": "approve", "active": False})
            action = {
                "name": self.product_tmpl_id.name,
                "view_mode": "form",
                "res_model": "product.template",
                "view_id": self.env.ref(
                    "seller_management.view_seller_product_template_form"
                ).id,
                "type": "ir.actions.act_window",
                "res_id": self.product_tmpl_id.id,
                "target": "main",
            }
            return action

    def approve_variant_change(self):
        variant_changes_dict = json.loads(self.variant_changes_text)
        for key, value in variant_changes_dict.items():
            product = self.env["product.product"].browse(int(key))
            for field_name, field_value in value.items():
                if field_name == "lst_price":
                    pricelist = self.env["product.pricelist.item"].search(
                        [
                            ("product_tmpl_id", "=", self.product_tmpl_id.id),
                            ("product_id", "=", product.id),
                        ]
                    )
                    if pricelist:
                        pricelist.write({"fixed_price": float(field_value)})
                    else:
                        pricelist = self.env["product.pricelist"].search([], limit=1)
                        if pricelist:
                            self.env["product.pricelist.item"].create(
                                {
                                    "pricelist_id": pricelist.id,
                                    "product_id": product.id,
                                    "product_tmpl_id": self.product_tmpl_id.id,
                                    "fixed_price": float(field_value),
                                    "compute_price": "fixed",
                                }
                            )
                else:
                    product.write({field_name: field_value})
        return True

    def button_reject(self):
        ctx = {"product_ids": self.product_tmpl_id.id, "request_obj": self.id}
        return {
            "name": ("Reject Product Details Updates"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "cancel.reason",
            "target": "new",
            "context": ctx,
        }

    def write(self, vals):
        approve_vals = {"state", "active"}
        if len(vals) == len(approve_vals) and all(key in vals for key in approve_vals):
            return super(ProductChangeRequest, self).write(vals)
        changes_str = ""
        if not self.changes_text:
            changes_str = json.dumps(vals)
            vals.update({"changes_text": changes_str})
        else:
            changes_dict = json.loads(self.changes_text)
            changes_dict.update(vals)
            changes_str = json.dumps(changes_dict)
            vals.update({"changes_text": changes_str})
        html_note, variant_changes_text = self.get_html_note(changes_str)
        vals.update(
            {
                "change_request_note": html_note,
                "variant_changes_text": json.dumps(variant_changes_text),
            }
        )
        return super(ProductChangeRequest, self).write(vals)

    def get_html_note(self, change_str):
        change_dict = json.loads(change_str)
        html_note = """<b> The Following Fields Values Are Changed In This Change Request</b><br/>
        <table style="border: 1px solid black;border-collapse: collapse;width:100%">
            <tr>
                <td style="border: 1px solid black;padding:5px;"><b>Field Name</b></td>
                <td style="border: 1px solid black;padding:5px;"><b>Current Value</b></td>
                <td style="border: 1px solid black;padding:5px;"><b>New Value To Be Updated</b></td>
            </tr>"""
        variant_changes_text = None
        for field in fields_name:
            if field in change_dict.keys():
                if field == "taxes_id":
                    actual_taxes = ", ".join(
                        map(
                            lambda x: (x.description or x.name),
                            self.product_tmpl_id.mapped(field),
                        )
                    )
                    new_taxes_ids = list(tax[2] for tax in change_dict.get(field))[-1]
                    new_taxes = ", ".join(
                        map(
                            lambda x: (x.description or x.name),
                            self.env["account.tax"].browse(new_taxes_ids),
                        )
                    )
                    html_note = """<tr>
                                    <td style="border: 1px solid black;padding:5px;">%s</td>
                                    <td style="border: 1px solid black;padding:5px;">%s</td>
                                    <td style="border: 1px solid black;padding:5px;">%s</td>
                                 </tr>""" % (
                        fields_name.get(field),
                        actual_taxes,
                        new_taxes,
                    )
                elif field == "variant_change_request_line":
                    variant_changes_text = self.get_variant_changes(
                        change_dict.get(field)
                    )
                else:
                    html_note = """<tr>
                                    <td style="border: 1px solid black;padding:5px;">%s</td>
                                    <td style="border: 1px solid black;padding:5px;">%s</td>
                                    <td style="border: 1px solid black;padding:5px;">%s</td>
                                  </tr>""" % (
                        fields_name.get(field),
                        str(self.product_tmpl_id.mapped(field)[0]),
                        str(change_dict.get(field)),
                    )
        html_note = "</table><br/><br/>"
        if variant_changes_text:
            format_vals = self.format_variant_changes(variant_changes_text)
            html_note = format_vals
        return html_note, variant_changes_text

    def format_variant_changes(self, variant_change_dict):
        variant_change_table = """
        <h3>List Of Variants Changes</h3><br/>
        <table style="border: 1px solid black;border-collapse: collapse;width:100%">
            <tr>
                <td style="border: 1px solid black;padding:5px;"><b>Variant Name</b></td>
                <td style="border: 1px solid black;padding:5px;"><b>Field Name</b></td>
                <td style="border: 1px solid black;padding:5px;"><b>Current Value</b></td>
                <td style="border: 1px solid black;padding:5px;"><b>New Value To Be Updated</b></td>
            </tr>
        """
        for key, value in variant_change_dict.items():
            product = self.env["product.product"].browse(int(key))
            for k, v in value.items():
                variant_change_table = """<tr><td style="border: 1px solid black;padding:5px;"><b>%s</b></td>
                <td style="border: 1px solid black;padding:5px;">%s</td>
                <td style="border: 1px solid black;padding:5px;">%s</td>
                <td style="border: 1px solid black;padding:5px;">%s</td>""" % (
                    ", ".join(
                        map(
                            lambda x: (x.display_name),
                            product.product_template_attribute_value_ids,
                        )
                    ),
                    k.title() if k != "lst_price" else "Price",
                    product.mapped(k)[-1],
                    v,
                )
                variant_change_table = "</tr>"
        variant_change_table = "</table>"
        return variant_change_table

    def get_variant_changes(self, variant_changes_list):
        variant_change = self.env["variant.change.request"]
        change_list = json.loads(self.variant_changes_text)
        for variant in variant_changes_list:
            variant_obj = variant_change.browse(int(variant[1]))
            if variant[0] == 1 and variant[-1] != False:
                if change_list:
                    if str(variant_obj.product_id.id) in change_list:
                        change_list.get(str(variant_obj.product_id.id)).update(
                            variant[-1]
                        )
                    else:
                        change_list.update(
                            {str(variant_obj.product_id.id): variant[-1]}
                        )
                else:
                    change_list = {str(variant_obj.product_id.id): variant[-1]}
        return change_list


class ProductTemplate(models.Model):
    _inherit = "product.template"

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("to_approve", "Waiting For Approval"),
            ("approve", "Approved"),
            ("reject", "Rejected"),
        ],
        string="State",
        default="draft",
        copy=False,
    )
    rejection_reason = fields.Text("Reason For Rejection")
    product_variant_line = fields.One2many('product.product','product_tmpl_id')

    def button_approve(self):
        return self.write({"state": "approve"})

    def button_reject(self):
        product_ids = self.env.context.get("active_ids") or False
        if not product_ids:
            ctx = {"product_ids": self.id}
        else:
            ctx = {"product_ids": product_ids}
        return {
            "name": ("Reject Product Details Updates"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "cancel.reason",
            "target": "new",
            "context": ctx,
        }

    def change_request(self):
        change_request_obj = self.create_change_request()
        if change_request_obj:
            if self.attribute_line_ids:
                self.create_variant_change_request(change_request_obj)
                change_request_obj.write({"is_variants": True})
            else:
                change_request_obj.write({"is_variants": False})
            self.write({"state": "to_approve"})
            return {
                "name": "Product Change Request Form",
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                "res_model": "product.change.request",
                "res_id": change_request_obj.id,
            }
        return False

    def create_variant_change_request(self, request_obj):
        product_obj = self.env["product.product"].search(
            [("product_tmpl_id", "=", self.id)]
        )
        variant_change_request = self.env["variant.change.request"]
        for product in product_obj:
            prev_request = variant_change_request.search(
                [
                    ("product_id", "=", product.id),
                    ("change_request_id", "=", request_obj.id),
                ],
                limit=1,
            )
            if not prev_request:
                vals = {
                    "product_tmpl_id": self.id,
                    "product_id": product.id,
                    "lst_price": product.lst_price,
                    "name": ", ".join(
                        map(
                            lambda x: (x.display_name),
                            product.product_template_attribute_value_ids,
                        )
                    ),
                    "change_request_id": request_obj.id,
                    "barcode": product.barcode,
                    "default_code": product.default_code,
                }
                variant_change_request.create(vals)

    def create_change_request(self):
        change_request = self.env["product.change.request"]
        prev_request = change_request.search(
            [("product_tmpl_id", "=", self.id)], limit=1
        )
        if prev_request:
            return prev_request
        else:
            vals = {
                "product_tmpl_id": self.id,
                "name": self.name,
                "description": self.description,
                "description_sale": self.description_sale,
                "list_price": self.list_price,
                "l10n_in_hsn_code": self.l10n_in_hsn_code,
                "l10n_in_hsn_description": self.l10n_in_hsn_description,
                "active": True,
            }
            if self.taxes_id:
                vals.update({"taxes_id": [(6, 0, self.taxes_id.ids)]})
            new_change_request = change_request.create(vals)
            return new_change_request

    def button_submit(self):
        return self.write({"state": "to_approve"})


class ProductProduct(models.Model):
    _inherit = "product.product"

    state = fields.Selection(
        related="product_tmpl_id.state", store=True, readonly=False, copy=False
    )


class VariantChangeRequest(models.Model):
    _name = "variant.change.request"
    _description = "Variant Change Request"

    product_id = fields.Many2one("product.product", "Variant")
    name = fields.Char()
    product_tmpl_id = fields.Many2one("product.template", "Template")
    lst_price = fields.Float(
        "Price",
        default=1.0,
        digits="Product Price",
        help="Price at which the product is sold to customers.",
    )
    change_request_id = fields.Many2one("product.change.request", "Change Request")
    barcode = fields.Char("Barcode")
    default_code = fields.Char("Internal Reference")
