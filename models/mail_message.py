import logging

from odoo import api, fields, models,_

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = 'mail.message'
    
    tms_order_id = fields.Many2one('tms.order',_('Related TMS Order'))
    
    def write(self, vals):
        ret = super().write(vals)
        if 'gateway_message_id' in vals and self.body.find("Button:"):
            _logger.warning('WA write: %s detecte un boton %s || %s',self,vals['gateway_message_id'],self.gateway_message_id)
            template_message = self.gateway_message_id
            _logger.warning('WA write: el mensaje es %s',template_message)
            tms_order = template_message.tms_order_id
            _logger.warning('WA write: la orden es %s',tms_order)
            if self.body.find("Confirmar"):
                tms_order.stage_id = self.env.ref("tms.tms_stage_order_confirmed")
        return ret
            
            
    