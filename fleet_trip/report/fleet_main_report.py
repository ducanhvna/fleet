# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError, ValidationError

MONTH_SELECTION = [('1', '1'),
                   ('2', '2'),
                   ('3', '3'),
                   ('4', '4'),
                   ('5', '5'),
                   ('6', '6'),
                   ('7', '7'),
                   ('8', '8'),
                   ('9', '9'),
                   ('10', '10'),
                   ('11', '11'),
                   ('12', '12')]


class FleetMainReport(models.Model):
    _name = 'fleet.main.report'
    _rec_name = 'equipment_id'
    _description = 'Chi phí phát sinh'
    _order = 'date desc'

    date = fields.Date(string='Thời gian', required=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Xe', required=True)
    invoice_amount = fields.Float(string='Phát sinh/Hóa đơn', default=0, digits=(16, 0))
    oil_amount = fields.Float(string="Tiền dầu", default=0, digits=(16, 0))
    machine_amount = fields.Float(string="Dầu máy", default=0, digits=(16, 0))

    day_time = fields.Char(string="Ngày", compute='_compute_date_time', store=True)
    month_time = fields.Char(string="Tháng", compute='_compute_date_time', store=True)
    year_time = fields.Char(string="Năm", compute='_compute_date_time', store=True)

    @api.depends("date")
    def _compute_date_time(self):
        for rec in self:
            if rec.date:
                rec.day_time = str(rec.date.day)
                rec.month_time = str(rec.date.month)
                rec.year_time = str(rec.date.year)


class FleetGrowReport(models.Model):
    _name = 'fleet.grow.report'
    _rec_name = 'equipment_id'
    _description = 'Chi phí vận tải'
    _order = 'create_date desc'

    month_time = fields.Selection(MONTH_SELECTION, string="Tháng", required=True)
    year_time = fields.Integer(string="Năm", required=True)
    year_time_str = fields.Char(string="Năm", compute='_compute_year_time_str')
    equipment_id = fields.Many2one('maintenance.equipment', string='Xe', required=True)
    total_amount = fields.Float(string='Tiền vận tải', required=True, default=0, digits=(16, 0))
    partner_id = fields.Many2one("res.partner", string="Công ty", required=True)

    @api.depends("year_time")
    def _compute_year_time_str(self):
        for rec in self:
            if rec.year_time:
                rec.year_time_str = str(rec.year_time)
            else:
                rec.year_time_str = False


class AdvanceMoneyReport(models.Model):
    _name = 'advance.money.report'
    _rec_name = 'date'
    _description = 'Ứng tiền'
    _order = 'date desc'

    date = fields.Date(string='Thời gian', required=True)
    employee_id = fields.Many2one('hr.employee', string='Người ứng')
    equipment_id = fields.Many2one('maintenance.equipment', string='Xe')
    total_amount = fields.Float(string='Tiền ứng', required=True, default=0, digits=(16, 0))

    day_time = fields.Char(string="Ngày", compute='_compute_date_time', store=True)
    month_time = fields.Char(string="Tháng", compute='_compute_date_time', store=True)
    year_time = fields.Char(string="Năm", compute='_compute_date_time', store=True)

    @api.depends("date")
    def _compute_date_time(self):
        for rec in self:
            if rec.date:
                rec.day_time = str(rec.date.day)
                rec.month_time = str(rec.date.month)
                rec.year_time = str(rec.date.year)


class SalaryMoneyReport(models.Model):
    _name = 'salary.money.report'
    _rec_name = 'equipment_id'
    _description = 'Tiền lương'
    _order = 'create_date desc'

    month_time = fields.Selection(MONTH_SELECTION, string="Tháng", required=True)
    year_time = fields.Integer(string="Năm", required=True)
    year_time_str = fields.Char(string="Năm", compute='_compute_year_time_str')
    equipment_id = fields.Many2one('maintenance.equipment', string='Xe', required=True)
    total_amount = fields.Float(string='Tiền lương', required=True, default=0, digits=(16, 0))

    @api.depends("year_time")
    def _compute_year_time_str(self):
        for rec in self:
            if rec.year_time:
                rec.year_time_str = str(rec.year_time)
            else:
                rec.year_time_str = False
