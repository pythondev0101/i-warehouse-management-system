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
from iwms.models import Term
from iwms.forms import TermForm, TermEditForm



@bp_iwms.route('/terms')
@login_required
def terms():
    fields = [Term.id,Term.code,Term.description,Term.days,Term.created_by,Term.created_at,Term.updated_by,Term.updated_at]
    return admin_table(Term,fields=fields,form=TermForm(), edit_url='bp_iwms.edit_term',\
            create_url="bp_iwms.create_term")


@bp_iwms.route('/terms/create',methods=['POST'])
@login_required
def create_term():
    form = TermForm()

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.terms'))

    try:
        new = Term()
        new.code = form.code.data
        new.description = form.description.data
        new.days = form.days.data if not form.days.data == '' else None
        new.created_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.add(new)
        db.session.commit()
        create_log('New term added','TermID={}'.format(new.id))
        flash("New term added successfully!",'success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.terms'))


@bp_iwms.route('/terms/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_term(oid):
    ins = Term.query.get_or_404(oid)
    form = TermEditForm(obj=ins)

    if request.method == "GET":
        return admin_edit(form,'bp_iwms.edit_term',oid, model=Term)
    
    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.terms'))
    
    try:
        ins.code = form.code.data
        ins.description = form.description.data
        ins.days = form.days.data if not form.days.data == '' else None
        ins.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        ins.updated_at = datetime.now()
        db.session.commit()
        create_log('Term update','TermID={}'.format(ins.id))
        flash('Term update Successfully!','success')
        return redirect(url_for('bp_iwms.terms'))
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.terms'))
