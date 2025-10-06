from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import timedelta, date
import random
import string

_logger = logging.getLogger(__name__)

class TailorCustomer(models.Model):
    _name = 'tailor.customer' 
    _description = 'Tailor Customer'

    name = fields.Char(string='Customer Name', required=True)
    mobile = fields.Char(string='Mobile Number')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')
    order_ids = fields.One2many('tailor.order', 'customer_id', string='Orders')
    total_orders = fields.Integer(string='Total Orders', compute='_compute_statistics', store=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_statistics', store=True)
    
    total_advance_payment = fields.Float(string='Total Advance Payment', compute='_compute_payment_statistics', store=True)
    total_pending_payment = fields.Float(string='Total Pending Payment', compute='_compute_payment_statistics', store=True)

    @api.depends('order_ids', 'order_ids.state', 'order_ids.total_amount')
    def _compute_statistics(self):
        for record in self:
            record.total_orders = len(record.order_ids)
            record.total_amount = sum(record.order_ids.mapped('total_amount'))

    @api.depends('order_ids', 'order_ids.advance_payment', 'order_ids.pending_payment')
    def _compute_payment_statistics(self):
        for record in self:
            record.total_advance_payment = sum(record.order_ids.mapped('advance_payment'))
            record.total_pending_payment = sum(record.order_ids.mapped('pending_payment'))

class TailorBulkCategory(models.Model):
    _name = 'tailor.bulk.category'
    _description = 'Tailor Bulk Order Category'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

class TailorBulkClient(models.Model):
    _name = 'tailor.bulk.client'
    _description = 'Tailor Bulk Order Client'
    
    name = fields.Char(string='Client Name', required=True)
    client_id = fields.Char(string='Client ID', readonly=True, unique=True)
    company_name = fields.Char(string='Company Name', required=True)
    bulk_order_id = fields.Many2one('tailor.order', string='Bulk Order', required=True, ondelete='cascade')
    bulk_category_id = fields.Many2one('tailor.bulk.category', string='Bulk Category', required=True)
    mobile = fields.Char(string='Mobile Number')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')
    
    measurement_type = fields.Selection([
        ('shirt', 'Shirt'),
        ('pant', 'Pant'),
        ('both', 'Both')
    ], string='Measurement Type', required=True, default='shirt')
    
    shirt_length = fields.Float(string='Shirt Length (inches)')
    shoulder = fields.Float(string='Shoulder (inches)')
    sleeve_length = fields.Float(string='Sleeve Length (inches)')
    bicep = fields.Float(string='Bicep (inches)')
    cuff = fields.Float(string='Cuff (inches)')
    chest = fields.Float(string='Chest (inches)')
    stomach = fields.Float(string='Stomach (inches)')
    seat = fields.Float(string='Seat (inches)')
    neck = fields.Float(string='Neck (inches)')
    front = fields.Float(string='Front (inches)')
    
    pant_length = fields.Float(string='Pant Length (inches)')
    inseam = fields.Float(string='Inseam (inches)')
    waist = fields.Float(string='Waist (inches)')
    seat_pant = fields.Float(string='Seat (inches)')
    thigh = fields.Float(string='Thigh (inches)')
    knee = fields.Float(string='Knee (inches)')
    bottom = fields.Float(string='Bottom (inches)')
    
    remarks = fields.Text(string='Remarks')
    
    def _generate_unique_client_id(self, company_name, client_name):
        if company_name and company_name.strip():
            company_prefix = ''.join([c.upper() for c in company_name.strip() if c.isalpha()])
        else:
            company_prefix = 'COMPANY'
        
        if client_name and client_name.strip():
            client_prefix = ''.join([c.upper() for c in client_name.strip() if c.isalpha()])
        else:
            client_prefix = 'CLIENT'
        
        sequence = self.env['ir.sequence'].next_by_code('tailor.bulk.client') or '0001'
        if len(sequence) < 4:
            sequence = sequence.zfill(4)
        
        return f"{company_prefix}/{client_prefix}/{sequence}"
    
    @api.model
    def create(self, vals):
        if not vals.get('client_id'):
            company_name = vals.get('company_name', '')
            client_name = vals.get('name', '')
            vals['client_id'] = self._generate_unique_client_id(company_name, client_name)
        
        return super(TailorBulkClient, self).create(vals)
    
    @api.model
    def default_get(self, fields_list):
        defaults = super(TailorBulkClient, self).default_get(fields_list)
        
        if 'client_id' in fields_list and not defaults.get('client_id'):
            company_name = defaults.get('company_name', '')
            client_name = defaults.get('name', '')
            defaults['client_id'] = self._generate_unique_client_id(company_name, client_name)
        
        return defaults
    
    _sql_constraints = [
        ('client_id_unique', 'unique(client_id)', 'Client ID must be unique!')
    ]

class TailorLabour(models.Model):
    _name = 'tailor.labour'
    _description = 'Tailor Labour/Employee'

    name = fields.Char(string='Tailor Name', required=True)
    labour_category = fields.Selection([
        ('shop_labour', 'Shop Labour'),
        ('outsource_labour', 'Outsource Labour')
    ], string='Labour Category', required=True, default='shop_labour')
    
    skill_ids = fields.Many2many('tailor.skill', string='Skills')
    
    commission_percent = fields.Float(string='Commission (%)', default=10.0)
    mobile = fields.Char(string='Mobile Number')
    address = fields.Text(string='Address')
    joining_date = fields.Date(string='Joining Date', default=fields.Date.today)
    joining_date_formatted = fields.Char(string='Joining Date', compute='_compute_joining_date_formatted', store=True)
    
    @api.depends('joining_date')
    def _compute_joining_date_formatted(self):
        for record in self:
            if record.joining_date:
                record.joining_date_formatted = record.joining_date.strftime('%d/%m/%y')
            else:
                record.joining_date_formatted = ''
    
    completed_orders_count = fields.Integer(string='Completed Orders', compute='_compute_completed_orders', store=True)
    total_commission = fields.Float(string='Total Commission', compute='_compute_commission', store=True)
    monthly_commission = fields.Float(string='Monthly Commission', compute='_compute_monthly_commission')
    completed_order_ids = fields.One2many('tailor.order', 'labour_id', 
                                         domain=[('state', '=', 'delivered')], 
                                         string='Completed Orders')
    
    work_record_ids = fields.One2many('tailor.work.record', 'labour_id', string='Work Records')
    paid_work_count = fields.Integer(string='Paid Work Count', compute='_compute_payment_counts', store=True)
    pending_work_count = fields.Integer(string='Pending Work Count', compute='_compute_payment_counts', store=True)

    @api.depends('completed_order_ids')
    def _compute_completed_orders(self):
        for record in self:
            record.completed_orders_count = len(record.completed_order_ids)

    @api.depends('completed_order_ids', 'commission_percent')
    def _compute_commission(self):
        for record in self:
            total_sales = sum(record.completed_order_ids.mapped('total_amount'))
            record.total_commission = (total_sales * record.commission_percent) / 100

    def _compute_monthly_commission(self):
        today = fields.Date.today()
        start_of_month = today.replace(day=1)
        for record in self:
            monthly_orders = record.completed_order_ids.filtered(
                lambda o: o.create_date.date() >= start_of_month
            )
            monthly_sales = sum(monthly_orders.mapped('total_amount'))
            record.monthly_commission = (monthly_sales * record.commission_percent) / 100

    @api.depends('work_record_ids.payment_settled')
    def _compute_payment_counts(self):
        for record in self:
            record.paid_work_count = len(record.work_record_ids.filtered('payment_settled'))
            record.pending_work_count = len(record.work_record_ids.filtered(lambda r: not r.payment_settled))
    
class TailorSkill(models.Model):
    _name = 'tailor.skill'
    _description = 'Tailor Skill'
    _rec_name = 'name'

    name = fields.Char(string='Skill Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

class TailorWorkRecord(models.Model):
    _name = 'tailor.work.record'
    _description = 'Tailor Work Record'

    labour_id = fields.Many2one('tailor.labour', string='Labour', required=True, ondelete='cascade')
    order_id = fields.Many2one('tailor.order', string='Order', required=True)
    customer_id = fields.Many2one('tailor.customer', string='Customer', related='order_id.customer_id', store=True)
    product_type = fields.Selection(related='order_id.product_type', string='Product', store=True)
    amount = fields.Float(string='Amount', related='order_id.total_amount', store=True)
    payment_settled = fields.Boolean(string='Payment Settled', default=False)
    delivery_date = fields.Date(string='Delivery', related='order_id.delivery_date', store=True)
    payment_date = fields.Date(string='Payment Date')
    delivery_date_formatted = fields.Char(string='Delivery Date', compute='_compute_delivery_date_formatted', store=True)
    payment_date_formatted = fields.Char(string='Payment Date', compute='_compute_payment_date_formatted', store=True)
    
    @api.depends('delivery_date')
    def _compute_delivery_date_formatted(self):
        for record in self:
            if record.delivery_date:
                record.delivery_date_formatted = record.delivery_date.strftime('%d/%m/%y')
            else:
                record.delivery_date_formatted = ''
    
    @api.depends('payment_date')
    def _compute_payment_date_formatted(self):
        for record in self:
            if record.payment_date:
                record.payment_date_formatted = record.payment_date.strftime('%d/%m/%y')
            else:
                record.payment_date_formatted = ''
    
    payment_amount = fields.Float(string='Payment Amount')
    
    def action_settle_payment(self):
        for record in self:
            if not record.payment_settled:
                record.write({
                    'payment_settled': True,
                    'payment_date': fields.Date.today(),
                    'payment_amount': (record.amount * record.labour_id.commission_percent) / 100
                })

class TailorMaterial(models.Model):
    _name = 'tailor.material'
    _description = 'Tailor Material'
    _rec_name = 'name'

    name = fields.Char(string='Material Name', required=True)
    material_type = fields.Selection([
        ('fabric', 'Fabric'),
        ('thread', 'Thread'),
        ('button', 'Button'),
        ('zipper', 'Zipper'),
        ('other', 'Other')
    ], string='Material Type', default='fabric')
    unit_of_measure = fields.Selection([
        ('meter', 'Meter'),
        ('yard', 'Yard'),
        ('piece', 'Piece'),
        ('kg', 'Kilogram'),
        ('gram', 'Gram')
    ], string='Unit of Measure', default='meter')
    stock_quantity = fields.Float(string='Stock Quantity', default=0.0)
    unit_price = fields.Float(string='Unit Price')
    total_value = fields.Float(string='Total Value', compute='_compute_total_value', store=True)
    active = fields.Boolean(string='Active', default=True)
    
    @api.depends('stock_quantity', 'unit_price')
    def _compute_total_value(self):
        for record in self:
            record.total_value = record.stock_quantity * record.unit_price

class TailorOrderMaterial(models.Model):
    _name = 'tailor.order.material'
    _description = 'Tailor Order Material Consumption'

    order_id = fields.Many2one('tailor.order', string='Order', required=True, ondelete='cascade')
    material_id = fields.Many2one('tailor.material', string='Material', required=True)
    quantity_consumed = fields.Float(string='Quantity Consumed', required=True)
    unit_price = fields.Float(string='Unit Price', related='material_id.unit_price', readonly=True)
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)
    
    @api.depends('quantity_consumed', 'unit_price')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = record.quantity_consumed * record.unit_price
    
    @api.model
    def create(self, vals):
        material = self.env['tailor.material'].browse(vals['material_id'])
        if material.stock_quantity < vals['quantity_consumed']:
            raise ValidationError(f"Insufficient stock for {material.name}. Available: {material.stock_quantity}, Required: {vals['quantity_consumed']}")
        
        record = super(TailorOrderMaterial, self).create(vals)
        material.stock_quantity -= vals['quantity_consumed']
        return record
    
    def write(self, vals):
        if 'quantity_consumed' in vals:
            for record in self:
                old_quantity = record.quantity_consumed
                new_quantity = vals['quantity_consumed']
                difference = new_quantity - old_quantity
                
                if difference > 0 and record.material_id.stock_quantity < difference:
                    raise ValidationError(f"Insufficient stock for {record.material_id.name}. Available: {record.material_id.stock_quantity}, Required: {difference}")
                
                record.material_id.stock_quantity -= difference
        
        return super(TailorOrderMaterial, self).write(vals)
    
    def unlink(self):
        for record in self:
            record.material_id.stock_quantity += record.quantity_consumed
        return super(TailorOrderMaterial, self).unlink()

class TailorOrder(models.Model):
    _name = 'tailor.order'
    _description = 'Tailor Order'
    _order = 'create_date desc'

    name = fields.Char(string='Order No', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    customer_id = fields.Many2one('tailor.customer', string='Customer', required=False)
    customer_mobile = fields.Char(string='Mobile Number', related='customer_id.mobile', store=True, readonly=False)
    customer_email = fields.Char(string='Email', related='customer_id.email', store=True, readonly=False)
    customer_address = fields.Text(string='Address', related='customer_id.address', store=True, readonly=False)
    
    delivery_completed = fields.Boolean(string='Delivery Completed')
    image = fields.Image(string='Clothing Cut Image')
    
    order_category = fields.Selection([
        ('individual', 'Individual'),
        ('bulk', 'Bulk')
    ], string='Order Category', required=True, default='individual')
    
    company_name = fields.Char(string='Company Name')
    bulk_category_id = fields.Many2one('tailor.bulk.category', string='Bulk Category')
    bulk_client_ids = fields.One2many('tailor.bulk.client', 'bulk_order_id', string='Bulk Clients')
    total_bulk_clients = fields.Integer(string='Total Clients', compute='_compute_bulk_clients_count', store=True)
    
    measurement_master_id = fields.Many2one('tailor.labour', string='Measurement Master')
    cutting_master_id = fields.Many2one('tailor.labour', string='Cutting Master')
    stitching_master_id = fields.Many2one('tailor.labour', string='Stitching Master')
    
    shirt_measurement_master_id = fields.Many2one('tailor.labour', string='Shirt Measurement Master')
    shirt_cutting_master_id = fields.Many2one('tailor.labour', string='Shirt Cutting Master')
    shirt_stitching_master_id = fields.Many2one('tailor.labour', string='Shirt Stitching Master')
    
    pant_measurement_master_id = fields.Many2one('tailor.labour', string='Pant Measurement Master')
    pant_cutting_master_id = fields.Many2one('tailor.labour', string='Pant Cutting Master')
    pant_stitching_master_id = fields.Many2one('tailor.labour', string='Pant Stitching Master')
    
    description = fields.Text(string='Work Description')
    
    labour_id = fields.Many2one('tailor.labour', string='Primary Tailor')
    
    measurement_type = fields.Selection([
        ('shirt', 'Shirt'),
        ('pant', 'Pant'),
        ('both', 'Both')
    ], string='Measurement Type', required=True, default='shirt')
    
    stitching_category = fields.Selection([
        ('shirt_customised', 'Shirt Customised'),
        ('pant_customised', 'Pant Customised'),
        ('pant_regular', 'Pant Regular'),
        ('shirt_regular', 'Shirt Regular'),
        ('nehru_payjama', 'Nehru Payjama'),
        ('pathani_payjama', 'Pathani Payjama'),
        ('nehru_only', 'Nehru Only'),
        ('payjama_belt', 'Payjama Belt'),
        ('payjama_nadi', 'Payjama Nadi'),
        ('ho_shirt_only', 'H.O. Shirt Only'),
        ('kurta_pattern', 'Kurta Pattern'),
        ('kurta_astar', 'Kurta Astar'),
        ('jeans', 'Jeans'),
        ('safari', 'Safari'),
        ('simple_safari', 'Simple Safari'),
        ('sherwani', 'Sherwani'),
        ('kids_shirt', 'Kids Shirt'),
        ('kids_pant', 'Kids Pant'),
        ('half_pant', 'Half Pant'),
        ('blazer_only', 'Blazer Only'),
        ('blazer_pant_shirt', 'Blazer/Pant/Shirt'),
        ('modi_jacket', 'Modi Jacket/Business Coat')
    ], string='Stitching Category', required=True)
    
    shirt_charges = fields.Float(string='Shirt Charges', default=0.0)
    pant_charges = fields.Float(string='Pant Charges', default=0.0)
    alteration_charges = fields.Float(string='Alteration Charges', default=0.0)
    urgent_delivery_charges = fields.Float(string='Urgent Delivery Charges', default=0.0)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    advance_payment = fields.Float(string='Advance Payment', default=0.0)
    pending_payment = fields.Float(string='Pending Payment', compute='_compute_pending_payment', store=True)
    
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI')
    ], string='Payment Method', default='cash')
    
    final_payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI')
    ], string='Final Payment Method', default='cash')
    
    final_payment_amount = fields.Float(string='Final Payment Amount', compute='_compute_final_payment_amount', store=True)
    payment_reference = fields.Char(string='Payment Reference/Transaction ID')
    payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid')
    ], string='Payment Status', compute='_compute_payment_status', store=True)
    
    product_type = fields.Selection([
        ('mens', 'Mens'),
        ('ladies', 'Ladies')
    ], string='Product Type', required=True, default='mens')
    
    order_type = fields.Selection([
        ('new', 'New Order'),
        ('alteration', 'Alteration')  
    ], string='Order Type', required=True, default='new')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('measurement', 'Measurement'),
        ('cutting', 'Cutting'),
        ('stitching', 'Stitching'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    
    current_work_stage = fields.Char(string='Current Stage', compute='_compute_current_stage', store=True)
    
    sms_sent = fields.Boolean(string='SMS Sent', default=False)
    delivery_reminder_sent = fields.Boolean(string='Delivery Reminder Sent', default=False)
    
    remarks = fields.Text(string='Remarks')
    
    shirt_length = fields.Float(string='Shirt Length (inches)')
    shoulder = fields.Float(string='Shoulder (inches)')
    sleeve_length = fields.Float(string='Sleeve Length (inches)')
    bicep = fields.Float(string='Bicep (inches)')
    cuff = fields.Float(string='Cuff (inches)')
    chest = fields.Float(string='Chest (inches)')
    stomach = fields.Float(string='Stomach (inches)')
    seat = fields.Float(string='Seat (inches)')
    neck = fields.Float(string='Neck (inches)')
    front = fields.Float(string='Front (inches)')
    
    pant_length = fields.Float(string='Pant Length (inches)')
    inseam = fields.Float(string='Inseam (inches)')
    waist = fields.Float(string='Waist (inches)')
    seat_pant = fields.Float(string='Seat (inches)')
    thigh = fields.Float(string='Thigh (inches)')
    knee = fields.Float(string='Knee (inches)')
    bottom = fields.Float(string='Bottom (inches)')
    
    delivery_date = fields.Date(string='Delivery Date', required=True)
    current_date = fields.Date(string="Current Date", compute="_compute_current_date", store=False)
    delivery_date_formatted = fields.Char(string='Delivery Date', compute='_compute_delivery_date_formatted', store=True)
    current_date_formatted = fields.Char(string="Current Date", compute="_compute_current_date_formatted", store=False)
    create_date_formatted = fields.Char(string='Create Date', compute='_compute_create_date_formatted', store=True)
    write_date_formatted = fields.Char(string='Last Modified', compute='_compute_write_date_formatted', store=True)
    
    @api.depends('delivery_date')
    def _compute_delivery_date_formatted(self):
        for record in self:
            if record.delivery_date:
                record.delivery_date_formatted = record.delivery_date.strftime('%d/%m/%y')
            else:
                record.delivery_date_formatted = ''
    
    def _compute_current_date_formatted(self):
        for record in self:
            record.current_date_formatted = date.today().strftime('%d/%m/%y')
    
    @api.depends('create_date')
    def _compute_create_date_formatted(self):
        for record in self:
            if record.create_date:
                record.create_date_formatted = record.create_date.strftime('%d/%m/%y')
            else:
                record.create_date_formatted = ''
    
    @api.depends('write_date')
    def _compute_write_date_formatted(self):
        for record in self:
            if record.write_date:
                record.write_date_formatted = record.write_date.strftime('%d/%m/%y')
            else:
                record.write_date_formatted = ''
    
    material_ids = fields.One2many('tailor.order.material', 'order_id', string='Materials')
    total_material_cost = fields.Float(string='Total Material Cost', compute='_compute_total_material_cost', store=True)
    work_record_ids = fields.One2many('tailor.work.record', 'order_id', string='Work Records')

    @api.depends('pending_payment')
    def _compute_final_payment_amount(self):
        for record in self:
            record.final_payment_amount = record.pending_payment

    @api.depends('total_amount', 'advance_payment', 'pending_payment')
    def _compute_payment_status(self):
        for record in self:
            if record.pending_payment <= 0:
                record.payment_status = 'paid'
            elif record.advance_payment > 0 and record.pending_payment > 0:
                record.payment_status = 'partial'
            else:
                record.payment_status = 'pending'

    def action_complete_payment(self):
        for record in self:
            if record.pending_payment > 0:
                return {
                    'name': 'Payment Completion Warning',
                    'type': 'ir.actions.act_window',
                    'res_model': 'payment.completion.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_order_id': record.id,
                        'default_pending_amount': record.pending_payment,
                        'default_final_payment_method': record.final_payment_method,
                        'default_final_payment_amount': record.pending_payment,
                    }
                }
            else:
                raise UserError("No pending payment to complete.")

    def action_view_bulk_clients(self):
        self.ensure_one()
        return {
            'name': 'Bulk Clients',
            'type': 'ir.actions.act_window',
            'res_model': 'tailor.bulk.client',
            'view_mode': 'tree,form',
            'domain': [('bulk_order_id', '=', self.id)],
            'context': {'default_bulk_order_id': self.id},
            'target': 'current',
        }
    
    @api.constrains('customer_id', 'order_category')
    def _check_customer_required(self):
        for record in self:
            if record.order_category == 'individual' and not record.customer_id:
                raise ValidationError(_('Customer is required for individual orders.'))

    @api.depends('bulk_client_ids')
    def _compute_bulk_clients_count(self):
        for record in self:
            record.total_bulk_clients = len(record.bulk_client_ids)

    @api.depends('material_ids.total_cost')
    def _compute_total_material_cost(self):
        for record in self:
            record.total_material_cost = sum(record.material_ids.mapped('total_cost'))

    @api.onchange('order_category')
    def _onchange_order_category(self):
        if self.order_category == 'individual':
            self.company_name = False
            self.bulk_category_id = False
        elif self.order_category == 'bulk':
            pass

    @api.onchange('customer_mobile', 'customer_email', 'customer_address')
    def _onchange_customer_details(self):
        if self.customer_id and (self.customer_mobile or self.customer_email or self.customer_address):
            self.customer_id.write({
                'mobile': self.customer_mobile,
                'email': self.customer_email,
                'address': self.customer_address
            })

    @api.onchange('stitching_category')
    def _onchange_stitching_category(self):
        if self.stitching_category:
            category_charges = {
                'shirt_customised': {'shirt': 600, 'pant': 0},
                'pant_customised': {'shirt': 0, 'pant': 800},
                'pant_regular': {'shirt': 0, 'pant': 700},
                'shirt_regular': {'shirt': 500, 'pant': 0},
                'nehru_payjama': {'shirt': 700, 'pant': 1200},
                'pathani_payjama': {'shirt': 0, 'pant': 1200},
                'nehru_only': {'shirt': 700, 'pant': 0},
                'payjama_belt': {'shirt': 0, 'pant': 550},
                'payjama_nadi': {'shirt': 0, 'pant': 500},
                'ho_shirt_only': {'shirt': 550, 'pant': 0},
                'kurta_pattern': {'shirt': 800, 'pant': 0},
                'kurta_astar': {'shirt': 1100, 'pant': 0},
                'jeans': {'shirt': 0, 'pant': 800},
                'safari': {'shirt': 1500, 'pant': 0},
                'simple_safari': {'shirt': 1300, 'pant': 0},
                'sherwani': {'shirt': 4000, 'pant': 0},
                'kids_shirt': {'shirt': 450, 'pant': 0},
                'kids_pant': {'shirt': 0, 'pant': 600},
                'half_pant': {'shirt': 0, 'pant': 500},
                'blazer_only': {'shirt': 3000, 'pant': 0},
                'blazer_pant_shirt': {'shirt': 2000, 'pant': 2000},
                'modi_jacket': {'shirt': 1300, 'pant': 0}
            }
            
            if self.stitching_category in category_charges:
                charges = category_charges[self.stitching_category]
                self.shirt_charges = charges['shirt']
                self.pant_charges = charges['pant']

    @api.onchange('measurement_type')
    def _onchange_measurement_type(self):
        measurement_domain = [('skill_ids.name', 'ilike', 'measurement')]
        cutting_domain = [('skill_ids.name', 'ilike', 'cutting')]
        stitching_domain = [('skill_ids.name', 'ilike', 'stitching')]
        
        if self.measurement_type == 'both':
            self.measurement_master_id = False
            self.cutting_master_id = False
            self.stitching_master_id = False
        else:
            self.shirt_measurement_master_id = False
            self.shirt_cutting_master_id = False
            self.shirt_stitching_master_id = False
            self.pant_measurement_master_id = False
            self.pant_cutting_master_id = False
            self.pant_stitching_master_id = False
        
        return {
            'domain': {
                'measurement_master_id': measurement_domain,
                'cutting_master_id': cutting_domain,
                'stitching_master_id': stitching_domain,
                'shirt_measurement_master_id': measurement_domain,
                'shirt_cutting_master_id': cutting_domain,
                'shirt_stitching_master_id': stitching_domain,
                'pant_measurement_master_id': measurement_domain,
                'pant_cutting_master_id': cutting_domain,
                'pant_stitching_master_id': stitching_domain
            }
        }

    def action_next_stage(self):
        for record in self:
            if record.state == 'draft':
                record.state = 'confirmed'
            elif record.state == 'confirmed':
                record.state = 'measurement'
            elif record.state == 'measurement':
                record.state = 'cutting'
            elif record.state == 'cutting':
                record.state = 'stitching'
            elif record.state == 'stitching':
                record.state = 'ready'

    def action_add_bulk_client(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Bulk Client',
            'res_model': 'tailor.bulk.client',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_bulk_order_id': self.id,
                'default_company_name': self.company_name,
                'default_bulk_category_id': self.bulk_category_id.id if self.bulk_category_id else False,
            }
        }

    def _compute_current_date(self):
        for rec in self:
            rec.current_date = date.today()

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            current_year = fields.Date.today().strftime('%y')
            order_category = vals.get('order_category', 'individual')
            
            if order_category == 'bulk':
                prefix = f'BLK/{current_year}/'
                sequence_code = 'tailor.bulk.order'
            else:
                prefix = f'ST/{current_year}/'
                sequence_code = 'tailor.order'
            
            sequence = self.env['ir.sequence'].search([('code', '=', sequence_code)], limit=1)
            if not sequence:
                sequence = self.env['ir.sequence'].create({
                    'name': 'Tailor Order Sequence' if order_category == 'individual' else 'Tailor Bulk Order Sequence',
                    'code': sequence_code,
                    'prefix': prefix,
                    'suffix': '',
                    'padding': 4,
                    'number_increment': 1,
                    'number_next_actual': 1,
                    'use_date_range': False,
                })
            else:
                if sequence.prefix != prefix:
                    sequence.write({
                        'prefix': prefix,
                        'number_next_actual': 1
                    })
            vals['name'] = sequence.next_by_id()
        
        record = super(TailorOrder, self).create(vals)
        
        self._create_work_records(record)
        
        return record

    def write(self, vals):
        result = super(TailorOrder, self).write(vals)
        
        master_fields = [
            'measurement_master_id', 'cutting_master_id', 'stitching_master_id',
            'shirt_measurement_master_id', 'shirt_cutting_master_id', 'shirt_stitching_master_id',
            'pant_measurement_master_id', 'pant_cutting_master_id', 'pant_stitching_master_id'
        ]
        
        if any(field in vals for field in master_fields):
            for record in self:
                record._create_work_records(record)
        
        return result

    def _create_work_records(self, record):
        masters = []
        
        if record.measurement_type == 'both':
            if record.shirt_measurement_master_id:
                masters.append(record.shirt_measurement_master_id)
            if record.shirt_cutting_master_id:
                masters.append(record.shirt_cutting_master_id)
            if record.shirt_stitching_master_id:
                masters.append(record.shirt_stitching_master_id)
            if record.pant_measurement_master_id:
                masters.append(record.pant_measurement_master_id)
            if record.pant_cutting_master_id:
                masters.append(record.pant_cutting_master_id)
            if record.pant_stitching_master_id:
                masters.append(record.pant_stitching_master_id)
        else:
            if record.measurement_master_id:
                masters.append(record.measurement_master_id)
            if record.cutting_master_id:
                masters.append(record.cutting_master_id)
            if record.stitching_master_id:
                masters.append(record.stitching_master_id)
        
        record.work_record_ids.unlink()
        
        for master in masters:
            self.env['tailor.work.record'].create({
                'labour_id': master.id,
                'order_id': record.id,
            })

    @api.depends('state')
    def _compute_current_stage(self):
        stage_mapping = {
            'draft': 'Draft',
            'confirmed': 'Confirmed',
            'measurement': 'Measurement',
            'cutting': 'Cutting', 
            'stitching': 'Stitching',
            'ready': 'Ready',
            'delivered': 'Delivered',
            'cancelled': 'Cancelled'
        }
        for record in self:
            record.current_work_stage = stage_mapping.get(record.state, 'Unknown')

    @api.depends('shirt_charges', 'pant_charges', 'alteration_charges', 'urgent_delivery_charges')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.shirt_charges + record.pant_charges + record.alteration_charges + record.urgent_delivery_charges

    @api.depends('total_amount', 'advance_payment')
    def _compute_pending_payment(self):
        for record in self:
            record.pending_payment = record.total_amount - record.advance_payment

    def action_print_measurement(self):
        return self.env.ref('custom_tailor.action_report_measurement').report_action(self)

    def action_print_bill(self):
        return self.env.ref('custom_tailor.action_report_bill').report_action(self)
    def action_print_bulk_bill(self):
        return self.env.ref('custom_tailor.action_report_bulk_bill').report_action(self)

    def action_confirm(self):
        self.state = 'confirmed'

    def action_deliver(self):
        self.state = 'delivered'
        self.delivery_completed = True   

