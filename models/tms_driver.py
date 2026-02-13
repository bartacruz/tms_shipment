from odoo import _, api, fields, models


class TMSDriver(models.Model):
    _inherit = "tms.driver"
    _order = "stage_id,sequence, name, id"
    
    # TODO: use a configuration setting for this.
    STAGE_BASE = 5
    STAGE_ASSIGNED = 6
    
    def _default_driver_location_id(self):
        return self.env["tms.driver.location"].search([],
            order="sequence asc",
            limit=1,
        )
    driver_type=fields.Selection(default='terrestrial')
    driver_location_id = fields.Many2one(
        "tms.driver.location",
        string="Driver Location",
        index=True,
        copy=False,
        default=_default_driver_location_id,
        group_expand="_read_group_driver_location_ids",
    
    )
    vehicle_ids = fields.One2many("fleet.vehicle", "tms_driver_id")
    vehicle_id = fields.Many2one('fleet.vehicle',compute='_compute_tms_vehicle', inverse='_inverse_tms_vehicle', domain="[('operation','=','cargo')]")
    trailer_id = fields.Many2one('fleet.vehicle', related='vehicle_id.trailer_id', readonly=True, store=True)
    
    trips_ids_count = fields.Integer(compute='_compute_trips_ids')
    active_tms_order_id = fields.Many2one("tms.order", compute="_compute_active_tms_order", store=True)
    sequence = fields.Integer(default=100)
    
    @api.depends('trips_ids')
    def _compute_trips_ids(self):
        for record in self:
            record.trips_ids_count = len(record.trips_ids)
        
    @api.depends('vehicle_ids')
    def _compute_tms_vehicle(self):
        for record in self:
            vehicles = [ x for x in record.vehicle_ids if x.operation == 'cargo']
            if len(vehicles) > 0:
                record.vehicle_id = vehicles[0].id
            else:
                record.vehicle_id = False
    
    def _inverse_tms_vehicle(self):
        for record in self:
            old = record.env['fleet.vehicle'].search([ ('tms_driver_id','=',record.id) ])
            old.tms_driver_id=False
            print("inv vehicle. old:",old,"new:",record.vehicle_id)
            if record.vehicle_id:
                record.vehicle_id.tms_driver_id=record.id
                record.vehicle_id.trailer_id.tms_driver_id=record.id
                
        
    def write(self, values):
        location_id = values.get('driver_location_id')
        if location_id:
            
            if location_id == self._default_driver_location_id().id :
                values['sequence'] = 100
            else:
                nloc = self.env["tms.driver.location"].browse(location_id)
                values['sequence'] =nloc.driver_count +1
            
        result = super().write(values)
        if 'stage_id' in values:
            # self.env['bus.bus']._sendone('broadcast','driver_changed',{'id':self.id})
            self.env['bus.bus']._sendone('tms','driver_changed',{'id':self.id})
            
    def _read_group_driver_location_ids(self,locations,domain,order):
        return self.env['tms.driver.location'].search([],order=order)
    
    def _populate_driver_location_id(self):
        for record in self:
            if not record.driver_location_id:
                record.driver_location_id = record._default_driver_location_id()
    
    @api.depends('trips_ids')
    def _compute_active_tms_order(self):
        for record in self:
            old_active = record._origin.active_tms_order_id
            record.active_tms_order_id = record.trips_ids.search([('driver_id','=',record.id),('is_active','=',True)],limit=1)
            if record.active_tms_order_id:
                record.driver_location_id = 1
                record.stage_id = self.STAGE_ASSIGNED
            elif record.stage_id.id == self.STAGE_ASSIGNED or old_active:
                # Was assigned but not anymore => return to base
                record.stage_id = self.STAGE_BASE
            
    def action_view_tms_orders(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "tms.order",
            "view_mode": "tree,form",
            "domain": [("driver_id", "=", self.id)],
            "name": "TMS Orders %s" % self.name,
        }        
    
    ### super methods for view compatiblility ###
    
    def action_view_partner_with_same_bank(self):
        return self.partner_id.action_view_partner_with_same_bank()
    
    def action_view_cpe(self):
        return self.partner_id.action_view_cpe()
    
    def action_view_sale_order(self):
        return self.partner_id.action_view_sale_order()

    def action_view_partner_invoices(self):
        return self.partner_id.action_view_partner_invoices()
    def l10n_ar_afipws_fe_min_ammount(self):
        return self.partner_id.l10n_ar_afipws_fe_min_ammount()