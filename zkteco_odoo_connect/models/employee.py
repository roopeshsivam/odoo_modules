from odoo.exceptions import UserError     # type: ignore
from odoo import api, fields, models, tools, _    # type: ignore
import datetime as dt
import logging
_logger = logging.getLogger(__name__)


class EmployeeAttendance(models.Model):
    _inherit = 'hr.employee'

    machine_ids = fields.Many2many(
        'attendance.machine', string='Enrolled Machines')

    def enroll_user(self):
        for record in self:
            if not record.machine_ids.ids:
                raise UserError(
                    'Atleast one machine should be selected to enroll')
            try:
                code = int(record.barcode)
            except:
                raise UserError(
                    'Employee code is not valid, shoud be a number with atleast 4 digits')
            record.machine_ids.filtered(
                lambda r: r.enroll_user(code, record.name))

    def mark_attendance_once(self, machine_id, time_stamp):
        attendance = self.env['hr.attendance']

        if not self.last_attendance_id:
            attendance.create({
                'employee_id': self.id,
                'check_in': time_stamp,
                'machine_id': machine_id.id,
            })
            return True
        if self.last_attendance_id and not self.last_attendance_id.check_out:
            if self.last_attendance_id.check_in == time_stamp:
                return False
            if self.last_attendance_id.check_in.date() == time_stamp.date():
                self.last_attendance_id.update({
                    'check_out': time_stamp,
                })
                return True
            if self.last_attendance_id.check_in.date() < time_stamp.date():
                date = self.last_attendance_id.check_in + \
                    dt.timedelta(seconds=1)
                self.last_attendance_id.update({
                    'check_out': date,
                })
                attendance.create({
                    'employee_id': self.id,
                    'check_in': time_stamp,
                    'machine_id': machine_id.id,
                })
                return True
        if self.last_attendance_id.check_out and self.last_attendance_id.check_out.date() == time_stamp.date():
            if self.last_attendance_id.check_out.time() < time_stamp.time():
                self.last_attendance_id.update({
                    'check_out': time_stamp,
                })
                return True

        if self.last_attendance_id.check_out and self.last_attendance_id.check_out.date() < time_stamp.date():
            attendance.create({
                'employee_id': self.id,
                'check_in': time_stamp,
                'machine_id': machine_id.id,
            })
            return True

    def mark_attendance(self, machine_id, time_stamp):
        _logger.info(self.name)

        attendance = self.env['hr.attendance']
        if self.last_attendance_id and self.last_attendance_id.check_out and time_stamp.time() <= dt.time(13, 30, 0):
            _logger.info('1')
            attendance.create({
                'employee_id': self.id,
                'check_in': time_stamp,
                'machine_id': machine_id
            })
        elif self.last_attendance_id and not self.last_attendance_id.check_out:
            _logger.info('2')
            if self.last_attendance_id.check_in.date() == time_stamp.date():
                _logger.info('3')
                self.last_attendance_id.write({
                    'check_out': time_stamp,
                    'machine_id': machine_id
                })
            elif self.last_attendance_id.check_in.date() <= time_stamp.date():
                _logger.info('4')
                date = self.last_attendance_id.check_in.replace(
                    hour=15, minute=31, second=0)
                self.last_attendance_id.write({
                    'check_out': date,
                    'machine_id': machine_id
                })
                attendance.create({
                    'employee_id': self.id,
                    'check_in': time_stamp,
                    'machine_id': machine_id
                })
        elif not self.last_attendance_id:
            _logger.info('5')
            attendance.create({
                'employee_id': self.id,
                'check_in': time_stamp,
                'machine_id': machine_id
            })
