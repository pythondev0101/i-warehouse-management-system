from datetime import datetime
from sqlalchemy import func
from flask import (
    render_template, request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from sqlalchemy.sql.expression import false
from app import db, CONTEXT
from iwms.logging import create_log
from app.admin import admin_render_template
from app.admin.routes import admin_table, admin_edit
from app.auth.permissions import check_create
from iwms import bp_iwms
from iwms.models import Picking, SalesOrder, Warehouse, ItemBinLocations, PickingItemLine
from iwms.forms import PickingCreateForm, PickingIndexForm
from iwms.functions import generate_number



scripts = [
    {'bp_iwms.static': 'js/picking.js'},
]

modals = [
    "iwms/picking/search_so_modal.html",
    "iwms/picking/so_line_modal.html",
    "iwms/picking/confirm_modal.html",
]


@bp_iwms.route('/pickings')
@login_required
def pickings():
    fields = [Picking.id,Picking.number,Picking.created_by,Picking.created_at,Picking.status]

    return admin_table(Picking,fields=fields,form=PickingIndexForm(),\
        create_modal=False,create_button=True, create_url="bp_iwms.create_picking")


@bp_iwms.route('/pickings/create',methods=['GET','POST'])
@login_required
def create_picking():
    pck_generated_number = ""
    pck = db.session.query(Picking).order_by(Picking.id.desc()).first()
    if pck:
        pck_generated_number = generate_number("PCK",pck.id)
    else:
        pck_generated_number = "PCK00000001"

    f = PickingCreateForm()

    if request.method == "GET":
        warehouses = Warehouse.query.all()
        sales_orders = SalesOrder.query.filter(SalesOrder.status.in_(['ON HOLD','LOGGED']))

        data = {
            'warehouses': warehouses,
            'sales_orders': sales_orders,
            'pck_generated_number': pck_generated_number
        }

        CONTEXT['model'] = 'picking'
        
        return admin_render_template('iwms/picking/iwms_picking_create.html', 'iwms',\
            form=f,title="Create picking", data=data, scripts=scripts, modals=modals)
    
    if not f.validate_on_submit():
        for key, value in f.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.pickings'))

    try:
        obj = Picking()
        so = SalesOrder.query.filter_by(number=f.so_number.data).first()
        obj.sales_order = so
        obj.number = pck_generated_number
        obj.status = "LOGGED"
        obj.remarks = f.remarks.data
        obj.created_by = "{} {}".format(current_user.fname,current_user.lname)
        
        _remaining = 0
        items_list = request.form.getlist('pick_items[]')
        if items_list:
            for item_id in items_list:
                bin_item = ItemBinLocations.query.get_or_404(item_id)
                lot_no = request.form.get('lot_no_{}'.format(item_id))
                expiry_date = request.form.get('expiry_{}'.format(item_id)) if not request.form.get('expiry_{}'.format(item_id)) == '' else None
                uom = request.form.get('uom_{}'.format(item_id))
                qty = request.form.get('qty_{}'.format(item_id)) if not request.form.get('qty_{}'.format(item_id)) == '' else None
                line = PickingItemLine(item_bin_location=bin_item,lot_no=lot_no,expiry_date=expiry_date,uom=uom,qty=qty)
                obj.item_line.append(line)

                """ DEDUCTING QUANTITY TO THE PICKED ITEMS """

                bin_item.qty_on_hand = bin_item.qty_on_hand - int(qty)
                
                for pi in so.product_line:

                    if int(item_id) == pi.item_bin_location_id:
                        pi.issued_qty = pi.issued_qty + int(qty)
                        pi.qty = pi.qty - int(qty)
                        db.session.commit()

        for pi in so.product_line:
            _remaining = _remaining + pi.qty               

        if _remaining == 0:
            so.status = "CONFIRMED"
        else:
            so.status = "ON HOLD"

        db.session.add(obj)
        db.session.commit()
        create_log('New picking added','PCKID={}'.format(obj.id))
        flash('New Picking added Successfully!','success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.pickings'))
