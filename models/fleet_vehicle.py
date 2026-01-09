from odoo import models,fields,api,_

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    operation = fields.Selection(selection_add=[('trailer','Trailer')] )
    trailer_id = fields.Many2one('fleet.vehicle', context = {'default_operation': 'trailer'}, domain = "[('operation','=','trailer')]")
    truck_id = fields.Many2one('fleet.vehicle', context = {'default_operation': 'cargo'}, domain = "[('operation','=','cargo')]")

    @api.onchange('trailer_id')
    def _update_trailer(self):
        for record in self:
            print("record",record,record.trailer_id)
            if record.trailer_id:
                record.trailer_id.truck_id = record
            else:
                # Unset old relation
                trailers = self.search([ ('truck_id','=',record.id)])
                trailers.truck_id = False

    @api.depends('model_id.brand_id.name', 'model_id.name', 'license_plate')
    def _compute_vehicle_name(self):
        for record in self:
            record.name = (record.license_plate or _('No Plate'))