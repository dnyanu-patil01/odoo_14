from odoo import models, fields, api


class SaleWorkflowProcess(models.Model):
    _name = "sale.workflow.process.ept"
    _inherit = ['mail.thread','sale.workflow.process.ept']