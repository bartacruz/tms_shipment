from odoo import _, api, fields, models


class TMSStage(models.Model):
    _inherit = "tms.driver"
    def _default_driver_location_id(self):
        return self.env["tms.driver.location"].search([],
            order="sequence asc",
            limit=1,
        )
        
    driver_location_id = fields.Many2one(
        "tms.driver.location",
        string="Driver Location",
        index=True,
        copy=False,
        default=_default_driver_location_id,
        group_expand="_read_group_driver_location_ids",
    
    )
    
    def _read_group_driver_location_ids(self,locations,domain,order):
        return self.env['tms.driver.location'].search([],order=order)
    
    def _populate_driver_location_id(self):
        for record in self:
            if not record.driver_location_id:
                record.driver_location_id = record._default_driver_location_id()
    

