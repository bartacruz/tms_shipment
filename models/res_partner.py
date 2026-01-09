from odoo import api, fields, models,_



class ResPartner(models.Model):
    _inherit = "res.partner"
    _rec_names_search = ['alias_name', 'complete_name', 'email', 'ref', 'vat', 'company_registry']  # TODO vat must be sanitized the same way for storing/searching
    
    alias_name = fields.Char(_('Alias'))

    @api.depends('alias_name')
    @api.depends_context('show_alias')
    def _compute_display_name(self):
        super()._compute_display_name()
        print("CONTEXT", self._context.get('show_alias'))
        if not self._context.get('show_alias'):
            return
        for record in self:
            if record.alias_name:
                record.display_name = "["+record.alias_name+"] " + record.display_name 
    
    
    # @api.depends('driver_ids')
    # def _compute_driver_id(self):
    #     for record in self:
    #         if len(record.driver_ids) > 0:
    #             record.driver_id = record.driver_ids[0].id
    #         else:
    #             record.driver_id = False
    
    # def _inverse_driver_id(self):
    #     for record in self:
    #         if len(record.driver_ids) > 0:
    #             driver = self.env['tms.driver'].browse(record.driver_ids[0])
    #             driver.partner_id = False
    #         record.driver_id.partner_id=record
                                                        

    def toggle_location(self):
        for record in self:
            record.tms_location = not record.tms_location