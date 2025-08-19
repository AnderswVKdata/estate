from odoo import fields, models, api 
from datetime import date, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import *


class EstatePropertyOffer(models.Model):
    _name="estate.property.offer"
    _description="property offer"

    offer_validity = fields.Integer(default=7)
    price = fields.Float()

    deadline = fields.Date(
        string="Deadline",
        compute="_compute_deadline",
        store=True,
        readonly=True,
    )

    partner_id = fields.Many2one( 
        "res.partner",
        string="partner",
        required=True
    )

    property_id = fields.Many2one(
        "estate.property",
        string="Property",
        required=True
    )
    
    property_type_id = fields.Many2one(
        related='property_id.property_type_id',
        store=True,
        string="Property Type"
    )

    offer_status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused')
        ],
        string="Offer Status",
        copy=False
    )
    
    @api.constrains("price")
    def _price_validator(self):
         for record in self:
            expected_price = record.property_id.expected_price
            min_price = expected_price *0.9
            if float_compare(record.price, min_price, precision_digits=2) < 0:
                 raise ValidationError("offer must be within 90 percent of expected price")       

    @api.model_create_multi
    def create(self, vals_list):
        # vals_list is a list of dicts, each dict is a record's values
        for vals in vals_list:
            property_id = vals.get("property_id")
            offer_price = vals.get("price", 0)
            if property_id:
                property = self.env["estate.property"].browse(property_id)
                if property.property_offer_ids:
                    max_offer = max(property.property_offer_ids.mapped("price"))
                    if offer_price < max_offer:
                        raise ValidationError("Cannot create an offer lower than an existing offer.")
                property.state = "offer_received"
        
        records = super().create(vals_list)
        return records
    
    def accept_offer(self):
         for record in self:
              record.offer_status = "accepted"
              record.property_id.selling_price = record.price
              record.property_id.buyer_id = record.partner_id
              record.property_id.state = "offer_accepted"

    def refuse_offer(self):
         for record in self:
              record.offer_status = "refused"
              record.property_id.selling_price = 0
              record.property_id.state = "new"

    @api.depends("offer_validity")
    def _compute_deadline(self):
        for record in self:
                record.deadline = date.today() + timedelta(days=record.offer_validity)

