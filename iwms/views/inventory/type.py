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
from iwms.models import StockItemType
from iwms.forms import TypeForm, TypeEditForm



@bp_iwms.route('/stock-item-types')
@login_required
def stock_item_types():
    fields = [StockItemType.id,StockItemType.name,StockItemType.created_by,\
        StockItemType.created_at,StockItemType.updated_by,StockItemType.updated_at]

    return admin_table(StockItemType,fields=fields,form=TypeForm(), edit_url='bp_iwms.edit_type',\
            create_url="bp_iwms.create_type")


@bp_iwms.route('/types/create',methods=['POST'])
@login_required
def create_type():
    form = TypeForm()
    
    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.stock_item_types'))

    try:
        new = StockItemType()
        new.name = form.name.data
        new.created_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.add(new)
        db.session.commit()
        create_log('New type added','TypeID={}'.format(new.id))
        flash("New type added successfully!",'success')
    except Exception as e:
        flash(str(e),'error')

    return redirect(url_for('bp_iwms.stock_item_types'))



@bp_iwms.route('/types/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_type(oid):
    ins = StockItemType.query.get_or_404(oid)
    form = TypeEditForm(obj=ins)

    if request.method == "GET":
        return admin_edit(form,'bp_iwms.edit_type',oid, model=StockItemType)

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.stock_item_types'))

    try:
        ins.name = form.name.data
        ins.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        ins.updated_at = datetime.now()
        db.session.commit()
        create_log('Type update','TypeID={}'.format(ins.id))
        flash('Type update Successfully!','success')
    except Exception as e:
        flash(str(e),'error')

    return redirect(url_for('bp_iwms.stock_item_types'))
