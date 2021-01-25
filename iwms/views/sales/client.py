from datetime import datetime
from flask import (
    render_template, request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from sqlalchemy.ext.declarative.api import instrument_declarative
from app import db, CONTEXT
from iwms.logging import create_log
from app.admin import admin_render_template
from app.admin.routes import admin_table, admin_edit
from app.auth.permissions import check_create
from iwms import bp_iwms
from iwms.models import Client
from iwms.forms import ClientForm, ClientEditForm
from iwms.functions import generate_number



@bp_iwms.route('/clients')
@login_required
def clients():
    fields = [Client.id,Client.code,Client.name,Client.created_by,Client.created_at,Client.updated_by,Client.updated_at]
    form = ClientForm()
    cli_generated_number = ""
    cli = db.session.query(Client).order_by(Client.id.desc()).first()

    if cli:
        cli_generated_number = generate_number("CLI",cli.id)
    else:
        cli_generated_number = "CLI00000001"

    form.code.auto_generated = cli_generated_number

    return admin_table(Client,fields=fields,form=form, edit_url='bp_iwms.edit_client',\
            create_url="bp_iwms.create_client")


@bp_iwms.route('/clients/create',methods=['POST'])
@login_required
def create_client():
    form = ClientForm()

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.clients'))

    try:
        new = Client()
        new.name = form.name.data
        new.code = form.code.data
        new.term_id = form.term_id.data if not form.term_id.data == '' else None
        new.ship_via_id = form.ship_via_id.data if not form.ship_via_id.data == '' else None
        new.created_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.add(new)
        db.session.commit()
        create_log('New client added','ClientID={}'.format(new.id))
        flash("New Client added successfully!",'success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.clients'))


@bp_iwms.route('/clients/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_client(oid):
    ins = Client.query.get_or_404(oid)
    form = ClientEditForm(obj=ins)
    if request.method == "GET":
        CONTEXT['mm-active'] = 'client'
        return admin_edit(form,'bp_iwms.edit_client',oid, model=Client)
    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.clients'))

    try:
        ins.name = form.name.data
        ins.code = form.code.data
        ins.term_id = form.term_id.data if not form.term_id.data == '' else None
        ins.ship_via_id = form.ship_via_id.data if not form.ship_via_id.data == '' else None
        ins.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        ins.updated_at = datetime.now()
        db.session.commit()
        create_log('Client update','ClientID={}'.format(ins.id))
        flash('Client update Successfully!','success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.clients'))
