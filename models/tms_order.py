# Copyright (C) 2025 Julio Santa Cruz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from random import randint
from datetime import datetime, timedelta
from odoo import _, api, fields, models, SUPERUSER_ID
from markupsafe import Markup
import logging

_logger = logging.getLogger(__name__)
class TMSOrderTag(models.Model):
    _name = "tms.order.tag"
    _description = "Order Tag"
    _order = "sequence, id"

    def _default_color(self):
        return randint(1, 11)
    
    name = fields.Char("Name", required=True, translate=True)
    sequence = fields.Integer('Sequence', default=0)
    color = fields.Integer(
        string='Color Index', default=lambda self: self._default_color(),
        help='Tag color. No color means no display in kanban or front-end, to distinguish internal tags from public categorization tags.'
    )

class TMSOrder(models.Model):
    _inherit = "tms.order"
    
    customer_id = fields.Many2one("res.partner", _("Customer"), related="sale_id.partner_shipping_id", store=True)
    sale_order_label = fields.Char("Pedido", compute = '_compute_sale_order_label', store=True, readonly=True, group_expand='_sale_id_expand_groups')
    color = fields.Integer("Color",compute = '_compute_tms_color')
    tag_ids = fields.Many2many('tms.order.tag', string=_("Etiquetas"))
    is_active = fields.Boolean(related='stage_id.is_active')
    is_completed = fields.Boolean(related='stage_id.is_completed')
    is_cancelled = fields.Boolean(related='stage_id.fold')
    trailer_id = fields.Many2one('fleet.vehicle', related='vehicle_id.trailer_id', readonly=True)
    vehicle_label = fields.Char(compute='_compute_vehicle_label',readonly=True, store=True)
    contact_phone = fields.Char(compute = '_compute_contact_phone')
    driver_phone =  fields.Char(compute='_compute_driver_phone')
    origin_locality_id = fields.Many2one('afip.locality')
    origin_state_id = fields.Many2one('res.country.state', related="origin_locality_id.state_id")
    destination_locality_id = fields.Many2one('afip.locality')
    destination_state_id = fields.Many2one('res.country.state', related="destination_locality_id.state_id")
    
    cpe_id = fields.Many2one("afip.cpe","Carta de Porte",ondelete="set null")
    cpe_mismatch = fields.Boolean()
    
    distance = fields.Integer()
    delivered = fields.Integer()
    delivered_extra =fields.Integer()
    delivered_total = fields.Integer(compute='_compute_delivered', readonly=True)
    
    warnings = fields.Char(compute="_compute_warnings")
    has_warnings = fields.Boolean(compute="_compute_has_warnings", store=True,readonly=True)
    
    driver_rejected = fields.Boolean()
    
    cloned_sale_id = fields.Many2one('sale.order')
    cloned_sale_line_id = fields.Many2one('sale.order.line')
    
    
    def tms_clone(self):
        for record in self:
            record = record.with_context(trucking_clone=True)
            if not record.sale_line_id.product_id.tms_trip:
                try:
                    print("cloning",record,record.name,record.sale_id,record.sale_line_id)
                    record.cloned_sale_id = record.sale_id
                    record.cloned_sale_line_id = record.sale_line_id
                    record.sale_id = False
                    record.sale_line_id = False
                    record.cloned_sale_id._compute_tms_order_ids()
                    record.cloned_sale_id._compute_has_tms_order()
                    
                except:
                    _logger.exception("record %s" % record)
                self.env.cr.commit()
            else:
                print("not dereffing",record,record.name,"because it has product",record.sale_line_id.product_id,record.sale_line_id.product_id.name)
            
    
    @api.model
    def _sale_id_expand_groups(self, records, domain, order):
        print("_expand_", records,domain,order)
        return records[::-1]
    
    @api.depends('delivered','delivered_extra','cpe_id')
    def _compute_delivered(self):
        for record in self:
            record.delivered_total = record.delivered + record.delivered_extra
            print("delivered",record,record.delivered_total)
            
    @api.depends('driver_id','is_active','cpe_mismatch', 'vehicle_id')
    def _compute_has_warnings(self):
        for record in self:
            record.has_warnings = len(record.warnings) > 0
        
    @api.depends('driver_id','is_active','cpe_mismatch','vehicle_id')
    def _compute_warnings(self):
        for record in self:
            record.warnings = ''
            if record.is_active  and record.driver_id and not record.driver_id.vehicle_id:
                record.warnings += "El conductor no tiene vehículo asignado\n"
            if record.is_active and record.driver_id:
                record.driver_id._compute_active_tms_order()
                if record.driver_id.active_tms_order_id != record:
                    print("warn",record,record.driver_id.active_tms_order_id,record)
                    record.warnings += "El conductor está asignado en otra orden (%s)\n" % record.driver_id.active_tms_order_id.name
            if record.cpe_mismatch:
                record.warnings += "Los datos de la CPE no coinciden con la orden\n"
            if record.driver_rejected and record.driver_id:
                record.warnings += "El conductor rechazó la orden\n"
                
    @api.depends('customer_id')
    def _compute_contact_phone(self):
        for record in self:
            if not record.contact_phone:
                record.contact_phone = record.customer_id.mobile or record.customer_id.phone or False

    @api.depends('driver_id')
    def _compute_driver_phone(self):
        for record in self:
            if not record.driver_phone:
                record.driver_phone = record.driver_id.mobile or record.driver_id.phone or False

    # def _compute_display_name(self):
    #     for record in self:
    #         record.display_name = record.driver_id.name or record.name
    
    @api.depends('driver_id','vehicle_id')
    def _compute_vehicle_label(self):
        for record in self:
            if not record.vehicle_id and record.driver_id:
                record.vehicle_id = record.driver_id.vehicle_id
            record.vehicle_label = record.vehicle_id.license_plate
            if record.trailer_id:
                record.vehicle_label += ' ' + record.trailer_id.license_plate
            print(record.vehicle_label)
                
    @api.depends('sale_id')
    def _compute_sale_order_label(self):
        for record in self:
            record.sale_order_label = '%s - %s' % (record.sale_id.name,record.sale_id.partner_id.name,)
        
    def _compute_tms_color(self):
        for record in self:
            if not record.driver_id:
                record.color = 3
            else:
                if record.end_trip:
                    record.color = 10
                elif record.start_trip:
                    record.color = 2
                else:
                    record.color = 7
    @api.onchange('driver_id')
    def _onchange_driver_id(self):
        print("onchange driver",self.driver_id.vehicle_id)
        self.vehicle_id = self.driver_id.vehicle_id
        self.driver_rejected = False
    
    # @api.onchange('cpe_id')
    # def _onchange_cpe(self):
    #     for record in self:
    #         if record.cpe_id and not record.cpe_id.origin_partner_id:
    #             record.cpe_id.origin_partner_id = self.customer_id
    
    def update_sale_line(self):
        for record in self:
            delivered = record.delivered_total
            print("update_sale_line",record,delivered)
            
            # On tms.order, distances are in Km and weight in kg.
            # We need to convert them to the Uom of the sale.line fields.
            
            
            product_id = record.sale_line_id.product_id
            distance_uom = self.env.ref('uom.uom_categ_length')
            weight_uom = self.env.ref('uom.product_uom_categ_kgm')
            units_uom = self.env.ref('uom.product_uom_categ_unit')
            
            kg_uom = self.env.ref('uom.product_uom_kgm')
            km_uom = self.env.ref('uom.product_uom_km')
            if product_id.tms_factor_type == 'weight':
                record.sale_line_id.tms_factor = kg_uom._compute_quantity(delivered,product_id.tms_factor_weight_uom)
                record.sale_line_id.tms_factor_uom = product_id.tms_factor_weight_uom.name
                 
            elif product_id.tms_factor_type == 'distance':
                record.sale_line_id.tms_factor = km_uom._compute_quantity(record.distance,product_id.tms_factor_distance_uom)
                record.sale_line_id.tms_factor_uom = product_id.tms_factor_distance_uom.name
            
            if product_id.uom_id.category_id == weight_uom:
                if delivered > 1:
                    record.sale_line_id.product_uom_qty = kg_uom._compute_quantity(delivered,product_id.uom_id)
                    print("updated product_uom_qty",delivered,record.sale_line_id.product_uom_qty)
                record.sale_line_id.qty_delivered = kg_uom._compute_quantity(delivered,product_id.uom_id)
                record.sale_line_id.product_uom = product_id.uom_id
            elif product_id.uom_id.category_id == distance_uom:
                record.sale_line_id.qty_delivered = km_uom._compute_quantity(record.distance,product_id.uom_id)
                record.sale_line_id.product_uom = product_id.uom_id
            elif product_id.uom_id.category_id == units_uom:
                record.sale_line_id.qty_delivered = (record.distance and delivered) and 1 or 0
                record.sale_line_id.product_uom = product_id.uom_id
            
            record.sale_line_id.name = f'Viaje {record.name} {record.origin_locality_id.name} a {record.destination_locality_id.name}' 
            if record.driver_id:
                    record.sale_line_id.name += f' Transportista: {record.driver_id.name}'
            if record.is_completed:
                # Fill the order line with trip data.
                if record.distance > 1:
                    record.sale_line_id.name += f' Distancia:{record.distance} km'
                if delivered > 1:
                    record.sale_line_id.name += f' Descarga neta: {delivered} kg'
                if record.sale_id.pricelist_id:
                    record.sale_line_id.name += f' Lista de Precio: {record.sale_id.pricelist_id.name}'
                if record.cpe_id:
                    record.sale_line_id.name += f' CTG: {record.cpe_id.ctg_number}'
        
    @api.model
    def write(self, vals):
        if "stage_id" in vals and self.env.context.get('trucking_clone',False):
            stage = vals.pop('stage_id')
            print("ignoring stage_id",stage, "in tms.order write",self,vals)

        completed = self.env.ref("tms.tms_stage_order_completed")
        if "stage_id" in vals:
            actives = self.env["tms.stage"].search([("is_active", "=", True)]).ids
            
            
            print("Stage change to ", vals["stage_id"], " actives: ", actives)
            if vals["stage_id"] in actives:
                # # TODO: add configurable option for auto-start
                # if not self.start_trip:
                #     print("starting trip")
                #     vals["start_trip"] = True
                #     vals["date_start"] = self.date_start or datetime.now()
                    vals["date_end"] = False
                    vals["end_trip"] = False
                # else:
                #     print("already started")
            elif vals["stage_id"] == completed.id:
                
                # TODO: add configurable option for auto-end
                if not self.end_trip:
                    print("ending completed trip")
                    vals["end_trip"] = True
                    vals["date_end"] = self.date_end or datetime.now()
                else:
                    print("already ended")
                    
        ret = super().write(vals)
        
        if self.env.context.get('trucking_clone',False):
            return ret
        
        self.sale_id._compute_tms_active()
        if any(key in vals for key in ['stage_id','driver_id','date_start','date_end','tag_ids','cpe_id','warnings']):
            print("sending order_changed",self.id,self.sale_id)
            self.env['bus.bus']._sendone('tms','order_changed',{'id':self.id,'order_id':self.sale_id.id})
        
        if 'cpe_id' in vals:
            if self.cpe_id:
                updated = self.cpe_id.action_update_cpe()
                if not updated:
                    self.action_update_from_cpe()
            elif self.cpe_mismatch:
                self.cpe_mismatch=False
                
        if 'vehicle_id' in vals:
            if self.cpe_mismatch and self.cpe_id:
                # Vehicle changed after mismatch. Try again.
                self.action_update_from_cpe()
        
        if any(x in vals for x in ['delivered','delivered_extra','distance','driver_id','origin_locality_id','destination_locality_id']):
            self.update_sale_line()

        return ret
    
    
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
    def action_open_record_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Detalle del viaje',
            'res_model': 'tms.order',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
    def action_update_from_cpe(self):
        for record in self:
            cpe = record.cpe_id
            if not record.sale_line_id or not record.sale_line_id.product_id.tms_trip:
                print(record,"Ignoring CPE update",record.sale_line_id)
                return
            
            old_stage = record.stage_id
            
            if cpe.transport_ids:
                vehicle_id = cpe.transport_ids[0].vehicle_id
                if record.vehicle_id and vehicle_id != record.vehicle_id:
                    _logger.warning("CPE %s: Vehicle mismatch: %s (%s) != %s (%s) ",
                        record,
                        record.vehicle_id, 
                        record.vehicle_id.name,
                        vehicle_id,
                        vehicle_id.name
                    )
                    if not record.cpe_mismatch:
                        record.cpe_mismatch = True
                        message = _(
                            "Vehicle from CPE %s mismatches the one in the order. The order was not updated.",
                            Markup(
                                f"""<a href=# data-oe-model=afip.cpe data-oe-id={record.cpe_id.id}"""
                                f""">{record.cpe_id.name}</a>"""
                            ),
                        )
                        self.with_user(SUPERUSER_ID).message_post(
                            body=message,
                            message_type='comment',
                        )
                    return False
                record.cpe_mismatch = False
                record.vehicle_id = cpe.transport_ids[0].vehicle_id
                record.date_start = cpe.transport_ids[0].start_date
                record.distance = cpe.transport_ids[0].distance
                
                record.delivered = cpe.unload_net
                
                if cpe.status == 'CN':
                    record.stage_id = self.env.ref("tms.tms_stage_order_completed")
                    record.end_trip = True
                    record.date_end = cpe.status_date
                elif cpe.status == 'AN':
                    record.stage_id = self.env.ref("tms.tms_stage_order_cancelled")
                    
            if cpe.customer_id:
                record.customer_id = cpe.customer_id
                record.sale_id.partner_invoice_id = cpe.customer_id
            if cpe.origin_id:
                record.origin_id = cpe.origin_id
            if cpe.origin_locality_id:
                record.origin_locality_id = cpe.origin_locality_id
            if cpe.destination_id:
                record.destination_id = cpe.destination_id
            if cpe.destination_locality_id:
                record.destination_locality_id = cpe.destination_locality_id
            
            # if record.stage_id != old_stage and record.cpe_id:
            message = _(
                "Orden actualizada desde la carta de porte: %s",
                Markup(
                    f"""<a href=# data-oe-model=afip.cpe data-oe-id={record.cpe_id.id}"""
                    f""">{record.cpe_id.name}</a>"""
                ),
            )
            self.message_post(body=message)
    
    def button_end_order(self):
        super().button_end_order()
        self.stage_id = self.env.ref("tms.tms_stage_order_completed")
        self.message_post(body=_("Order finished"))
        
    @api.model
    def assign_driver(self,order_id,driver_id):
        order = self.browse(order_id)
        
        order.driver_id = int(driver_id)
        order._onchange_driver_id()
        print("Assigned driver %s to order %s" % (driver_id,order_id))
        message = _(
            "Driver assigned: %s",
            Markup(
                f"""<a href=# data-oe-model=tms.driver data-oe-id={driver_id}"""
                f""">{order.driver_id.name}</a>"""
            ),
        )
        order.message_post(body=message)
        order.driver_rejected=False
        return order.id
    
    def _whatsapp_get_partner(self):
        if "customer_id" in self._fields:
            return self.customer_id
        return super()._whatsapp_get_partner()
    
    def _send_whatsapp(self,partner_id,body=False,template_id=False,gateway=1):
        gateway_id = self.env['mail.gateway'].browse(gateway)
        context = {'default_res_id':self.id}
        if template_id:
            context['whatsapp_template_id'] = template_id
            template = self.env['mail.whatsapp.template'].browse(template_id)    
            body = template.with_context(context).render_body_message()
            
        number_field_name = partner_id.mobile and 'mobile' or 'phone'
        channel = partner_id._whatsapp_get_channel(number_field_name, gateway_id)
        message = channel.with_context(context).message_post(
            body=body, subtype_xmlid="mail.mt_comment", message_type="comment")
        message.tms_order_id = self.id
        _logger.info("WA %s sent to %s:  %s",self.name,partner_id.name,message)
            
    def action_send_whatsapp_request(self):
        partner = self.driver_id
        #partner = self.env['res.partner'].browse(4185) # YO
        self._send_whatsapp(partner,template_id=12)

