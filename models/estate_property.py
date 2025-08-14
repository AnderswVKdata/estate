from odoo import fields, models, api
from datetime import date, timedelta
from odoo.exceptions import UserError, ValidationError

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    name = fields.Char(required=True)
    expected_price = fields.Float(required=True)
    description = fields.Text()
    postcode = fields.Char()
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    date_availability = fields.Date()
    facades = fields.Integer()
    garage = fields.Boolean()
    property_type_name = fields.Char(
        related='property_type_id.name',
        store=True,
        readonly=True,
    )
    address = fields.Text()  
    date_availability = fields.Date(default=lambda self: date.today() + timedelta(days=90), copy=False)
    active = fields.Boolean(default=True)
    salesman = fields.Text()
    buyer = fields.Text()
    living_area = fields.Integer(string="Living Area")
    garden_area = fields.Integer(string="Garden Area")
    total_area = fields.Integer(compute="_compute_total_area", store=True, readonly=True)
    best_offer = fields.Float(
        string="Best Offer",
        compute="_compute_best_offer",
        store=True,
        readonly=True,
    )   
    garden = fields.Boolean(default=False)
    is_sold = fields.Boolean(default=False)
    is_cancelled = fields.Boolean(default=False)
    state = fields.Selection(
    [
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='new', required=True, copy=False)
    garden_orientation = fields.Selection(
        string='Direction',
        selection=[
            ('east','East'), 
            ('west','West'), 
            ('north','North'), 
            ('south','South')
        ],
        help="Garden orientation"
    )

    property_type_id = fields.Many2one(
        "estate.property.type",
          string="Property Type"
    )
    property_tag_id = fields.Many2many(
        "estate.property.tag",
          string="Property Tag"
    )
    property_offer_ids = fields.One2many(
        "estate.property.offer",
        "property_id",
        string="Offers"
    )   
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        copy=False,
    )   
    salesperson_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        default=lambda self: self.env.user,
    )

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            if record.name:
                existing = self.search([
                    ('name', '=', record.name),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError('The name must be unique.')             
    
    @api.constrains('expected_price')
    def _expected_price_validation(self):
        for record in self:
            if record.expected_price <= 0:
                raise ValidationError("Expected price must be greater than zero.")
            
    @api.onchange("garden")
    def _set_garden_variables(self):
        for record in self:
            if record.garden:
                record.garden_orientation="north"
                record.garden_area = 10
            else: 
                record.garden_orientation = False
                record.garden_area = 0                

    @api.depends("living_area","garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
    
    @api.depends("property_offer_ids.price")
    def _compute_best_offer(self):
        for property in self:
            prices = property.property_offer_ids.mapped("price")
            property.best_offer = max(prices) if prices else 0.0   
    
    @api.ondelete(at_uninstall=False)
    def _check_if_deletable(self):
        for record in self:
            if record.state not in ["new", "cancelled"]:
                raise UserError("You can only delete properties which are new or cancelled")   
    
    def set_property_sold(self):
        for record in self:
            if record.is_cancelled:
                raise UserError("Cannot sell a cancelled property")
            else:
                record.state = "sold"
                record.is_sold = True
 
    def set_property_cancelled(self):
        for record in self:
            if record.is_sold:
                raise UserError("Cannot cancel a sold property")
            else:
                record.state = "cancelled"
                record.is_cancelled = True

    
    
    