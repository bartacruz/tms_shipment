from odoo import api, fields, models

class SaleOrderTrip(models.TransientModel):
    _name = "sale.order.trip"
    _description = "Create a transport sale with trips"

    order_id = fields.Many2one('sale.order', string="Order")
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    product_id = fields.Many2one('product.product')
    has_route = fields.Boolean(string="Use Routes")
    route = fields.Many2one("tms.route")
    origin = fields.Many2one(
        "res.partner",
        domain="[('tms_location', '=', 'True')]",
        context={"default_tms_location": True},
    )
    destination = fields.Many2one(
        "res.partner",
        domain="[('tms_location', '=', 'True')]",
        context={"default_tms_location": True},
    )
    qty = fields.Integer("Trucks",default=1)
    start = fields.Datetime(string="Scheduled start")
    end = fields.Datetime(string="Scheduled end")

    order_confirmed = fields.Boolean(readonly=True)

    @api.onchange("origin", "destination", "start", "end", "has_route", "route")
    def _compute_readonly_fields(self):
        state = self.order_id.state
        if state == "sale" or state == "cancelled":
            self.order_confirmed = True
        else:
            self.order_confirmed = False
            
    def create_sale_order(self):
        vals_list = [{
            "partner_id": self.partner_id.id,
            "state": "sale",
            "order_line": [
                (0, 0, {'product_id': self.product_id.id, 
                        "product_uom_qty": self.qty,
                        "product_uom": self.product_id.uom_id.id,
                        'tms_origin_id':self.origin.id, 
                        'tms_destination_id':self.destination.id
                        }
                 ) 
            ],
        } ]
        print("vals",vals_list)
        self.env["sale.order"].create(vals_list)

