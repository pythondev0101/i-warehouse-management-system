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
from iwms.models import Putaway, Warehouse, StockReceipt, BinLocation, StockItem,\
    ItemBinLocations, InventoryItem, PutawayItemLine
from iwms.forms import PutawayViewForm, PutawayCreateForm
from iwms.functions import generate_number



scripts = [
    {'bp_iwms.static': 'js/putaway.js'}
]

modals = [
    "iwms/putaway/search_sr_modal.html",
    "iwms/putaway/sr_line_modal.html",
    "iwms/putaway/confirm_modal.html"
]

@bp_iwms.route('/putaways')
@login_required
def putaways():
    fields = [Putaway.id,Putaway.pwy_number,Putaway.created_at,Putaway.created_by,Putaway.status]
    return admin_table(Putaway,fields=fields,form=PutawayViewForm(),\
        create_modal=False, create_button=True, create_url="bp_iwms.create_putaway")


@bp_iwms.route('/putaways/create',methods=['GET','POST'])
@login_required
def create_putaway():
    pwy_generated_number = ""
    pwy = db.session.query(Putaway).order_by(Putaway.id.desc()).first()

    if pwy:
        pwy_generated_number = generate_number("PWY",pwy.id)
    else:
        pwy_generated_number = "PWY00000001"

    form = PutawayCreateForm()
    
    if request.method == "GET":
        warehouses = Warehouse.query.all()
        sr_list = StockReceipt.query.filter(StockReceipt.status.in_(['LOGGED','PENDING']))
        bin_locations = BinLocation.query.all()

        data = {
            'warehouses': warehouses,
            'sr_list': sr_list,
            'bin_locations': bin_locations,
            'pwy_generated_number': pwy_generated_number,
        }

        CONTEXT['model'] = 'putaway'

        return admin_render_template('iwms/putaway/iwms_putaway_create.html', 'iwms', form=form,\
            title="Create putaway", data=data, scripts=scripts, modals=modals)

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.putaways'))

    try:
        new = Putaway()
        sr = StockReceipt.query.filter_by(sr_number=form.sr_number.data).first()
        new.stock_receipt = sr
        new.pwy_number = pwy_generated_number
        new.status = "LOGGED"
        new.reference = form.reference.data
        new.remarks = form.remarks.data
        new.created_by = "{} {}".format(current_user.fname,current_user.lname)

        _remaining = False
        items_list = request.form.getlist('pwy_items[]')
        if items_list:
            for item_id in items_list:
                item = StockItem.query.get(item_id)
                lot_no = request.form.get('lot_no_{}'.format(item_id))
                expiry_date = request.form.get('expiry_{}'.format(item_id)) if not request.form.get('expiry_{}'.format(item_id)) == '' else None
                uom = request.form.get('uom_{}'.format(item_id))
                qty = request.form.get('qty_{}'.format(item_id)) if not request.form.get('qty_{}'.format(item_id)) == '' else None
                _bin_location_code = request.form.get("bin_location_{}".format(item_id)) if not request.form.get("bin_location_{}".format(item_id)) == '' else None
                line = PutawayItemLine(stock_item=item,lot_no=lot_no,expiry_date=expiry_date,uom=uom,qty=qty)
                new.item_line.append(line)

                """ SENDING CONFIRM ITEMS TO INVENTORY ITEM """

                _check_for_item = InventoryItem.query.filter_by(stock_item_id=item_id).first()
                bin_location = BinLocation.query.filter_by(code=_bin_location_code).first()

                if _check_for_item is None:
                    inventory_item = InventoryItem()
                    inventory_item.stock_item = item
                    inventory_item.category_id = item.category_id
                    inventory_item.stock_item_type_id = item.stock_item_type_id
                    inventory_item.default_price = item.default_price
                    inventory_item.default_cost = item.default_cost

                    item_location = ItemBinLocations(inventory_item=inventory_item,bin_location=bin_location,\
                        qty_on_hand=qty,expiry_date=expiry_date,lot_no=lot_no)

                    db.session.add(inventory_item)
                    db.session.commit()
                else:
                    bin_item = ItemBinLocations.query.filter_by(inventory_item_id=_check_for_item.id,bin_location_id=bin_location.id).first()
                    if bin_item is not None:
                        bin_item.qty_on_hand = bin_item.qty_on_hand + int(qty)
                        db.session.commit()
                    else:
                        new_bin_item_location = ItemBinLocations(inventory_item=_check_for_item,\
                            bin_location=bin_location,qty_on_hand=qty,expiry_date=expiry_date,lot_no=lot_no)
                        db.session.add(new_bin_item_location)
                        db.session.commit()

                for srp in sr.item_line:
                    if int(item_id) == srp.stock_item_id:
                        srp.is_putaway = True
                        db.session.commit()


        for srp in sr.item_line:
            if srp.is_putaway == False:
                _remaining = True

        _po_remaining = False

        for pol in sr.purchase_order.product_line:
            if pol.remaining_qty > 0 :
                _po_remaining = True

        if _remaining == False:
            sr.status = "COMPLETED"
            if _po_remaining == False:
                sr.purchase_order.status = "COMPLETED"
        else:
            sr.status = "PENDING"

        db.session.add(new)
        db.session.commit()
        create_log('New putaway added','PWYID={}'.format(new.id))
        flash('New Putaway added Successfully!','success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.putaways'))
