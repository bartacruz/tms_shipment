from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.tools import format_datetime, formatLang


class Pricelist(models.Model):
    _inherit = "product.pricelist"
    
    tms_use_distance = fields.Boolean()
    