# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta, date


class EmployeeUsers(models.Model):
    _inherit = 'res.users'

    employee_id = fields.Many2one('hr.employee',
                                  string='Related Employee', ondelete='restrict',
                                  help='Employee-related data of the user', auto_join=True)

    @api.model
    def create(self, vals):
        result = super(EmployeeUsers, self).create(vals)
        result['employee_id'] = self.env['hr.employee'].create({'name': result['name'],
                                                                'user_id': result['id'],
                                                                'address_home_id': result['partner_id'].id})
        return result


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _order = 'id desc'

    trip_ids = fields.One2many('fleet.trip', 'employee_id')
    trip_count = fields.Integer(string='Số chuyến hôm nay', compute='_compute_trip_count')
    trip_done_count = fields.Integer(string='Số chuyến hoàn thành', compute='_compute_trip_count')
    other_info = fields.Char(string='Thông tin khác')
    salary_last_month = fields.Float(string='Lương tháng trước')
    message_ids = fields.One2many('mail.message', 'res_id', string='Ghi chú')
    equipment_id = fields.Many2one('maintenance.equipment', string='Phụ trách xe')

    @api.depends('trip_ids')
    def _compute_trip_count(self):
        for rec in self:
            today = date.today()
            trip_ids = rec.trip_ids.filtered(lambda x: x.schedule_date)
            rec.trip_count = len(trip_ids.filtered(lambda x: x.schedule_date == today))
            rec.trip_done_count = len(trip_ids.filtered(lambda x: x.schedule_date == today and x.state =='3_done'))