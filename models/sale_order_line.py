from odoo import _, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    def _prepare_tms_values(self, **kwargs):
        ret = super()._prepare_tms_values(**kwargs)

        if self.order_id.state == "sale":
            stage = self.env.ref("tms.tms_stage_order_confirmed")
        elif self.state == "cancel":
            stage = self.env.ref("tms.tms_stage_order_cancelled")
        else:
            stage = self.env.ref("tms.tms_stage_order_draft")
        ret['stage_id']=stage.id
        return ret