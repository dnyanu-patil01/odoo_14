from odoo import models, fields, SUPERUSER_ID, api,tools
from odoo.fields import Field
import logging
import base64,json
from odoo.http import request
from datetime import datetime
from odoo.exceptions import MissingError

_logger = logging.getLogger(__name__)

BLOCKED_FIELDS = [
'id', 'create_uid', 'create_date', 'write_uid', 'write_date','message_is_follower',
'display_name', '__last_update', 'message_partner_ids', 'message_follower_ids','message_ids',
]

class mail_thread_capture_json(models.AbstractModel):
    _name='mail.thread'
    _inherit='mail.thread'
    _description = 'Capture JSON Values'

    _notes_fields_to_ignore = []

    
    def init(self):
        cr = self._cr
        sql = """
            DO $$
                BEGIN
                    BEGIN
                        ALTER TABLE mail_message ADD COLUMN audit_log json;
                    EXCEPTION
                        WHEN duplicate_column THEN RAISE NOTICE 'column audit_log already exists in mail_message';
                    END;
                END;
            $$
        """
        cr.execute(sql)

        
    @tools.ormcache('self.env.uid', 'self.env.su')
    def _get_tracked_fields(self):
        """ Return the set of tracked fields names for the current model. """
        fields = {
            name
            for name, field in self._fields.items()
            if (name not in BLOCKED_FIELDS)
        }
        return fields and set(self.fields_get(fields))

    def message_track(self, tracked_fields, initial_values):
        """ Track updated values. Comparing the initial and current values of
        the fields given in tracked_fields, it generates a message containing
        the updated values. This message can be linked to a mail.message.subtype
        given by the ``_track_subtype`` method.

        :param tracked_fields: iterable of field names to track
        :param initial_values: mapping {record_id: {field_name: value}}
        :return: mapping {record_id: (changed_field_names, tracking_value_ids)}
            containing existing records only
        """
        if not tracked_fields:
            return True

        tracked_fields = self.fields_get(tracked_fields)
        tracking = dict()
        for record in self:
            try:
                tracking[record.id] = record._message_track(tracked_fields, initial_values[record.id])
            except MissingError:
                continue

        for record in self:
            changes, tracking_value_ids = tracking.get(record.id, (None, None))
            if not changes:
                continue

            # find subtypes and post messages or log if no subtype found
            subtype = False
            # By passing this key, that allows to let the subtype empty and so don't sent email because partners_to_notify from mail_message._notify will be empty
            if not self._context.get('mail_track_log_only'):
                subtype = record._track_subtype(dict((col_name, initial_values[record.id][col_name]) for col_name in changes))
            if subtype:
                if not subtype.exists():
                    _logger.debug('subtype "%s" not found' % subtype.name)
                    continue
                record.message_post(subtype_id=subtype.id, tracking_value_ids=tracking_value_ids)
            elif tracking_value_ids:
                new_message=record._message_log(tracking_value_ids=tracking_value_ids)
                json_data={}
                for rec in new_message.message_format()[0]['tracking_value_ids']:
                	json_data.update({rec.get('changed_field'):{'new_value':rec.get('new_value'),'old_value':rec.get('old_value'),'col_info':rec.get('changed_field')}})
                self.env.cr.execute("update mail_message set audit_log = %s where id = %s",(json.dumps(json_data),new_message.id))
        return tracking
mail_thread_capture_json

class MailTracking(models.Model):
    _inherit = 'mail.tracking.value'

    @api.model
    def create_tracking_values(self, initial_value, new_value, col_name, col_info, tracking_sequence, model_name):
        tracked = True

        field = self.env['ir.model.fields']._get(model_name, col_name)
        if not field:
            return

        values = {'field': field.id, 'field_desc': col_info['string'], 'field_type': col_info['type'], 'tracking_sequence': tracking_sequence}

        if col_info['type'] in ['integer', 'float', 'char', 'text', 'datetime', 'monetary']:
            values.update({
                'old_value_%s' % col_info['type']: initial_value,
                'new_value_%s' % col_info['type']: new_value
            })
        elif col_info['type'] == 'date':
            values.update({
                'old_value_datetime': initial_value and fields.Datetime.to_string(datetime.combine(fields.Date.from_string(initial_value), datetime.min.time())) or False,
                'new_value_datetime': new_value and fields.Datetime.to_string(datetime.combine(fields.Date.from_string(new_value), datetime.min.time())) or False,
            })
        elif col_info['type'] == 'boolean':
            values.update({
                'old_value_integer': initial_value,
                'new_value_integer': new_value
            })
        elif col_info['type'] == 'selection':
            values.update({
                'old_value_char': initial_value and dict(col_info['selection'])[initial_value] or '',
                'new_value_char': new_value and dict(col_info['selection'])[new_value] or ''
            })
        elif col_info['type'] == 'many2one':
            values.update({
                'old_value_integer': initial_value and initial_value.id or 0,
                'new_value_integer': new_value and new_value.id or 0,
                'old_value_char': initial_value and initial_value.sudo().name_get()[0][1] or '',
                'new_value_char': new_value and new_value.sudo().name_get()[0][1] or ''
            })
        elif col_info['type'] == 'one2many' or col_info['type'] == 'many2many':
            values.update({
                'old_value_char': str(initial_value) and str(initial_value) or 0,
                'new_value_char': str(new_value) and str(new_value) or 0,
            })
        else:
            tracked = False

        if tracked:
            return values
        return {}