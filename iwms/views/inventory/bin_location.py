from datetime import datetime
from flask import (
    render_template, request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from app import db
from app.core.logging import create_log
from app.admin.routes import admin_table, admin_edit
from app.auth.permissions import check_create
from iwms import bp_iwms
from iwms.models import BinLocation, Warehouse, Zone
from iwms.forms import BinLocationForm, BinLocationEditForm



@bp_iwms.route('/bin-locations')
@login_required
def bin_locations():
    fields = [
        BinLocation.id,BinLocation.code,BinLocation.description,
        Warehouse.name,Zone.code
        ]
    models = [BinLocation,Warehouse,Zone]

    return admin_table(*models,fields=fields,form=BinLocationForm(),\
        create_url="bp_iwms.create_bin_location", edit_url="bp_iwms.edit_bin_location")


@bp_iwms.route('/bin-locations/create',methods=['POST'])
@login_required
def create_bin_location():
    if not check_create('bin_location'):
        return render_template('auth/authorization_error.html')

    form = BinLocationForm()

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.bin_locations'))

    try:
        new = BinLocation()
        new.code = form.code.data
        new.description = form.description.data
        new.index = form.index.data if not form.index.data == '' else None
        new.warehouse_id = form.warehouse_id.data if not form.warehouse_id.data == '' else None
        new.zone_id = form.zone_id.data if not form.zone_id.data == '' else None
        new.pallet_slot = form.pallet_slot.data if not form.pallet_slot.data == '' else None
        new.pallet_cs = form.pallet_cs.data if not form.pallet_cs.data == '' else None
        new.capacity = form.capacity.data if not form.capacity.data == '' else None
        new.weight_cap = form.weight_cap.data if not form.weight_cap.data == '' else None
        new.cbm_cap = form.cbm_cap.data if not form.cbm_cap.data == '' else None
        new.created_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.add(new)
        db.session.commit()
        create_log('New bin location added','BinLocationID={}'.format(new.id))
        flash("New Bin Location added successfully!",'success')
    except Exception as exc:
        flash(str(exc),'error')
   
    return redirect(url_for('bp_iwms.bin_locations'))


@bp_iwms.route('/bin-locations/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_bin_location(oid):
    ins = BinLocation.query.get_or_404(oid)
    form = BinLocationEditForm(obj=ins)
 
    if request.method == "GET":
        return admin_edit(form,'bp_iwms.edit_bin_location',oid, model=BinLocation)
 
    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.bin_locations'))

    try:
        ins.code = form.code.data
        ins.description = form.description.data
        ins.index = form.index.data if not form.index.data == '' else None
        ins.warehouse_id = form.warehouse_id.data if not form.warehouse_id.data == '' else None
        ins.zone_id = form.zone_id.data if not form.zone_id.data == '' else None
        ins.pallet_slot = form.pallet_slot.data if not form.pallet_slot.data == '' else None
        ins.pallet_cs = form.pallet_cs.data if not form.pallet_cs.data == '' else None
        ins.capacity = form.capacity.data if not form.capacity.data == '' else None
        ins.weight_cap = form.weight_cap.data if not form.weight_cap.data == '' else None
        ins.cbm_cap = form.cbm_cap.data if not form.cbm_cap.data == '' else None
        ins.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        ins.updated_at = datetime.now()
        db.session.commit()
        create_log('BinLocation update','BinLocationID={}'.format(ins.id))
        flash('Bin Location update Successfully!','success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.bin_locations'))
