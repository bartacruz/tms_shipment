from odoo import _, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    tms_origin_locality_id = fields.Many2one('afip.locality')
    tms_destination_locality_id = fields.Many2one('afip.locality')
    
    def _prepare_tms_values(self, **kwargs):
        ret = super()._prepare_tms_values(**kwargs)
        ret['origin_locality_id'] = self.tms_origin_locality_id.id or None
        ret['destination_locality_id'] = self.tms_destination_locality_id.id or None
        
        if self.order_id.state == "sale":
            stage = self.env.ref("tms.tms_stage_order_confirmed")
        elif self.state == "cancel":
            stage = self.env.ref("tms.tms_stage_order_cancelled")
        else:
            stage = self.env.ref("tms.tms_stage_order_draft")
        if self.tms_order_ids.stage_id != stage:
            ret['stage_id']=stage.id
        
        return ret
    
    def _check_required_fields(self):
        print("Ignoring fields check")