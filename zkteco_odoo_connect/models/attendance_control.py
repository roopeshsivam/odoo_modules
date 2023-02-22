# -*- coding: utf-8 -*-
from odoo import models, _     # type: ignore


class CollectAttendance(models.TransientModel):
    _name = 'hr.attendence.collect'
    _description = 'Attendance Collection'

    def mark_attendance(self, time, barcode):
        attendance = False
        if barcode:
            employee = self.env['hr.employee'].search(
                [('barcode', '=', barcode)], limit=1)
            attendance = self.env['hr.attendance'].search(
                [('employee_id', '=', employee.id), ('check_out', '=', False)])

        if employee and attendance:
            attendance.write({
                'check_out': time
            })
        if employee and not attendance:
            vals = {
                'employee_id': employee.id,
                'check_in': time
            }
            self.env['hr.attendance'].create(vals)
