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
from iwms.models import Group
from iwms.forms import GroupForm, GroupEditForm



@bp_iwms.route('/groups')
@login_required
def groups():
    fields = [Group.id,Group.name,Group.created_by,Group.created_at,Group.updated_by,Group.updated_at]
    return admin_table(Group,fields=fields,create_url='bp_iwms.create_group',\
        edit_url='bp_iwms.edit_group', form=GroupForm())


@bp_iwms.route('/groups/create',methods=['POST'])
@login_required
def create_group():
    if not check_create('Groups'):
        return render_template("auth/authorization_error.html")
    form = GroupForm()

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.groups'))

    try:
        group = Group()
        group.name = form.name.data
        group.created_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.add(group)
        db.session.commit()
        flash('New group added successfully!','success')
        create_log('New group added',"GroupID={}".format(group.id))
    except Exception as e:
        flash(str(e),'error')

    return redirect(url_for('bp_iwms.groups'))


@bp_iwms.route('/groups/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_group(oid):
    group = Group.query.get_or_404(oid)
    form = GroupEditForm(obj=group)
    
    if request.method == "GET":
        return admin_edit(form,'bp_iwms.edit_group',oid,model=Group)

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.groups'))

    try:
        group.name = form.name.data
        group.updated_at = datetime.now()
        group.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.commit()
        flash('Group update Successfully!','success')
        create_log("Group update","GroupID={}".format(group.id))
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.groups'))
