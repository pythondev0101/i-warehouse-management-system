from flask import (
    render_template, request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from app.admin.routes import admin_table, admin_edit
from iwms import bp_iwms


@bp_iwms.route('/unit_of_measures')
@login_required
def unit_of_measures():
    fields = [UnitOfMeasure.id,UnitOfMeasure.code,UnitOfMeasure.description,UnitOfMeasure.active,\
        UnitOfMeasure.created_by,UnitOfMeasure.created_at,UnitOfMeasure.updated_by,UnitOfMeasure.updated_at]
    CONTEXT['mm-active'] = 'unit_of_measure'
    return admin_table(UnitOfMeasure,fields=fields,form=UnitOfMeasureForm(), \
        template='iwms/iwms_index.html', edit_url='bp_iwms.unit_of_measure_edit', \
            create_url="bp_iwms.unit_of_measure_create",kwargs={'active':'inventory'})


@bp_iwms.route('/unit_of_measure_create',methods=['POST'])
@login_required
def unit_of_measure_create():
    f = UnitOfMeasureForm()
    if request.method == "POST":
        if f.validate_on_submit():
            try:
                obj = UnitOfMeasure()
                obj.code = f.code.data
                obj.description = f.description.data
                obj.active = 1 if f.active.data == 'on' else 0
                obj.created_by = "{} {}".format(current_user.fname,current_user.lname)
                db.session.add(obj)
                db.session.commit()
                _log_create('New unit of measure added','UOMID={}'.format(obj.id))
                flash("New Unit of measure added successfully!",'success')
                return redirect(url_for('bp_iwms.unit_of_measures'))
            except Exception as e:
                flash(str(e),'error')
                return redirect(url_for('bp_iwms.unit_of_measures'))
        else:
            for key, value in f.errors.items():
                flash(str(key) + str(value), 'error')
            return redirect(url_for('bp_iwms.unit_of_measures'))



@bp_iwms.route('/unit_of_measure_edit/<int:oid>',methods=['GET','POST'])
@login_required
def unit_of_measure_edit(oid):
    obj = UnitOfMeasure.query.get_or_404(oid)
    f = UnitOfMeasureEditForm(obj=obj)
    if request.method == "GET":
        CONTEXT['mm-active'] = 'unit_of_measure'

        return admin_edit(f,'bp_iwms.unit_of_measure_edit',oid, \
            model=UnitOfMeasure,template='iwms/iwms_edit.html',kwargs={'active':'inventory'})
    elif request.method == "POST":
        if f.validate_on_submit():
            try:
                obj.code = f.code.data
                obj.description = f.description.data
                obj.active = 1 if f.active.data == 'on' else 0
                obj.updated_by = "{} {}".format(current_user.fname,current_user.lname)
                obj.updated_at = datetime.now()
                db.session.commit()
                _log_create('Unit of measure update','UOMID={}'.format(obj.id))
                flash('Unit of measure update Successfully!','success')
                return redirect(url_for('bp_iwms.unit_of_measures'))
            except Exception as e:
                flash(str(e),'error')
                return redirect(url_for('bp_iwms.unit_of_measures'))
        else:
            for key, value in form.errors.items():
                flash(str(key) + str(value), 'error')
            return redirect(url_for('bp_iwms.unit_of_measures'))
