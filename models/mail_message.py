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
            #tms_order.message_post(**self._get_gateway_thread_message_vals())
            if "Confirmar" in self.body:
                tms_order.driver_rejected=False
                tms_order.stage_id = self.env.ref("tms.tms_stage_order_confirmed")
                body = 'Confirmación recibida.\nNos estaremos contactando para mas detalles.'
            else:
                tms_order.driver_rejected=True
                if tms_order.is_active:
                    tms_order.stage_id = self.env.ref("tms.tms_stage_order_draft")
                body = 'Cancelación recibida.'
            tms_order._send_whatsapp(self.author_id,body=body)
        return ret
    