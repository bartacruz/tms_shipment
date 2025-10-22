# Copyright (C) 2025 Julio Santa Cruz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo import _, api, fields, models


class TMSOrder(models.Model):
    _inherit = "tms.order"

    @api.model
    def write(self, vals):
        for order in self:
            if "stage_id" in vals:
                actives = self.env["tms.stage"].search([("is_active", "=", True)]).ids
                
                print("Stage change to ", vals["stage_id"], " actives: ", actives)
                if vals["stage_id"] in actives:
                    if not order.start_trip:
                        print("starting trip")
                        vals["start_trip"] = True
                        vals["date_start"] = order.date_start or datetime.now()
                    else:
                        print("already started")
                    
        return super().write(vals)