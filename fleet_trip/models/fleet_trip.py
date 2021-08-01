# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import base64
import requests


class FleetTrip(models.Model):
    _name = 'fleet.trip'
    _rec_name = 'equipment_id'
    _description = 'Hành trình vận tải'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    equipment_id = fields.Many2one('maintenance.equipment', string='Xe', required=True)
    location_id = fields.Many2one('fleet.location', 'Điểm xuất phát', required=True)
    location_dest_id = fields.Many2one('fleet.location', 'Điểm đích', required=True)
    eating_fee = fields.Monetary('Tiền ăn', required=True)
    law_money = fields.Monetary('Tiền luật', required=True)
    road_tiket_fee = fields.Monetary('Vé cầu đường', required=True)
    incurred_fee = fields.Monetary('Phát sinh')
    note = fields.Text('Ghi chú sửa chữa')
    fee_total = fields.Monetary('Tổng cộng')
    odometer_start = fields.Integer('Số CTM xuất phát', required=True)
    odometer_dest = fields.Integer('Số CTM điểm đích', required=True)
    odometer_end = fields.Integer('Số CTM quay về', required=True)
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True)
    state = fields.Selection([
        ('1_draft', 'Đang Chờ'),
        ('2_confirm', 'Đã Xuất Phát'),
        ('3_done', 'Hoàn Thành')
    ], string='Trạng thái', default='1_draft')
    schedule_date = fields.Date(string='Ngày thực hiện', required=True)
    start_date = fields.Datetime(string='Bắt đầu', readonly=True)
    end_date = fields.Datetime(string='Kết thúc', readonly=True)

    delivery_id = fields.Many2one('stock.delivery', string='Phiếu xuất kho')
    code = fields.Char(related='delivery_id.code', store=True)
    project_id = fields.Many2one(related='delivery_id.project_id')

    def do_start_trip(self):
        self.start_date = fields.Datetime.now()
        self.state = '2_confirm'

    def do_end_trip(self):
        self.end_date = fields.Datetime.now()
        self.state = '3_done'

    def do_odometer_start(self, odometer_start):
        # attachment_obj = self.env['ir.attachment']
        self.odometer_start = odometer_start

    def do_odometer_end(self, odometer_end, attachments=[]):
        self.odometer_end = odometer_end
        if not attachments:
            return True
        for attachment in attachments:
            datas = base64.b64encode(requests.get(attachment).content)
            self.env['ir.attachment'].create({
                'name': self.name,
                'datas': datas,
                'res_model': 'fleet.trip',
                'res_id': self.id,
            })


class StockDelvery(models.Model):
    _name = 'stock.delivery'
    _rec_name = 'code'
    _description = 'Phiếu xuất kho'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    code = fields.Char(string='Số phiếu', required=True)
    project_id = fields.Many2one('fleet.project', string='Dự án', required=True)
    category_id = fields.Many2one('fleet.category', string='Hạng mục')
    stock_date = fields.Date(string="Ngày", default=fields.Date.today)
    location_dest_id = fields.Many2one('fleet.location', 'Điểm đích', required=True)
    partner_receive_id = fields.Many2one('res.partner', string='Người nhận', required=True)
    partner_receive_phone = fields.Char(related='partner_receive_id.phone', string='Điện thoại')
    shipping_id = fields.Many2one('res.partner', string='Đơn vị vận chuyển', required=True)
    driver_id = fields.Many2one('res.partner', string='Lái xe', required=True)
    driver_phone = fields.Char(related='driver_id.phone', string='Điện thoại')
    equipment_id = fields.Many2one('maintenance.equipment', string='Xe', required=True)
    delivery_line = fields.One2many('stock.delivery.line', 'delivery_id', string='Chi tiết xuất kho')


class StockDelveryLine(models.Model):
    _name = 'stock.delivery.line'
    _description = 'Chi tiết xuất kho'

    delivery_id = fields.Many2one('stock.delivery', string='Phiếu xuất kho')
    product_id = fields.Many2one('product.template', string='Sản phẩm', required=True)
    section = fields.Char(related='product_id.section', string='Tiết diện')
    product_length = fields.Integer(related='product_id.product_length', string='Dài')
    uom_id = fields.Many2one(related='product_id.uom_id', string='Đơn vị')
    out_qty = fields.Float(string='SL Xuất')
    bao_qty = fields.Float(string='Bao')
    note = fields.Text(string='Ghi chú')

