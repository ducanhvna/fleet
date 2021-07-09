# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class FleetProject(models.Model):
    _name = 'fleet.project'
    _description = 'Dự án'
    _order = 'name'

    name = fields.Char(string='Tên dự án', required=True)


class FleetCategory(models.Model):
    _name = 'fleet.category'
    _description = 'Hạng mục'
    _order = 'name'

    name = fields.Char(string='Tên hạng mục', required=True)


class FleetLocation(models.Model):
    _name = 'fleet.location'
    _description = 'Địa điểm'
    _order = 'name'

    name = fields.Char(string='Tên địa điểm', required=True)


class FleetCar(models.Model):
    _name = 'fleet.car'
    _description = 'Phương Tiện'
    _order = 'name'

    name = fields.Char(string='Tên phương tiện', required=True)
    license_plate = fields.Char(string='Biển số', required=True)
    acquisition_date = fields.Date('Ngày đăng kiểm')
    vin_sn = fields.Char('Số khung', copy=False)
    seats = fields.Integer('Số ghế')
    model_year = fields.Char('Đời xe')
    color = fields.Char('Màu xe')

    fleet_trip_ids = fields.One2many('fleet.trip', 'car_id', 'Danh sách hành trình', readonly=True)

    def name_get(self):
        self.browse(self.ids).read(['name', 'license_plate'])
        return [(car.id, '%s%s' % (car.license_plate and '[%s] ' % car.license_plate or '', car.name))
                for car in self]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    section = fields.Char(string='Tiết diện')
    product_length = fields.Integer(string='Dài')