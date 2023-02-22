import pytz as tz
from odoo import api, fields, models, _    # type: ignore
from odoo.exceptions import UserError    # type: ignore
from zk import ZK    # type: ignore
from odoo.addons import decimal_precision as dp    # type: ignore
UNIT = dp.get_precision("Location")
utc_zone = tz.timezone('UTC')


class AttendanceMachine(models.Model):
    _name = 'attendance.machine'
    _description = "Attendance Machine"

    name = fields.Char(string='Machine Name', required=True)
    domain = fields.Char(string='Device DNS/IP')
    cm_port = fields.Char(string='Communication Port', default=4370)
    last_record = fields.Integer(string='Last Record')
    attendance_count = fields.Integer(
        string='Count', compute='_compute_attendance_count')

    machine_nm = fields.Char(string='Machine Name')
    machine_fw = fields.Char(string='Firmware')
    machine_sr = fields.Char(string='Serial No:')
    machine_pt = fields.Char(string='Platform')
    machine_st = fields.Char(string='Status')

    machine_latitude = fields.Float("Latitude")
    machine_longitude = fields.Float("Longitude")


    def run_schedules(self):
        for record in self:
            record.fetch_attendance()
            record.process_data()


    @api.model
    def _tz_get(self):
        return [(x, x) for x in tz.all_timezones]

    tz_data = fields.Selection(_tz_get, string='Timezone', required=True,
                               default=lambda self: self.env.user.tz or 'UTC')

    @api.constrains('cm_port')
    def _check_comp_min(self):
        for record in self:
            try:
                if int(record.cm_port) >= 65535 or int(record.cm_port) < 101:
                    raise UserError(
                        'Port number sould be in between 100 and 65535')
            except ValueError:
                raise UserError(
                    'Not a valid port number. Port number sould be in between 100 and 65535.')

    machine_type = fields.Selection([
        ('zk', 'ZKteco'),
        ('app', 'Mobile App'),
    ], string='Type', required=True)

    def _compute_attendance_count(self):
        for record in self:
            record.attendance_count = len(
                self.env['attendance.machine.capture'].search([('machine_id', '=', self.id)]))

    def zk_connection(self):
        connection = None
        zk = ZK(f"""{self.domain}""", port=int(self.cm_port),
                timeout=5, password=0, force_udp=False, ommit_ping=True)
        connection = zk.connect()
        connection.disable_device()
        return connection

    def enroll_user(self, code, name):
        for record in self:
            connection = record.zk_connection()
            if not any(map((lambda user: user.uid == code), connection.get_users())):
                connection.set_user(
                    uid=code, name=name, password='1234', group_id='', user_id=str(code), card=0)
            connection.enable_device()

    def test_connectivity(self):
        try:
            connection = self.zk_connection()
            self.write({
                'machine_st': 'success',
                'machine_nm': connection.get_device_name(),
                'machine_fw': connection.get_firmware_version(),
                'machine_sr': connection.get_serialnumber(),
                'machine_pt': connection.get_platform()
            })
        except:
            raise UserError('Machine Not Connected')

    def fetch_attendance(self):
        connection = self.zk_connection()
        attendances = connection.get_attendance()
        for record in attendances:
            if record.uid > self.last_record:
                time = tz.timezone(self.tz_data).localize(record.timestamp)
                utc_time = time.astimezone(utc_zone)

                vals = {
                    'machine_id': self.id,
                    'serial': record.uid,
                    'user_code': record.user_id,
                    'time_stamp': utc_time.replace(tzinfo=None),
                    'status': record.status,
                    'punch': record.punch,
                    'processed': False
                }
                # raise UserError(str(vals))
                self.env['attendance.machine.capture'].create(vals)
        self.write({
            'last_record': record.uid
        })
        # except:
        #     return True

    def process_data(self):
        capture_ids = self.env['attendance.machine.capture'].search(
            [('machine_id', '=', self.id), ('processed', '=', False)], order='time_stamp asc')
        for record in capture_ids:
            employee_id = self.env['hr.employee'].search(
                [('barcode', '=', record.user_code)], limit=1)
            if employee_id:
                employee_id.mark_attendance_once(
                    record.machine_id, record.time_stamp)
                record.write({
                    'processed': True
                })

    def process_checkout(self):
        return
        attendence_ids = self.env['hr.attendance'].search(
            [('check_out', '=', False)])
        for record in attendence_ids:
            record.write({
                'check_out': record.check_in.replace(hour=13, minute=29, second=59)
            })


class MachineRecord(models.Model):
    _name = 'attendance.machine.capture'
    _description = 'Attendace Capture'
    _rec_name = 'serial'

    machine_id = fields.Many2one('attendance.machine', string='Machine')
    serial = fields.Integer(string='Serial')
    user_code = fields.Char(string='User Code')
    time_stamp = fields.Datetime(string='Time Stamp')
    status = fields.Integer(string='Status')
    punch = fields.Integer(string='Punch')
    processed = fields.Boolean(string='Processed')
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', compute='_compute_employee', store=True)

    @api.depends('user_code')
    def _compute_employee(self):
        for record in self:
            record.employee_id = self.env['hr.employee'].search(
                [('barcode', '=', record.user_code)], limit=1)


class AttendenceProcess(models.TransientModel):
    _name = 'process.attendance.wizard'
    _description = "Process Attendance Wizard"

    def process_attendance(self):
        machine_ids = self.env['attendance.machine'].search([])
        for record in machine_ids:
            record.fetch_attendance()
            record.process_data()
