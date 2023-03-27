# -*- coding: utf-8 -*-
from odoo import models, api, _
from collections import defaultdict
from odoo.exceptions import AccessError


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    # override
    @api.model
    def check(self, mode, values=None):
        """ Inherited to allow users to preview documents """
        if self.env.user.has_group('binary_file_preview.group_data_manager'):
            return True
        else:
            return super(IrAttachment, self).check(mode, values)          


