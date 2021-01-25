from flask import (request, jsonify)
from flask_login import login_required
from app import db, CONTEXT
from app.admin import admin_render_template
from iwms import bp_iwms
from iwms.models import BinLocation


modals = [
    "iwms/warehouse_bin_location/iwms_wbl_modal.html",
]

@bp_iwms.route('/bin_location')
@login_required
def warehouse_bin_location():
    bins = BinLocation.query.all()

    CONTEXT['active'] = 'warehouse_bin_location'
    CONTEXT['model'] = 'warehouse_bin_location'

    return admin_render_template('iwms/warehouse_bin_location/iwms_floor_plan.html', 'iwms',\
        bins=bins,title="Warehouse Floor Plan", modals=modals)


@bp_iwms.route('/api/bin-locations/create',methods=['POST'])
def create_bin_location_api():
    _bin_code = request.json['bin_code']
    bin = BinLocation()
    bin.code = _bin_code
    bin.x = 0
    bin.y = 0
    db.session.add(bin)
    db.session.commit()
    
    response = jsonify({
        'result': True
        })
    response.status_code = 200

    return response


@bp_iwms.route('/api/bin-locations/coords/update', methods=['POST'])
def update_bin_location_coords():
    _bin_code = request.json['bin_code']
    _x,_y = request.json['x'], request.json['y']

    bin = BinLocation.query.filter_by(code=_bin_code).first()
    bin.x = _x / 2
    bin.y = _y / 2

    db.session.commit()

    response = jsonify({
        'result': True
    })

    return response


@bp_iwms.route('/api/bin-locations/<string:bin_code>/products',methods=['GET'])
def get_bin_locations_items(bin_code):
    bin = BinLocation.query.filter_by(code=bin_code).first()
    items = []

    for x in bin.item_bin_locations:
        items.append({
            'name': x.inventory_item.stock_item.name,
            'qty_on_hand': x.qty_on_hand,
            'lot_no': x.lot_no,
            'expiry_date': x.expiry_date,
        })

    response = jsonify({
        'items': items
    })

    return response