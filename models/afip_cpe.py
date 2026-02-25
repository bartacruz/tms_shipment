from odoo import _, api, fields, models

class AfipCPE(models.Model):
    _inherit = 'afip.cpe'
    
    tms_order_id = fields.Many2one('tms.order', compute='_compute_tms_order_id')
    tms_has_order = fields.Boolean(compute="_compute_tms_order_id", store=True)
    
    def _compute_tms_order_id(self):
        for record in self:
            order_id = self.env['tms.order'].search([ ('cpe_id','=',record.id) ],limit=1)
            record.tms_order_id = order_id
            record.tms_has_order = len(order_id) > 0
    
    def action_update_cpe(self, force=False):
        ret = super().action_update_cpe(force=force)
        if ret and self.tms_order_id:
            self.tms_order_id.action_update_from_cpe()
        return ret
    
    def action_view_tms_order(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "tms.action_tms_dash_order"
        )
        if self.tms_order_id:
            action["views"] = [(self.env.ref("tms.tms_order_view_form").id, "form")]
            action["res_id"] = self.tms_order_id.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action
    
class AfipLocality(models.Model):
    _inherit="afip.locality"
    _order = "tms_order_count desc, afip_state_id, name"
    
    tms_order_ids = fields.Many2many('tms.order', compute='_compute_tms_orders')
    tms_order_origin_ids = fields.One2many('tms.order', 'origin_locality_id')
    tms_order_destination_ids = fields.One2many('tms.order', 'destination_locality_id')
    tms_order_count = fields.Integer(compute = '_compute_tms_order_count', store=True)
    
    @api.depends('tms_order_origin_ids', 'tms_order_destination_ids')
    def _compute_tms_orders(self):
        for record in self:
            record.tms_order_ids = record.tms_order_origin_ids + record.tms_order_destination_ids
    
    @api.depends('tms_order_origin_ids', 'tms_order_destination_ids')
    def _compute_tms_order_count(self):
        for record in self:
            record.tms_order_count = len(record.tms_order_origin_ids) + len(record.tms_order_destination_ids)