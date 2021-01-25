from datetime import datetime
from flask import (
    render_template, request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from app import db
from iwms.logging import create_log
from app.admin.routes import admin_table, admin_edit
from app.auth.permissions import check_create
from iwms import bp_iwms
from iwms.models import Zone, Warehouse
from iwms.forms import ZoneForm, ZoneEditForm



@bp_iwms.route('/zones')
@login_required
def zones():
    fields = [Zone.id,Zone.code,Zone.description,Zone.created_by,Zone.created_at,Zone.updated_by,Zone.updated_at]
    return admin_table(Zone,fields=fields,form=ZoneForm(),create_url='bp_iwms.create_zone', \
        edit_url='bp_iwms.edit_zone')
    

@bp_iwms.route('/zones/create',methods=['POST'])
@login_required
def create_zone():
    if not check_create('zone'):
        return render_template('auth/authorization_error.html')

    form = ZoneForm()

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.zones'))

    try:
        new = Zone()
        new.code = form.code.data
        new.description = form.description.data
        new.created_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.add(new)
        db.session.commit()
        create_log('New zone added','ZoneID={}'.format(new.id))
        flash("New zone added successfully!",'success')
    except Exception as exc:
        flash(str(exc),'error')
    
    return redirect(url_for('bp_iwms.zones'))


@bp_iwms.route('/zones/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_zone(oid):
    ins = Zone.query.get_or_404(oid)
    form = ZoneEditForm(obj=ins)
    
    if request.method == "GET":
    
        return admin_edit(form,'bp_iwms.edit_zone',oid, model=Warehouse)

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.zones'))

    try:
        ins.code = form.code.data
        ins.description = form.description.data
        ins.updated_at = datetime.now()
        ins.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.commit()
        create_log('Zone update','ZoneID={}'.format(ins.id))
        flash('Zone update Successfully!','success')
    except Exception as exc:
        flash(str(exc),'error')
    
    return redirect(url_for('bp_iwms.zones'))
