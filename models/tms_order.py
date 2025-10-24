# Copyright (C) 2025 Julio Santa Cruz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo import _, api, fields, models


class TMSOrder(models.Model):
    _inherit = "tms.order"

    customer_id = fields.Many2one("res.partner", related="sale_id.partner_id")

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