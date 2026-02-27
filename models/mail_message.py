import logging

from odoo import api, fields, models,_

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = 'mail.message'
    
    tms_order_id = fields.Many2one('tms.order',_('Related TMS Order'))
    
    def write(self, vals):
        super().write(vals)
        if 'gateway_message_id' in vals and self.body.find("Button:"):
            _logger.warning('WA write: %s detecte un boton',self)
            template_message = self.gateway_message_id
            _logger.warning('WA write: el mensaje es',template_message)
            tms_order = template_message.tms_order_id
            _logger.warning('WA write: la orden es',tms_order)
            if self.body.find("Confirmar"):
                tms_order.stage_id = self.env.ref("tms.tms_stage_order_confirmed")
            
            
    