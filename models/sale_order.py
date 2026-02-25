from odoo import _, api, fields, models
from markupsafe import Markup

class SaleOrder(models.Model):
    _inherit = "sale.order"
    tms_origin_id = fields.Many2one(
        "res.partner",
        compute="_compute_tms_origin"
    )
    tms_origin_locality_id = fields.Many2one("afip.locality")
    tms_origin_label = fields.Char(compute="_compute_tms_labels")
    
    tms_destination_id = fields.Many2one(
        "res.partner",
        compute="_compute_tms_destination"
        # domain="[('tms_location', '=', 'True')]",
        # context={"default_tms_location": True},
        # compute="_compute_route_id",
        # store=True,
        # readonly=False,
    )
    tms_destination_locality_id = fields.Many2one("afip.locality")
    tms_destination_label = fields.Char(compute="_compute_tms_labels")
    
    tms_distance = fields.Integer()
    tms_active = fields.Boolean(compute="_compute_tms_active", store=True)
    
    @api.depends('tms_origin_id','tms_origin_locality_id','tms_destination_id','tms_destination_locality_id')
    def _compute_tms_labels(self):
        for record in self:
            if record.tms_origin_id:
                if record.tms_origin_id.name.startswith("Planta"):
                    record.tms_origin_label=record.tms_origin_id.city.title()
                else:
                    record.tms_origin_label = record.tms_origin_id.display_name.title()
            else:
                record.tms_origin_label = record.tms_origin_locality_id and record.tms_origin_locality_id.name.title() or ''
                
            if record.tms_destination_id:
                if record.tms_destination_id.name.startswith("Planta") :
                    record.tms_destination_label = record.tms_destination_id.city.title()
                else:
                    record.tms_destination_label = record.tms_destination_id.display_name
            else:
                record.tms_destination_label = record.tms_destination_locality_id and record.tms_destination_locality_id.name.title() or ''
                
    @api.depends('tms_order_ids','state')
    def _compute_tms_active(self):
        for record in self:
            stages = [stage.is_completed or stage.is_cancelled for stage in record.tms_order_ids]
            #print("_compute_tms_active",stages)
            record.tms_active = record.state == 'sale' and not all(stages)
    
    @api.depends('partner_invoice_id')
    def _compute_partner_shipping_id(self):
        super()._compute_partner_shipping_id()
        for order in self:
            parent = order.partner_invoice_id or order.partner_id.parent_id or order.partner_id
            shipping = parent.address_get(['delivery'])['delivery']
            order.partner_shipping_id = shipping or order.partner_invoice_id
    
    @api.depends('tms_order_ids')
    def _compute_tms_origin(self):
        for record in self:
            record.tms_origin_id = fields.first(record.tms_order_ids).origin_id
            if not record.tms_origin_locality_id:
                record.tms_origin_locality_id = fields.first(record.tms_order_ids).origin_locality_id
            
    
    @api.depends('tms_order_ids')
    def _compute_tms_destination(self):
        for record in self:
            record.tms_destination_id = fields.first(record.tms_order_ids).destination_id
            if not record.tms_destination_locality_id:
                record.tms_destination_locality_id = fields.first(record.tms_order_ids).destination_locality_id

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
        product_id = self.env["product.product"].browse(10)
        sl = self.order_line.create({
            'product_id': product_id.id, 
            "product_uom_qty": 1,
            "product_uom": product_id.uom_id.id,
            'tms_origin_id':self.tms_origin_id and self.tms_origin_id.id,
            'tms_origin_locality_id':self.tms_origin_locality_id and self.tms_origin_locality_id.id,
            'tms_destination_id':self.tms_destination_id and self.tms_destination_id.id,
            'tms_destination_locality_id':self.tms_destination_locality_id and self.tms_destination_locality_id.id,
            'tms_factor': self.tms_distance,
            'tms_factor_uom': product_id.tms_factor_distance_uom.name,
            'order_id': self.id,
        }) 
        self._tms_generation()
        return sl
        
        # return {
        #     "name": _("Transport Order"),
        #     "type": "ir.actions.act_window",
        #     "res_model": "sale.order.trip",
        #     'view_mode': 'form',
        #     "target": "new",
        #     "context": {"is_modal": True},
        # }
    
    def _post_tms_message(self, tms_orders):
        """
        Post messages to the Sale Order and the newly created TMS Orders
        """
        self.ensure_one()
        for tms_order in tms_orders:
            
            # tms_order.message_mail_with_source(
            #     "mail.message_origin_link",
            #     render_values={"self": tms_order, "origin": self},
            #     subtype_id=self.env.ref("mail.mt_note").id,
            #     author_id=self.env.user.partner_id.id,
            # )
            message = _(
                "Transport Order(s) Created: %s",
                Markup(
                    f"""<a href=# data-oe-model=tms.order data-oe-id={tms_order.id}"""
                    f""">{tms_order.name}</a>"""
                ),
            )
            print("posting messsage",message)
            self.message_post(body=message)
            
    def action_view_trip_sale_order_line(self):
        action = super().action_view_trip_sale_order_line()
        action['context']={"default_origin":self.tms_origin_id}
        print("ACTION",action)
        return action