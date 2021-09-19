# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta, date
from odoo.addons.rest_api.controllers.main import generate_token, token_store
import time
import sys


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

    def create_by_api(self, name, email, password, company_id):
        user = self.create({
            'name': name or email,
            'login': email,
            'email': email,
            'password': password,
            'company_id': company_id.id,
            'company_ids': [(6, 0, [company_id.id])]
        })
        access_token = user.set_access_token()
        return access_token

    def get_expires_token(self):
        expires = sys.maxsize - time.time()
        expires_in, refresh_expires_in = expires, expires
        return expires_in, refresh_expires_in

    def set_access_token(self):
        if not self:
            return self
        self.ensure_one()
        env = self.env
        expires_in, refresh_expires_in = self.get_expires_token()
        access_token, refresh_token = generate_token(), generate_token()
        token_store.save_all_tokens(env=env, user_id=self.id, access_token=access_token, expires_in=expires_in,
                                    refresh_token=refresh_token, refresh_expires_in=refresh_expires_in)
        return access_token


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _order = 'id desc'

    trip_ids = fields.One2many('fleet.trip', 'employee_id')
    trip_count = fields.Integer(string='Số chuyến hôm nay', compute='_compute_trip_count')
    trip_done_count = fields.Integer(string='Số chuyến hoàn thành', compute='_compute_trip_count')
    other_info = fields.Char(string='Thông tin khác')
    salary_last_month = fields.Float(string='Lương tháng trước')
    message_ids = fields.One2many('mail.message', 'res_id', string='Ghi chú')
    # equipment_id = fields.Many2one('maintenance.equipment', string='Phụ trách xe')

    @api.depends('trip_ids')
    def _compute_trip_count(self):
        for rec in self:
            today = date.today()
            trip_ids = rec.trip_ids.filtered(lambda x: x.schedule_date)
            rec.trip_count = len(trip_ids.filtered(lambda x: x.schedule_date == today))
            rec.trip_done_count = len(trip_ids.filtered(lambda x: x.schedule_date == today and x.state =='3_done'))


class InheritResCompany(models.Model):
    _inherit = 'res.company'

    token_register_account = fields.Char('Token register account')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    token_register_account = fields.Char('Token register account')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        company = self.env.user.company_id
        res['token_register_account'] = company.token_register_account or ''
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        company = self.env.user.company_id
        company.sudo().write({
            'token_register_account': self.token_register_account or ''})