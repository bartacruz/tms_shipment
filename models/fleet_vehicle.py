from odoo import models,fields,api,_

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    @api.depends('model_id.brand_id.name', 'model_id.name', 'license_plate')
    def _compute_vehicle_name(self):
        for record in self:
            record.name = (record.license_plate or _('No Plate'))