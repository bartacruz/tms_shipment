from odoo import fields, models



class ResPartner(models.Model):
    _inherit = "res.partner"

    def toggle_location(self):
        for record in self:
            record.tms_location = not record.tms_location