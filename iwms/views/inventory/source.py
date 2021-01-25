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
from iwms.models import Source
from iwms.forms import SourceForm, SourceEditForm



@bp_iwms.route('/sources')
@login_required
def sources():
    fields = [Source.id,Source.name,Source.description,Source.created_by,Source.created_at,Source.updated_by,Source.updated_at]

    return admin_table(Source,fields=fields,form=SourceForm(), edit_url='bp_iwms.edit_source',\
            create_url="bp_iwms.create_source")


@bp_iwms.route('/sources/create',methods=['POST'])
@login_required
def create_source():
    form = SourceForm()
    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.sources'))
    try:
        obj = Source()
        obj.name = form.name.data
        obj.description = form.description.data
        obj.created_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.add(obj)
        db.session.commit()
        create_log('New source added','SourceID={}'.format(obj.id))
        flash("New source added successfully!",'success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.sources'))


@bp_iwms.route('/sources/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_source(oid):
    obj = Source.query.get_or_404(oid)
    form = SourceEditForm(obj=obj)

    if request.method == "GET":
        return admin_edit(form,'bp_iwms.edit_source', oid, model=Source)

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.sources'))

    try:
        obj.name = form.name.data
        obj.description = form.description.data
        obj.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        obj.updated_at = datetime.now()
        db.session.commit()
        create_log('Source update','SourceID={}'.format(obj.id))
        flash('Source update Successfully!','success')
    except Exception as e:
        flash(str(e),'error')

    return redirect(url_for('bp_iwms.sources'))
