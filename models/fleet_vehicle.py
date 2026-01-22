from odoo import models,fields,api,_

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    operation = fields.Selection(selection_add=[('trailer','Trailer')] )
    trailer_id = fields.Many2one('fleet.vehicle', context = {'default_operation': 'trailer'}, domain = "[('operation','=','trailer')]")
    truck_ids = fields.One2many('fleet.vehicle', 'trailer_id')
    truck_id = fields.Many2one('fleet.vehicle', compute='_compute_truck', store=True)
    
    @api.depends('truck_ids')
    def _compute_truck(self):
        for record in self:
            if len(record.truck_ids) > 0:
                record.truck_id = record.truck_ids[0]
                record.driver_id = record.truck_id.driver_id
                record.tms_driver_id = record.truck_id.tms_driver_id
            else:
                record.truck_id = False
                if record.opeation == 'trailer':
                    record.driver_id = False
                    record.tms_driver_id = False
    
    # def _inverse_trailer(self):
    #     for record in self:
    #         if len(record.truck_ids) > 0:
                
    #             trailers = self.search([ ('truck_id','=',record.id)])
    #             trailers.truck_id = record
                
    # @api.onchange('trailer_id')
    # def _update_trailer(self):
    #     for record in self:
    #         print("record",record,record.trailer_id)
    #         if record.trailer_id:
    #             record.trailer_id.truck_id = record
    #         else:
    #             # Unset old relation
    #             trailers = self.search([ ('truck_id','=',record.id)])
    #             trailers.truck_id = False

    @api.depends('model_id.brand_id.name', 'model_id.name', 'license_plate')
    def _compute_vehicle_name(self):
        for record in self:
            record.name = (record.license_plate or _('No Plate'))