class TailorStock(models.Model):
    _name = 'tailor.stock'
    _description = 'Tailor Stock'

    name = fields.Char(string='Item')
    quantity = fields.Float(string='Quantity')

class TailorExpense(models.Model):
    _name = 'tailor.expense'
    _description = 'Tailor Expense'

    name = fields.Char(string='Expense Name')
    amount = fields.Float(string='Amount')
    date = fields.Date(string='Date', default=fields.Date.today)
    date_formatted = fields.Char(string='Date', compute='_compute_date_formatted', store=True)
    
    @api.depends('date')
    def _compute_date_formatted(self):
        for record in self:
            if record.date:
                record.date_formatted = record.date.strftime('%d/%m/%y')
            else:
                record.date_formatted = ''

class MaterialStockUpdate(models.TransientModel):
    _name = 'material.stock.update'
    _description = 'Material Stock Update Wizard'
    
    material_id = fields.Many2one('tailor.material', string='Material', required=True)
    quantity_to_add = fields.Float(string='Quantity to Add', required=True)
    update_type = fields.Selection([
        ('add', 'Add Stock'),
        ('remove', 'Remove Stock')
    ], string='Update Type', default='add', required=True)
    
    def update_stock(self):
        if self.update_type == 'add':
            self.material_id.stock_quantity += self.quantity_to_add
        else:
            if self.material_id.stock_quantity < self.quantity_to_add:
                raise ValidationError(f"Cannot remove {self.quantity_to_add} units. Only {self.material_id.stock_quantity} units available.")
            self.material_id.stock_quantity -= self.quantity_to_add
        
        return {'type': 'ir.actions.act_window_close'}

class PaymentCompletionWizard(models.TransientModel):
    _name = 'payment.completion.wizard'
    _description = 'Payment Completion Wizard'

    order_id = fields.Many2one('tailor.order', string='Order', required=True)
    pending_amount = fields.Float(string='Pending Amount', readonly=True)
    final_payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('bank_transfer', 'Bank Transfer')
    ], string='Payment Method', required=True, default='cash')
    final_payment_amount = fields.Float(string='Payment Amount', required=True)
    payment_reference = fields.Char(string='Payment Reference/Transaction ID')

    def confirm_payment(self):
        if self.final_payment_amount != self.pending_amount:
            raise ValidationError(f"Payment amount must be exactly {self.pending_amount}")
        
        self.order_id.write({
            'final_payment_method': self.final_payment_method,
            'final_payment_amount': self.final_payment_amount,
            'payment_reference': self.payment_reference,
            'pending_payment': 0,
            'payment_status': 'paid'
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Payment Completed',
                'message': f'Payment of {self.final_payment_amount} has been completed successfully!',
                'type': 'success',
                'sticky': False,
            }
        }