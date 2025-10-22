# Copyright (C) 2025 Julio Santa Cruz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class TMSStage(models.Model):
    _inherit = "tms.stage"

    is_active = fields.Boolean(
        help="An active stage enforces the trip has started",
    )

    
    