# -*- coding: utf-8 -*-
import base64
import json
import re
from odoo import http, tools, _, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.website.controllers.main import Website
import zipfile
import os
from io import BytesIO
import shutil
import tempfile
from datetime import datetime
from odoo.exceptions import MissingError
import ast


class Website(Website):

    @http.route(auth="user")
    def index(self, **kw):
        return super(Website, self).index(**kw)

