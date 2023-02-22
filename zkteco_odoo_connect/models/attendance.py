# -*- coding: utf-8 -*-
from odoo import fields, models, _    # type: ignore


class HRAttendance(models.Model):
    _inherit = 'hr.attendance'

    machine_id = fields.Many2one('attencance.machine', string='Machine')
