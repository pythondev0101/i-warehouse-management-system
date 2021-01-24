from datetime import datetime
from flask import (
    render_template, request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from app import db, CONTEXT
from app.core.logging import create_log
from app.admin import admin_render_template
from app.admin.routes import admin_table, admin_edit
from app.auth.permissions import check_create
from iwms import bp_iwms
from iwms.models import Supplier
from iwms.forms import SupplierForm, SupplierEditForm
from iwms.functions import generate_number



@bp_iwms.route('/suppliers')
@login_required
def suppliers():
    fields = [Supplier.id,Supplier.code,Supplier.name,Supplier.created_by,Supplier.created_at,Supplier.updated_by,Supplier.updated_at]
    form = SupplierForm()
    sup_generated_number = ""
    sup = db.session.query(Supplier).order_by(Supplier.id.desc()).first()

    if sup:
        sup_generated_number = generate_number("SUP",sup.id)
    else:
        # MAY issue to kasi kapag hindi na truncate yung table magkaiba na yung id at number ng po
        # Make sure nakatruncate ang mga table ng po para reset yung auto increment na id
        sup_generated_number = "SUP00000001"
    form.code.auto_generated = sup_generated_number
    
    return admin_table(Supplier,fields=fields,form=form, edit_url='bp_iwms.edit_supplier',\
            create_url="bp_iwms.create_supplier")



@bp_iwms.route('/supplier/create',methods=['POST'])
@login_required
def create_supplier():
    form = SupplierForm()
    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.suppliers'))

    try:
        new = Supplier()
        new.code = form.code.data
        new.name = form.name.data
        new.status = "ACTIVE"
        new.address = form.address.data
        new.email_address = form.email_address.data
        new.contact_person = form.contact_person.data
        new.contact_number = form.contact_number.data
        new.created_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.add(new)
        db.session.commit()
        create_log('New supplier added','SUPID={}'.format(new.id))
        flash("New supplier added successfully!",'success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.suppliers'))


@bp_iwms.route('/supplier/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_supplier(oid):
    ins = Supplier.query.get_or_404(oid)
    form = SupplierEditForm(obj=ins)

    if request.method == "GET":
        return admin_edit(form,'bp_iwms.edit_supplier',oid, model=Supplier)
    
    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.suppliers'))
        
    try:
        ins.code = form.code.data
        ins.name = form.name.data
        ins.status = "ACTIVE"
        ins.address = form.address.data
        ins.email_address = form.email_address.data
        ins.contact_person = form.contact_person.data
        ins.contact_number = form.contact_number.data
        ins.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        ins.updated_at = datetime.now()
        db.session.commit()
        create_log('Supplier update','SUPID={}'.format(ins.id))
        flash('Supplier update Successfully!','success')
    except Exception as exc:
        flash(str(exc),'error')
    
    return redirect(url_for('bp_iwms.suppliers'))
