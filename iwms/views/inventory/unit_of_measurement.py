from datetime import datetime
from flask import (
    request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from app import db
from iwms.logging import create_log
from app.admin.routes import admin_table, admin_edit
from app.auth.permissions import check_create
from iwms import bp_iwms
from iwms.models import UnitOfMeasure
from iwms.forms import UnitOfMeasureForm, UnitOfMeasureEditForm



@bp_iwms.route('/unit-of-measurements')
@login_required
def unit_of_measurements():
    fields = [UnitOfMeasure.id,UnitOfMeasure.code,UnitOfMeasure.description,UnitOfMeasure.active,\
        UnitOfMeasure.created_by,UnitOfMeasure.created_at,UnitOfMeasure.updated_by,UnitOfMeasure.updated_at]
    
    return admin_table(UnitOfMeasure,fields=fields,form=UnitOfMeasureForm(),\
        edit_url='bp_iwms.edit_unit_of_measurement', create_url="bp_iwms.create_unit_of_measurement")


@bp_iwms.route('/unit-of-measurements/create',methods=['POST'])
@login_required
def create_unit_of_measurement():
    f = UnitOfMeasureForm()

    if not f.validate_on_submit():
        for key, value in f.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.unit_of_measurements'))

    try:
        obj = UnitOfMeasure()
        obj.code = f.code.data
        obj.description = f.description.data
        obj.active = 1 if f.active.data == 'on' else 0
        obj.created_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.add(obj)
        db.session.commit()
        create_log('New unit of measure added','UOMID={}'.format(obj.id))
        flash("New Unit of measure added successfully!",'success')
    except Exception as e:
        flash(str(e),'error')

    return redirect(url_for('bp_iwms.unit_of_measurements'))



@bp_iwms.route('/unit-of-measurements/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_unit_of_measurement(oid):
    obj = UnitOfMeasure.query.get_or_404(oid)
    f = UnitOfMeasureEditForm(obj=obj)
    
    if request.method == "GET":
        return admin_edit(f,'bp_iwms.edit_unit_of_measurement', oid, model=UnitOfMeasure)

    if not f.validate_on_submit():
        for key, value in f.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.unit_of_measurements'))

    try:
        obj.code = f.code.data
        obj.description = f.description.data
        obj.active = 1 if f.active.data == 'on' else 0
        obj.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        obj.updated_at = datetime.now()
        db.session.commit()
        create_log('Unit of measure update','UOMID={}'.format(obj.id))
        flash('Unit of measure update Successfully!','success')
    except Exception as e:
        flash(str(e),'error')

    return redirect(url_for('bp_iwms.unit_of_measurements'))
