from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_order_no = fields.Char(string='Customer Order No')
    site_address = fields.Text(string='Site Address')
    delivery_date = fields.Date(string='Delivery Date')
    reminder_days = fields.Integer(string='Reminder Days', default=7)
    charge_size_inch = fields.Float(string='Charge Size (Inch)')
    show_jobwork_section = fields.Boolean(string='Show Job Work Section', default=False)
    
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    job_work_total = fields.Float(string='Job Work Total', compute='_compute_job_work_total', store=True)
    net_total = fields.Float(string='Net Total', compute='_compute_net_total', store=True)

    def action_show_jobwork(self):
        self.show_jobwork_section = True
        return True

    @api.depends('order_line.amount')
    def _compute_total_amount(self):
        for order in self:
            main_lines = order.order_line.filtered(lambda l: not l.is_jobwork_line)
            order.total_amount = sum(line.amount for line in main_lines)

    @api.depends('order_line.job_work_amount')
    def _compute_job_work_total(self):
        for order in self:
            jobwork_lines = order.order_line.filtered(lambda l: l.is_jobwork_line)
            order.job_work_total = sum(line.job_work_amount for line in jobwork_lines)

    @api.depends('total_amount', 'job_work_total')
    def _compute_net_total(self):
        for order in self:
            order.net_total = order.total_amount + order.job_work_total


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    item_type = fields.Selection([
        ('glass', 'Glass'),
        ('hardware', 'Hardware'),
        ('service', 'Service'),
        ('other', 'Other'),
    ], string='Item Type', default='glass')
    
    notes = fields.Text(string='Notes')
    is_jobwork_line = fields.Boolean(string='Is Job Work Line', default=False)
    
    actual_length = fields.Float(string='Actual Length', digits=(10, 2))
    actual_breadth = fields.Float(string='Actual Breadth', digits=(10, 2))
    
    charge_length = fields.Float(string='Charge Length', digits=(10, 2))
    charge_breadth = fields.Float(string='Charge Breadth', digits=(10, 2))
    soft_value = fields.Float(string='SOFT Value', digits=(10, 2), compute='_compute_soft_value', store=True)
    rate = fields.Float(string='Rate', digits=(10, 2))
    
    amount = fields.Float(string='Amount', compute='_compute_amount_custom', store=True, digits=(10, 2))
    
    job_work_type = fields.Selection([
        ('cutting', 'Cutting'),
        ('polishing', 'Polishing'),
        ('drilling', 'Drilling'),
        ('tempering', 'Tempering'),
        ('acid_colour', 'Acid Colour'),
        ('acid_frosted', 'Acid Frosted'),
        ('sada_polish', 'Sada Polish'),
        ('other', 'Other'),
    ], string='Job Work Type')
    job_work_length = fields.Float(string='Job Work Length', digits=(10, 2))
    job_work_breadth = fields.Float(string='Job Work Breadth', digits=(10, 2))
    job_work_qty = fields.Float(string='Job Work Quantity', default=1.0, digits=(10, 2))
    job_work_sqft = fields.Float(string='Job Work SQFT', compute='_compute_job_work_sqft', store=True, digits=(10, 4))
    job_work_rate = fields.Float(string='Job Work Rate', digits=(10, 2))
    job_work_amount = fields.Float(string='Job Work Amount', compute='_compute_job_work_amount', store=True, digits=(10, 2))

    @api.depends('charge_length', 'charge_breadth')
    def _compute_soft_value(self):
        for line in self:
            if line.charge_length and line.charge_breadth:
                line.soft_value = (line.charge_length * line.charge_breadth) / 144
            else:
                line.soft_value = 0.0

    @api.depends('soft_value', 'rate', 'product_uom_qty')
    def _compute_amount_custom(self):
        for line in self:
            if not line.is_jobwork_line:
                if line.soft_value and line.rate and line.product_uom_qty:
                    line.amount = line.soft_value * line.rate * line.product_uom_qty
                else:
                    line.amount = 0.0
            else:
                line.amount = 0.0

    @api.depends('job_work_length', 'job_work_breadth')
    def _compute_job_work_sqft(self):
        for line in self:
            if line.job_work_length and line.job_work_breadth:
                line.job_work_sqft = (line.job_work_length * line.job_work_breadth) / 144
            else:
                line.job_work_sqft = 0.0

    @api.depends('job_work_sqft', 'job_work_rate', 'job_work_qty')
    def _compute_job_work_amount(self):
        for line in self:
            if line.is_jobwork_line and line.job_work_sqft and line.job_work_rate:
                qty = line.job_work_qty if line.job_work_qty else 1.0
                line.job_work_amount = line.job_work_sqft * line.job_work_rate * qty
            else:
                line.job_work_amount = 0.0

    @api.onchange('actual_length', 'actual_breadth')
    def _onchange_actual_dimensions(self):
        if self.actual_length and not self.charge_length:
            self.charge_length = self.actual_length
        if self.actual_breadth and not self.charge_breadth:
            self.charge_breadth = self.actual_breadth

    @api.onchange('charge_length', 'charge_breadth')
    def _onchange_charge_dimensions(self):
        if self.charge_length and not self.job_work_length:
            self.job_work_length = self.charge_length
        if self.charge_breadth and not self.job_work_breadth:
            self.job_work_breadth = self.charge_breadth