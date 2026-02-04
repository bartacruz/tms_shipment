from odoo import api, fields, models,_



class ResPartner(models.Model):
    _inherit = "res.partner"
    _rec_names_search = ['alias_name', 'complete_name', 'email', 'ref', 'vat', 'company_registry']  # TODO vat must be sanitized the same way for storing/searching
    
    alias_name = fields.Char(_('Alias'))
    tms_driver_ids = fields.One2many('tms.driver','partner_id')
    tms_driver_id = fields.Many2one('tms.driver', compute='_compute_tms_driver_id', readonly=True)
    
    

    @api.depends('alias_name')
    @api.depends_context('show_alias')
    def _compute_display_name(self):
        super()._compute_display_name()
        if not self._context.get('show_alias'):
            return
        for record in self:
            if record.alias_name:
                record.display_name = "["+record.alias_name+"] " + record.display_name 
    
    @api.depends('tms_driver_ids')
    def _compute_tms_driver_id(self):
        for record in self:
            if len(record.tms_driver_ids) > 0:
                record.tms_driver_id = record.tms_driver_ids[0].id
            else:
                record.tms_driver_id = False
    
    def action_view_cpe(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "afip.cpe",
            "view_mode": "tree,form",
            "domain": [("participants_ids", "in", self.id)],
            "name": "CPEs %s" % self.name,
        }
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