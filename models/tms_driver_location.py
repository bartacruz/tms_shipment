from odoo import _, api, fields, models

class TMSDriverLocation(models.Model):
    _name = "tms.driver.location"
    _description = "Transport Management System Driver Location"
    _order = "sequence, name, id"
    
    name = fields.Char(required=True, translate=True)
    description = fields.Text(translate=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.user.company_id.id,
    )
    driver_ids = fields.One2many("tms.driver","driver_location_id")
    driver_count = fields.Integer("Driver Count", compute="_compute_driver_count")
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=1, help="Used to order stages. Lower is first.")
    
    fold = fields.Boolean(
        "Folded in Kanban",
        help="This stage is folded in the kanban view when "
        "there are no record in that stage to display.",
    )
    is_default = fields.Boolean(readonly=True, default=False)
    custom_color = fields.Char(
        "Color Code", default="#FFFFFF", help="Use Hex Code only Ex:-#FFFFFF"
    )
    
    def _compute_driver_count(self):
        for record in self:
            record.driver_count = len(record.driver_ids)
            
    
    
    