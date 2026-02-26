from odoo import api, fields, models

class SaleOrderTrip(models.TransientModel):
    _name = "sale.order.trip"
    _description = "Create a transport sale with trips"

    order_id = fields.Many2one('sale.order', string="Order")
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    commitment_date = fields.Datetime(string="Fecha de Entrega", default=fields.Datetime.now)
    product_id = fields.Many2one('product.product', default=10)
    has_route = fields.Boolean(string="Use Routes")
    route = fields.Many2one("tms.route")
    origin_locality = fields.Many2one('afip.locality')
    destination_locality = fields.Many2one('afip.locality')
    origin = fields.Many2one(
        "res.partner",
        domain="[('tms_location', '=', 'True'), ('parent_id','=',partner_id)]",
        context={"default_tms_location": True, 'default_parent_id':partner_id},
        default = lambda self: self.order_id.tms_origin_id.id    )
    destination = fields.Many2one(
        "res.partner",
        domain="[('tms_location', '=', 'True')]",
        context={"default_tms_location": True},
        default = lambda self: self.order_id.tms_destination_id.id
    )
    qty = fields.Integer("Trucks",default=1)
    distance = fields.Integer("Distance",default=1)
    start = fields.Datetime(string="Scheduled start")
    end = fields.Datetime(string="Scheduled end")
    sale_label = fields.Char(compute="_compute_label")

    order_confirmed = fields.Boolean(readonly=True)

    @api.onchange("origin", "destination", "start", "end", "has_route", "route")
    def _compute_readonly_fields(self):
        state = self.order_id.state
        if state == "sale" or state == "cancelled":
            self.order_confirmed = True
        else:
            self.order_confirmed = False
            
    def create_sale_order(self):
        order_line = [
            (0, 0, {'product_id': self.product_id.id, 
                    "product_uom_qty": self.distance,
                    "product_uom": self.product_id.uom_id.id,
                    'tms_origin_id':self.origin.id,
                    'tms_origin_locality_id':self.origin_locality.id,
                    'tms_destination_id':self.destination.id,
                    'tms_destination_locality_id':self.destination_locality.id,
                    'tms_factor': 1,
                    'tms_factor_uom': 'T'
                    }
                ) 
        ]
        vals_list = [{
            "partner_id": self.partner_id.id,
            "commitment_date": self.commitment_date,
            "state": "sale",
            'tms_origin_locality_id':self.origin_locality.id,
            'tms_destination_locality_id':self.destination_locality.id,
            "tms_distance": self.distance,
            "order_line": order_line*self.qty,
        } ]
        print("vals",vals_list)
        self.env["sale.order"].create(vals_list)

