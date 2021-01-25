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
from iwms.models import Category
from iwms.forms import CategoryForm, CategoryEditForm



@bp_iwms.route('/categories')
@login_required
def categories():
    fields = [
        Category.id,Category.code,Category.description,Category.created_by,Category.created_at,\
        Category.updated_by,Category.updated_at
        ]
    return admin_table(Category,fields=fields,form=CategoryForm(),\
        create_url="bp_iwms.create_category", edit_url='bp_iwms.edit_category')


@bp_iwms.route('/categories/create',methods=['POST'])
@login_required
def create_category():
    if not check_create('category'):
        return render_template("auth/authorization_error.html")
        
    form = CategoryForm()

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.categories'))

    try:
        new = Category()
        new.code = form.code.data
        new.description = form.description.data
        new.created_by = "{} {}".format(current_user.fname,current_user.lname)
        db.session.add(new)
        db.session.commit()
        create_log('New category added','CategoryID={}'.format(new.id))
        flash("New Category added successfully!",'success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.categories'))


@bp_iwms.route('/categories/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_category(oid):
    ins = Category.query.get_or_404(oid)
    form = CategoryEditForm(obj=ins)
    if request.method == "GET":
        return admin_edit(form,'bp_iwms.edit_category',oid, model=Category)

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.categories'))

    try:
        ins.code = form.code.data
        ins.description = form.description.data
        ins.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        ins.updated_at = datetime.now()
        db.session.commit()
        create_log('Category update','CategoryID={}'.format(ins.id))
        flash('Category update Successfully!','success')
    except Exception as exc:
        flash(str(exc),'error')
    
    return redirect(url_for('bp_iwms.categories'))
