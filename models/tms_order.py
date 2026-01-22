# Copyright (C) 2025 Julio Santa Cruz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from random import randint
from datetime import datetime, timedelta
from odoo import _, api, fields, models

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
    sale_order_label = fields.Char("Pedido", compute = '_compute_sale_order_label', store=True, readonly=True)
    color = fields.Integer("Color",compute = '_compute_tms_color')
    tag_ids = fields.Many2many('tms.order.tag', string=_("Etiquetas"))
    is_active = fields.Boolean(related='stage_id.is_active')
    trailer_id = fields.Many2one('fleet.vehicle', related='vehicle_id.trailer_id', readonly=True)
    cpe_id = fields.Many2one("afip.cpe","Carta de Porte",ondelete="set null")
    
    # def _compute_display_name(self):
    #     for record in self:
    #         record.display_name = record.driver_id.name or record.name
    
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

    @api.onchange('cpe_id')
    def _onchange_cpe(self):
        for record in self:
            if record.cpe_id and not record.cpe_id.origin_partner_id:
                record.cpe_id.origin_partner_id = self.customer_id
    
    @api.model
    def write(self, vals):
        for order in self:
            if "stage_id" in vals:
                actives = self.env["tms.stage"].search([("is_active", "=", True)]).ids
                completed = self.env.ref("tms.tms_stage_order_completed")
                
                print("Stage change to ", vals["stage_id"], " actives: ", actives)
                if vals["stage_id"] in actives:
                    # TODO: add configurable option for auto-start
                    if not order.start_trip:
                        print("starting trip")
                        vals["start_trip"] = True
                        vals["date_start"] = order.date_start or datetime.now()
                    else:
                        print("already started")
                elif vals["stage_id"] == completed.id:
                    # TODO: add configurable option for auto-end
                    if not order.end_trip:
                        print("ending completed trip")
                        vals["end_trip"] = True
                        vals["date_end"] = order.date_end or datetime.now()
                    else:
                        print("already ended")
        return super().write(vals)
    
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