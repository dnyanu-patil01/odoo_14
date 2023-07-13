# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools

class AmazonshipmentServiceList(models.Model):
    _name = "amazon.shipment.service.list"
    _description = ("Amazon Shipment Rates To Show Available Service")
    _rec_name = "service_id"

    service_id = fields.Many2one("amazon.service", string='Service Name')
    service_code = fields.Char("Service Code")
    carrier_name = fields.Char("Carrier Name")
    carrier_id = fields.Char("Carrier ID")
    rate = fields.Float("Cost")
    rate_id = fields.Char("Rate ID")
    billed_weight = fields.Float('Billed Weight')
    est_pickup_startdate = fields.Char('Est Pickup StartDate')
    est_pickup_enddate = fields.Char('Est Pickup EndDate')
    est_delivery_startdate = fields.Char('Est Delivery StartDate')
    est_delivery_enddate = fields.Char('Est Delivery EndDate')
    picking_id = fields.Many2one("stock.picking", string='Picking ID')

class AmazonService(models.Model):
    _name = "amazon.service"
    _description = "Amazon Service"

    name = fields.Char("Service Name")
    service_code = fields.Char("Service Code")
