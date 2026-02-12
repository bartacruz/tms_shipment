from odoo import api, fields, models


class SaleOrderLineTrip(models.TransientModel):
    _inherit = "sale.order.line.trip"
    origin = fields.Many2one(related = "order_line_id.order_id.tms_origin_id")
    destination = fields.Many2one(default = lambda self: self.order_line_id.order_id.tms_destination_id.id)