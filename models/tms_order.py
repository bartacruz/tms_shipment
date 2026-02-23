# Copyright (C) 2025 Julio Santa Cruz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from random import randint
from datetime import datetime, timedelta
from odoo import _, api, fields, models
from markupsafe import Markup
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
        help='Tag color. No color means no display in kanban or front-end, to distinguish internal tags from public categorization tags.')


class TMSOrder(models.Model):
    _inherit = "tms.order"
    
    customer_id = fields.Many2one("res.partner", _("Customer"), related="sale_id.partner_id", store=True)
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
    
    warnings = fields.Char(compute="_compute_warnings")
    
    @api.model
    def _sale_id_expand_groups(self, records, domain, order):
        print("_expand_", records,domain,order)
        return records[::-1]
    
    @api.depends('driver_id')
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
    
    # @api.onchange('cpe_id')
    # def _onchange_cpe(self):
    #     for record in self:
    #         if record.cpe_id and not record.cpe_id.origin_partner_id:
    #             record.cpe_id.origin_partner_id = self.customer_id
    
    @api.model
    def write(self, vals):
        
        if "stage_id" in vals:
            actives = self.env["tms.stage"].search([("is_active", "=", True)]).ids
            completed = self.env.ref("tms.tms_stage_order_completed")
            
            print("Stage change to ", vals["stage_id"], " actives: ", actives)
            if vals["stage_id"] in actives:
                # TODO: add configurable option for auto-start
                if not self.start_trip:
                    print("starting trip")
                    vals["start_trip"] = True
                    vals["date_start"] = self.date_start or datetime.now()
                    vals["date_end"] = False
                else:
                    print("already started")
            elif vals["stage_id"] == completed.id:
                # TODO: add configurable option for auto-end
                if not self.end_trip:
                    print("ending completed trip")
                    vals["end_trip"] = True
                    vals["date_end"] = self.date_end or datetime.now()
                else:
                    print("already ended")
                    
        ret = super().write(vals)
        self.sale_id._compute_tms_active()
        if any(key in vals for key in ['stage_id','driver_id','date_start','date_end','tag_ids',]):
            print("sending order_changed",self.id,self.sale_id)
            self.env['bus.bus']._sendone('tms','order_changed',{'id':self.id,'order_id':self.sale_id.id})
        if 'cpe_id' in vals and self.cpe_id:
            self.cpe_id.action_update_cpe()
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
            old_stage = record.stage_id
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
            if cpe.transport_ids:
                record.vehicle_id = cpe.transport_ids[0].vehicle_id
                record.date_start = cpe.transport_ids[0].start_date
                if cpe.status == 'CN':
                    record.stage_id = self.env.ref("tms.tms_stage_order_completed")
                    record.end_trip = True
                    record.date_end = cpe.status_date
                elif cpe.status == 'AN':
                    record.stage_id = self.env.ref("tms.tms_stage_order_cancelled")
            if record.stage_id != old_stage and record.cpe_id:
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
        
    @api.model
    def assign_driver(self,order_id,driver_id):
        order = self.browse(order_id)
        
        order.driver_id = int(driver_id)
        order._onchange_driver_id()
        print("Assigned driver %s to order %s" % (driver_id,order_id))
        return order.id
    
    def _whatsapp_get_partner(self):
        if "customer_id" in self._fields:
            return self.customer_id
        return super()._whatsapp_get_partner()