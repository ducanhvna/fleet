# -*- coding: utf-8 -*-
from .main import *
import datetime

OUT_SUCCESS_CODE = 200

OUT_FLEET_TRIP_schema = (
    ("equipment_id", (
        "id",
        "name",
        "license_plate",
    ),),
    ("location_id", (
        "id",
        "name"
    ),),
    ("location_dest_id", (
        "id",
        "name"
    ),),
    "start_date",
    "end_date",
    "state",
)

OUT_model_res_user_read_one_SCHEMA = (
    "id",
    "name",
    ("employee_id", (
        "id",
        "mobile_phone",
        "trip_count",
        "trip_done_count",
        ("department_id", (
            "id",
            "name"
        ),),
        ("parent_id", (
            "id",
            "name"
        ),),
        "identification_id",
        "gender",
        "birthday",
        ("address_home_id", (
            "street",
            "street2",
            "city",
            ("state_id",
             (
                 "id",
                 "name"
             ),),
            "phone",
            "mobile",
        ),
    )),
))

OUT_maintenance_equipment_schema = (
    "id",
    "name",
    "last_request",
    "license_plate",
    "trip_count",
)

OUT_maintenance_request_schema = (
    "id",
    "name",
    ("equipment_id", (
        "id",
        "name",
        "license_plate",
    )),
    "request_date",
    ("user_id", (
        "id",
        "name"
    )),
    ("create_uid", (
        "id",
        "name"
    )),
    ("performer_id", (
        "id",
        "name"
    )),
    ("company_id", (
        "id",
        "name"
    )),
    ("maintenance_team_id", (
        "id",
        "name"
    )),
    "note",
    ("stage_id", (
        "id",
        "name"
    )),
    "date_process",
    "schedule_date",
    "trip_count",
)


class ControllerREST(http.Controller):

    @http.route('/api/maintenance.equipment', methods=['GET'], type='http', auth='none', cors=rest_cors_value)
    @check_permissions
    def api_maintenance_equipment_GET(self, **kw):
        domain = []
        for key, val in request.httprequest.args.items():
            try:
                val = literal_eval(val)
            except:
                pass
            domain += [(key, '=', val)]
        return wrap_resource_read_all(
            modelname='maintenance.equipment',
            default_domain=domain or [],
            success_code=OUT_SUCCESS_CODE,
            OUT_fields=OUT_maintenance_equipment_schema,
            search_more=False)

    @http.route('/api/maintenance.equipment/<id>', methods=['GET'], type='http', auth='none', cors=rest_cors_value)
    @check_permissions
    def api_model_maintenance_equipment_id_GET(self, id, **kw):
        return wrap_resource_read_one(
            modelname='maintenance.equipment',
            id=id,
            success_code=OUT_SUCCESS_CODE,
            OUT_fields=OUT_maintenance_equipment_schema
        )

    @http.route('/api/maintenance.request', methods=['GET'], type='http', auth='none', cors=rest_cors_value)
    @check_permissions
    def api_maintenance_request_GET(self, **kw):
        domain = []
        for key, val in request.httprequest.args.items():
            try:
                val = literal_eval(val)
            except:
                pass
            domain += [(key, '=', val)]
        return wrap_resource_read_all(
            modelname='maintenance.request',
            default_domain=domain or [],
            success_code=OUT_SUCCESS_CODE,
            OUT_fields=OUT_maintenance_request_schema,
            order_data='date_process desc')

    @http.route('/api/maintenance.equipment/<id>/<method>', methods=['PUT'], type='http', auth='none',
                cors=rest_cors_value,
                csrf=False)
    @check_permissions
    def api_maintenance_equipment_method_PUT(self, id, method, **kw):
        return wrap_resource_call_method(
            modelname='maintenance.equipment',
            id=id,
            method=method,
            success_code=OUT_SUCCESS_CODE
        )

    @http.route('/api/res.users/<id>', methods=['GET'], type='http', auth='none', cors=rest_cors_value)
    @check_permissions
    def api_model_res_users_id_GET(self, id, **kw):
        return wrap_resource_read_one(
            modelname='res.users',
            id=id,
            success_code=OUT_SUCCESS_CODE,
            OUT_fields=OUT_model_res_user_read_one_SCHEMA
        )

    @http.route('/api/fleet.trip', methods=['GET'], type='http', auth='none', cors=rest_cors_value)
    @check_permissions
    def api_model_fleet_trip_GET(self, **kw):
        domain = []
        today = datetime.date.today().strftime('%Y-%m-%d')
        for key, val in request.httprequest.args.items():
            try:
                val = literal_eval(val)
            except:
                pass
            if key == 'date' and val == 'today':
                domain += [('schedule_date', '>=', today), ('schedule_date', '<=', today)]
                continue
            domain += [(key, '=', val)]
        return wrap_resource_read_all(
            modelname='fleet.trip',
            default_domain=domain or [],
            success_code=OUT_SUCCESS_CODE,
            OUT_fields=OUT_FLEET_TRIP_schema)

    @http.route('/api/fleet.trip/<id>/<method>', methods=['PUT'], type='http', auth='none',
                cors=rest_cors_value,
                csrf=False)
    @check_permissions
    def api_model_fleet_trip_method_PUT(self, id, method, **kw):
        return wrap_resource_call_method(
            modelname='fleet.trip',
            id=id,
            method=method,
            success_code=OUT_SUCCESS_CODE
        )

