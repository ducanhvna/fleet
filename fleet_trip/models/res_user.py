# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime


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

    trip_ids = fields.One2many('fleet.trip', 'employee_id')
    trip_count = fields.Integer(string='Số chuyến hôm nay', compute='_compute_trip_count')
    trip_done_count = fields.Integer(string='Số chuyến hoàn thành', compute='_compute_trip_count')

    @api.depends('trip_ids')
    def _compute_trip_count(self):
        for rec in self:
            today = datetime.date.today().strftime('%Y-%m-%d')
            rec.trip_count = len(rec.trip_ids.filtered(lambda x: today <= x.schedule_date >= today))
            rec.trip_done_count = len(rec.trip_ids.filtered(
                lambda x: today <= x.schedule_date >= today and x.state =='done'))