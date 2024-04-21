from odoo import api, models, fields

class Order(models.Model):
    _name = 'delivery.order'
    _description = 'Order'

    order_id = fields.Char(string='Order ID', required=True, copy=False, readonly=True, index=True, default=lambda self: ('New'))

    name = fields.Char(string='Order Name', required=True)
    customer_id = fields.Many2one('delivery.customer', string='Customer', required=True)
    date = fields.Date(string='Order Date', default=fields.Date.today())
    carrier_id = fields.Many2one('delivery.carrier', string='Carrier')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', group_expand='_expand_states', required=True)
    amount = fields.Float(string='Amount')
    color = fields.Integer('Color', compute='_get_color')

    @api.model
    def create(self, vals):
        if vals.get('order_id', 'New') == 'New':
            vals['order_id'] = self.env['ir.sequence'].next_by_code('delivery.order_id') or 'New'
        return super(Order, self).create(vals)
    
    @api.constrains('amount')
    def _check_amount(self):
        for order in self:
            if order.amount < 0:
                raise models.ValidationError('Amount must be greater than 0')
            
    @api.constrains('status')
    def _check_status(self):
        for order in self:
            if order.status == 'done' and order.amount == 0:
                raise models.ValidationError('Amount must be greater than 0 for done status')
    
    def action_end_delivery(self):
        for order in self:
            if order.status == 'done':
                raise models.ValidationError('Order is already done')
            order.status = 'done'
    
    def action_remove_order(self):
        for order in self:
            order.unlink()

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).status.selection]

    def _get_color(self):
        for order in self:
            if order.status == 'draft':
                order.color = 3
            elif order.status == 'confirmed':
                order.color = 2
            elif order.status == 'done':
                order.color = 10
            elif order.status == 'cancel':
                order.color = 1
