from odoo import api, fields, models
from odoo.exceptions import ValidationError

SQL_GENERATE_FLEET_TRIP_COST_REPORT = """
DELETE FROM fleet_trip_cost_report WHERE id is not null;
INSERT INTO fleet_trip_cost_report
(schedule_date, equipment_id, invoice_amount, bill_content, oil_amount, number_of_oil, machine_amount, create_uid)
SELECT ft.schedule_date   AS schedule_date,
       ft.equipment_id    AS equipment_id,
       fmr.invoice_amount AS invoice_amount,
       fmr.bill_content   AS bill_content,
       fmr.oil_amount     AS oil_amount,
       fmr.number_of_oil  AS number_of_oil,
       fmr.machine_amount AS machine_amount,
       {create_uid}                  AS create_uid
FROM fleet_trip ft
         LEFT JOIN fleet_main_report fmr
                   ON ft.equipment_id = fmr.equipment_id AND ft.schedule_date = fmr.date
WHERE ft.schedule_date BETWEEN '{from_date}' AND '{to_date}'
ORDER BY ft.schedule_date asc;
"""


class FleetTripCostGenerate(models.TransientModel):
    _name = 'fleet.trip.cost.generate'
    _description = 'Fleet Trip Cost Generate'

    from_date = fields.Date(string="Từ ngày", required=True)
    to_date = fields.Date(string="Đến Ngày", required=True)

    @api.onchange('from_date', 'to_date')
    def onchange_from_date_to_date(self):
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValidationError("Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.")

    def action_generate_fleet_trip_cost_report(self):
        sql = SQL_GENERATE_FLEET_TRIP_COST_REPORT.format(
            create_uid=self._uid, from_date=self.from_date, to_date=self.to_date)
        self._cr.execute(sql)
        return self.action_view_fleet_trip_cost_report()

    @staticmethod
    def action_view_fleet_trip_cost_report():
        act_window = {
            'type': 'ir.actions.act_window',
            'name': "Bảng chi phí vận tải",
            'res_model': 'fleet.trip.cost.report',
            'view_mode': 'tree',
            'target': 'main',
        }
        return act_window


class FleetTripCostReport(models.Model):
    _name = 'fleet.trip.cost.report'
    _description = 'Fleet Trip Cost Report'

    schedule_date = fields.Date(string='Ngày')
    equipment_id = fields.Many2one('maintenance.equipment', string='Xe')
    invoice_amount = fields.Float(string='Hóa đơn', digits=(16, 0))
    bill_content = fields.Text(string="Nội dung hoá đơn")
    oil_amount = fields.Float(string="Tiền dầu", digits=(16, 0))
    number_of_oil = fields.Float(string="Số lít dầu", digits=(16, 2))
    machine_amount = fields.Float(string="Dầu máy", digits=(16, 0))
