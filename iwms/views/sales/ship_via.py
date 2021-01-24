from datetime import datetime
from flask import (
    render_template, request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from sqlalchemy.ext.declarative.api import instrument_declarative
from app import db, CONTEXT
from app.core.logging import create_log
from app.admin import admin_render_template
from app.admin.routes import admin_table, admin_edit
from app.auth.permissions import check_create
from iwms import bp_iwms
from iwms.models import ShipVia
from iwms.forms import ShipViaForm, ShipViaEditForm



@bp_iwms.route('/ship-via')
@login_required
def ship_via():
    fields = [ShipVia.id,ShipVia.description,ShipVia.created_by,ShipVia.created_at,ShipVia.updated_by,ShipVia.updated_at]
    return admin_table(ShipVia,fields=fields,form=ShipViaForm(),\
        edit_url='bp_iwms.edit_ship_via', create_url="bp_iwms.create_ship_via")


@bp_iwms.route('/ship-via/create',methods=['POST'])
@login_required
def create_ship_via():
    form = ShipViaForm()

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.ship_via'))
    
    try:
        new = ShipVia()
        new.description = form.description.data
        new.created_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.add(new)
        db.session.commit()
        create_log('New ship via added','ShipViaID={}'.format(new.id))
        flash("New ship via added successfully!",'success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.ship_via'))


@bp_iwms.route('/ship-via/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_ship_via(oid):
    ins = ShipVia.query.get_or_404(oid)
    form = ShipViaEditForm(obj=ins)
    
    if request.method == "GET":
        return admin_edit(form, 'bp_iwms.edit_ship_via',oid, model=ShipVia)

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.ship_via'))
        
    try:
        ins.description = form.description.data
        ins.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        ins.updated_at = datetime.now()
        db.session.commit()
        create_log('Ship via update','ShipViaID={}'.format(ins.id))
        flash('Ship via update Successfully!','success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.ship_via'))
