from flask import (
    render_template, request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from app.admin.routes import admin_table, admin_edit
from iwms import bp_iwms

@bp_iwms.route('/bin_location')
@login_required
def warehouse_bin_location():
    CONTEXT['active'] = 'warehouse_bin_location'
    CONTEXT['mm-active'] = 'warehouse_bin_location'
    CONTEXT['module'] = 'iwms'
    CONTEXT['model'] = 'warehouse_bin_location'
    bins = BinLocation.query.all()
    return render_template('iwms/iwms_warehouse_bin_location.html',context=CONTEXT,bins=bins,title="Warehouse Floor Plan")
