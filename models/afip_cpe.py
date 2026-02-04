from odoo import _, api, fields, models

class AfipCPE(models.Model):
    _inherit = 'afip.cpe'
    
    tms_order_id = fields.Many2one('tms.order', compute='_compute_tms_order_id')
    
    def _compute_tms_order_id(self):
        for record in self:
            order_id = self.env['tms.order'].search([ ('cpe_id','=',record.id) ],limit=1)
            record.tms_order_id = order_id
    
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