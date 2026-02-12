from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    tms_origin_id = fields.Many2one(
        "res.partner",
        compute="_compute_tms_origin"
    )
    tms_destination_id = fields.Many2one(
        "res.partner",
        compute="_compute_tms_destination"
        # domain="[('tms_location', '=', 'True')]",
        # context={"default_tms_location": True},
        # compute="_compute_route_id",
        # store=True,
        # readonly=False,
    )
    tms_active = fields.Boolean(compute="_compute_tms_active", store=True)
    
    @api.depends('tms_order_ids')
    def _compute_tms_active(self):
        for record in self:
            stages = [stage.is_completed or stage.is_cancelled for stage in record.tms_order_ids]
            record.tms_active = not all(stages)
    
    @api.depends('partner_invoice_id')
    def _compute_partner_shipping_id(self):
        super()._compute_partner_shipping_id()
        for order in self:
            parent = order.partner_invoice_id or order.partner_id.parent_id or order.partner_id
            shipping = parent.address_get(['delivery'])['delivery']
            order.partner_shipping_id = shipping or order.partner_invoice_id
    
    def _compute_tms_origin(self):
        for record in self:
            record.tms_origin_id = fields.first(record.tms_order_ids).origin_id
    
    def _compute_tms_destination(self):
        for record in self:
            record.tms_destination_id = fields.first(record.tms_order_ids).destination_id

    def action_create_tms_order(self):
        vid = self.env.ref('tms_shipment.sale_order_trip_view_form').id
        return {
            "name": _("Transport Order"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order.trip",
            "target": "new",
            "views": [[vid, "form"]],
            "context": {"is_modal": True},
        }
        
    def action_new_trip_sale(self):
        return {
            "name": _("Transport Order"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order.trip",
            "target": "new",
            "context": {"is_modal": True},
        }
        
    def action_view_trip_sale_order_line(self):
        action = super().action_view_trip_sale_order_line()
        action['context']={"default_origin":self.tms_origin_id}
        print("ACTION",action)
        return action