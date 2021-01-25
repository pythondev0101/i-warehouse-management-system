from datetime import datetime
from flask import (
    render_template, request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from app import db
from app.admin import admin_render_template
from app.admin.routes import admin_table, admin_edit
from app.auth.permissions import check_create
from iwms.logging import create_log
from iwms import bp_iwms
from iwms.models import Department
from iwms.forms import DepartmentForm, DepartmentEditForm



@bp_iwms.route('/departments')
@login_required
def departments():
    fields = [Department.id,Department.name,Department.created_by,Department.created_at,\
        Department.updated_by,Department.updated_at]
    return admin_table(Department,fields=fields,form=DepartmentForm(), \
            create_url="bp_iwms.create_department",edit_url="bp_iwms.edit_department")

@bp_iwms.route('/departments/create',methods=['POST'])
@login_required
def create_department():
    if not check_create('department'):
        return admin_render_template("auth/authorization_error.html", 'iwms')

    form = DepartmentForm()

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.departments'))

    try:
        dept = Department()
        dept.name = form.name.data
        dept.created_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.add(dept)
        db.session.commit()
        flash('New department added successfully!','success')
        create_log('New department added','DepartmentID={}'.format(dept.id))
    except Exception as e:
        flash(str(e),'error')

    return redirect(url_for('bp_iwms.departments'))

@bp_iwms.route('/departments/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_department(oid):
    obj = Department.query.get_or_404(oid)
    f = DepartmentEditForm(obj=obj)

    if request.method == "GET":
        return admin_edit(f,'bp_iwms.edit_department',oid, model=Department)

    if not f.validate_on_submit():
        for key, value in f.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.departments'))

    try:
        obj.name = f.name.data
        obj.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        obj.updated_at = datetime.now()
        db.session.commit()
        flash('Department update Successfully!','success')
        create_log('Department update','DepartmentID={}'.format(oid))
    except Exception as e:
        flash(str(e),'error')
        
    return redirect(url_for('bp_iwms.departments'))
