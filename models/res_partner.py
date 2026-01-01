from odoo import api, fields, models



class ResPartner(models.Model):
    _inherit = "res.partner"
    
    driver_ids = fields.One2many('tms.driver', 'partner_id')
    driver_id = fields.Many2one('tms.driver', compute='_compute_driver_id', inverse='_inverse_driver_id')
    
    @api.depends('driver_ids')
    def _compute_driver_id(self):
        for record in self:
            if len(record.driver_ids) > 0:
                record.driver_id = record.driver_ids[0].id
            else:
                record.driver_id = False
    
    def _inverse_driver_id(self):
        for record in self:
            if len(record.driver_ids) > 0:
                driver = self.env['tms.driver'].browse(record.driver_ids[0])
                driver.partner_id = False
            record.driver_id.partner_id=record
                                                        

    def toggle_location(self):
        for record in self:
            record.tms_location = not record.tms_location