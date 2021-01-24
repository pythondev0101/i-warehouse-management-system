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
from iwms.models import Warehouse
from iwms.forms import WarehouseForm, WarehouseEditForm



@bp_iwms.route('/warehouses')
@login_required
def warehouses():
    fields = [Warehouse.id,Warehouse.code,Warehouse.name,\
        Warehouse.created_by,Warehouse.created_at,Warehouse.updated_by,Warehouse.updated_at]
    
    return admin_table(Warehouse,fields=fields,form=WarehouseForm(),create_url='bp_iwms.create_warehouse',\
        edit_url='bp_iwms.edit_warehouse', kwargs={'convert_boolean':2})


@bp_iwms.route('/warehouses/create',methods=['POST'])
@login_required
def create_warehouse():
    if not check_create('warehouse'):
        return render_template("auth/authorization_error.html")
    
    form = WarehouseForm()
    
    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.warehouses'))

    try:
        new = Warehouse()
        new.code = form.code.data
        new.name = form.name.data
        new.active = 1
        new.main_warehouse = 1
        new.created_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.add(new)
        db.session.commit()
        create_log('New warehouse added','WarehouseID={}'.format(new.id))
        flash("New warehouse added successfully!",'success')
    except Exception as exc:
        flash(str(exc),'error')
    
    return redirect(url_for('bp_iwms.warehouses'))


@bp_iwms.route('/warehouses/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_warehouse(oid):
    ins = Warehouse.query.get_or_404(oid)
    form = WarehouseEditForm(obj=ins)

    if request.method == "GET":
        return admin_edit(form,'bp_iwms.edit_warehouse',oid, model=Warehouse)

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.warehouses'))

    try:
        ins.code = form.code.data
        ins.name = form.name.data
        ins.active = 1
        ins.main_warehouse = 1
        ins.updated_at = datetime.now()
        ins.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.commit()
        create_log('Warehouse update','WarehouseID={}'.format(oid))
        flash('Warehouse update Successfully!','success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.warehouses'))