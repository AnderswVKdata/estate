from odoo import fields, models, api

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"

    name = fields.Char(required=True)
    offer_count = fields.Integer(
        string="Offer Count",
        compute='_compute_offer_count'
    )

    property_ids = fields.One2many(
        "estate.property",
        "property_type_id",
        string="Properties",
    )

    offer_ids = fields.One2many(
        'estate.property.offer',
        'property_type_id',
        string="Offers"
    )   

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

            