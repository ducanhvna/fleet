# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta, date
# from odoo.addons.rest_api.controllers.main import generate_token, token_store
from ...rest_api.controllers.main import generate_token, token_store
import time
import sys


class EmployeeUsers(models.Model):
    _inherit = 'res.users'

    employee_id = fields.Many2one('hr.employee',
                                  string='Related Employee', ondelete='restrict',
                                  help='Employee-related data of the user', auto_join=True)
    equipment_ids = fields.One2many("maintenance.equipment", "owner_user_id")

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
    contract_date = fields.Date(string='Ngày kí hợp đồng')
    payroll_ids = fields.One2many('hr.employee.payroll', 'employee_id', string='Thông tin thu nhập')
    payroll_total_amount = fields.Float(string='Tổng thu nhập', compute="_compute_payroll_total_amount")

    @api.depends("payroll_ids")
    def _compute_payroll_total_amount(self):
        for rec in self:
            rec.payroll_total_amount = sum([line.total_amount for line in rec.payroll_ids])

    @api.depends('trip_ids')
    def _compute_trip_count(self):
        for rec in self:
            today = date.today()
            trip_ids = rec.trip_ids.filtered(lambda x: x.schedule_date)
            rec.trip_count = len(trip_ids.filtered(lambda x: x.schedule_date == today))
            rec.trip_done_count = len(trip_ids.filtered(lambda x: x.schedule_date == today and x.state =='3_done'))


class HrEmployeePayroll(models.Model):
    _name = 'hr.employee.payroll'
    _order = 'id desc'

    employee_id = fields.Many2one("hr.employee", string='Nhân viên')
    month = fields.Selection(
        [("1", "Tháng 1"), ("2", "Tháng 2"), ("3", "Tháng 3"), ("4", "Tháng 4"), ("5", "Tháng 5"), ("6", "Tháng 6"),
         ("7", "Tháng 7"), ("8", "Tháng 8"), ("9", "Tháng 9"), ("10", "Tháng 10"), ("11", "Tháng 11"),
         ("12", "Tháng 12")], string="Tháng", required=True)
    year = fields.Char(string='Năm', required=True, default=datetime.now().year)
    name = fields.Char(string='Ghi chú')
    payroll_amount = fields.Float(string='Lương', required=True)
    bonus_amount = fields.Float(string='Phụ cấp')
    total_amount = fields.Float(string='Tổng thu nhập', compute='_compute_total_amount')

    @api.onchange("month")
    def _onchange_month(self):
        if self.month and self.year and not self.name:
            self.name = f'Thu nhập {self.month}/{self.year}'

    @api.onchange("year")
    def _onchange_year(self):
        if self.month and self.year and not self.name:
            self.name = f'Thu nhập {self.month}/{self.year}'

    @api.depends("payroll_amount", "bonus_amount")
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = rec.payroll_amount + rec.bonus_amount


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