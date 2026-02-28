import logging
from markupsafe import Markup
from odoo import _,api, fields, models,SUPERUSER_ID
from pyzbar.pyzbar import decode
from PIL import Image
import base64
import io
_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    qr_codes = fields.One2many('qr.code','attachment_id')
    qr_scanned = fields.Boolean()
    
    
    def _extract_qr_codes(self):
        for record in self:
            print("_extract_qr_codes",record)
            
            if 'image' in record.mimetype:
                image = Image.open(io.BytesIO(base64.b64decode(record.datas)))
                decoded = decode(image)
                print("decoded",decoded)
                for r in decoded:
                    qr = record.qr_codes.create({
                        'attachment_id': record.id,
                        'code':r.data.decode('utf-8'),
                        'qr_type':r.type
                    })
                    _logger.info("Decoded attachment %s: %s %s",qr.attachment_id,qr.qr_type,qr.code)
            record.qr_scanned = True
    
class MailMessage(models.Model):
    _inherit = 'mail.message'
    
    qr_codes = fields.Many2many('qr.code', compute="_compute_qr_codes", store=True)
    tms_order_id = fields.Many2one('tms.order',_('Related TMS Order'))
    
    def _process_qr_code(self,qr):
        self.ensure_one()
        self.env[self.model].browse(self.res_id).message_post(
            author_id=SUPERUSER_ID,
            body=f'QR Code: {qr.code}',
            date=self.date,
            subtype_xmlid="mail.mt_comment",
            message_type="comment",
            gateway_notifications=[],
        )
        
        
        # CPE DETECTION
        if len(qr.code) == 11 and qr.code.startswith('1'):
            # CPE
            order = self.author_id.tms_driver_id.active_tms_order_id
            if not order:
                _logger.warning("Received CPE #%s from %s but there's no active order to attach to.",qr.code,self.author_id)
                return
            print("Es CPE y la orden está activa!",qr.code,order)
            order.message_post(
                author_id=self.author_id.id,
                body=f'{self.body}\n\nQR Code: {qr.code}',
                gateway_type=self.gateway_type,
                date=self.date,
                subtype_xmlid="mail.mt_comment",
                message_type="comment",
                attachment_ids=self.attachment_ids.ids,
                gateway_notifications=[],  # Avoid sending notifications
            )
            if not order.cpe_id:
                cpe = self.env['afip.cpe'].search([ '|',('ctg_number','=',qr.code),('name','=',qr.code) ])
                print("Cpe: ",cpe)
                if not cpe:
                    print("Creando CPE",qr.code)
                    cpe = self.env['afip.cpe'].create({
                        'name':qr.code,
                        'tms_order_id': order.id,
                    })
                    order.cpe_id = cpe
                else:        
                    order.cpe_id = cpe
                    cpe.tms_order_id = order
                    cpe.action_update_cpe(force=True)
                
                message1 = _(
                    "Carta de porte %s recibida por QR",
                    Markup(
                        f"""<a href=# data-oe-model=afip.cpe data-oe-id={cpe.id}"""
                        f""">{cpe.name}</a>"""
                    ),
                )                
                order.sudo().message_post(body=message1)

                message2 = Markup(f'<p>La carta de porte {qr.code} ha sido recibida y asignada al viaje {order.name}.<br/>Muchas gracias.</p>')
                self.sudo().env[self.model].browse(self.res_id).message_post(author_id=SUPERUSER_ID,body=message2, gateway_notifications=[],subtype_xmlid="mail.mt_comment",
                message_type="comment",)
                
    @api.depends('attachment_ids')
    def _compute_qr_codes(self):
        for record in self:
            print("_compute_qr_codes",record)
            for a in record.attachment_ids:
                if not a.qr_scanned:
                    a._extract_qr_codes()
                    for q in a.qr_codes:
                        record.sudo()._process_qr_code(q)
                record.qr_codes |= a.qr_codes
                
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
        