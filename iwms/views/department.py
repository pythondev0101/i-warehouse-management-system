from flask import (
    render_template, request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from app.admin.routes import admin_table, admin_edit
from iwms import bp_iwms

@bp_iwms.route('/departments')
@login_required
def departments():
    fields = [Department.id,Department.name,Department.created_by,Department.created_at,\
        Department.updated_by,Department.updated_at]
    CONTEXT['mm-active'] = 'department'
    return admin_table(Department,fields=fields,url='',form=DepartmentForm(), \
        template="iwms/iwms_index.html",kwargs={'active':'system'}, \
            create_url="bp_iwms.department_create",edit_url="bp_iwms.department_edit")

@bp_iwms.route('/department_create',methods=['POST'])
@login_required
def department_create():
    if _check_create('department'):
        form = DepartmentForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                try:
                    dept = Department()
                    dept.name = form.name.data
                    dept.created_by = "{} {}".format(current_user.fname,current_user.lname)
                    db.session.add(dept)
                    db.session.commit()
                    flash('New department added successfully!','success')
                    _log_create('New department added','DepartmentID={}'.format(dept.id))
                    return redirect(url_for('bp_iwms.departments'))
                except Exception as e:
                    flash(str(e),'error')
                    return redirect(url_for('bp_iwms.departments'))
            else:
                for key, value in form.errors.items():
                    flash(str(key) + str(value), 'error')
                return redirect(url_for('bp_iwms.departments'))
    else:
        return render_template("auth/authorization_error.html")

@bp_iwms.route('/department_edit/<int:oid>',methods=['GET','POST'])
@login_required
def department_edit(oid):
    obj = Department.query.get_or_404(oid)
    f = DepartmentEditForm(obj=obj)
    if request.method == "GET":
        CONTEXT['mm-active'] = 'department'

        return admin_edit(f,'bp_iwms.department_edit',oid, \
            model=Department,template='iwms/iwms_edit.html',kwargs={'active':'system'})
    elif request.method == "POST":
        if f.validate_on_submit():
            try:
                obj.name = f.name.data
                obj.updated_by = "{} {}".format(current_user.fname,current_user.lname)
                obj.updated_at = datetime.now()
                db.session.commit()
                flash('Department update Successfully!','success')
                _log_create('Department update','DepartmentID={}'.format(oid))
                return redirect(url_for('bp_iwms.departments'))
            except Exception as e:
                flash(str(e),'error')
                return redirect(url_for('bp_iwms.departments'))
        else:    
            for key, value in form.errors.items():
                flash(str(key) + str(value), 'error')
            return redirect(url_for('bp_iwms.departments'))
