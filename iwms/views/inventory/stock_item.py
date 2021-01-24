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
from iwms.models import StockItem, Category, Supplier, StockItemType, TaxCode, UnitOfMeasure,\
    StockItemUomLine
from iwms.forms import StockItemView, StockItemCreateForm
from iwms.functions import generate_number



scripts = [
    {'bp_iwms.static': 'js/stock_item.js'}
]

modals = [
    "iwms/stock_item/add_uom_modal.html",
]


@bp_iwms.route('/stock-items')
@login_required
def stock_items():
    fields = [StockItem.id,StockItem.number,StockItem.name,StockItem.description,\
        StockItem.created_by,StockItem.created_at,StockItem.updated_by,StockItem.updated_at]

    form = StockItemView()
    return admin_table(StockItem,form=form,fields=fields, create_modal=False, create_button=True,\
        create_url="bp_iwms.create_stock_item", edit_url="bp_iwms.edit_stock_item")


@bp_iwms.route('/stock-items/create',methods=['GET','POST'])
@login_required
def create_stock_item():
    si_generated_number = ""
    si = db.session.query(StockItem).order_by(StockItem.id.desc()).first()

    if si:
        si_generated_number = generate_number("SI",si.id)
    else:
        # MAY issue to kasi kapag hindi na truncate yung table magkaiba na yung id at number ng po
        # Make sure nakatruncate ang mga table ng po para reset yung auto increment na id
        si_generated_number = "SI00000001"

    form = StockItemCreateForm()

    if request.method == "GET":
        categories = Category.query.all()
        types = StockItemType.query.all()
        suppliers = Supplier.query.all()
        tax_codes = TaxCode.query.all()
        uoms = UnitOfMeasure.query.all()

        data = {
            'si_generated_number': si_generated_number,
            'categories': categories,
            'types': types,
            'suppliers': suppliers,
            'tax_codes': tax_codes,
            'uoms': uoms
        }

        CONTEXT['model'] = 'stock_item'

        return admin_render_template('iwms/stock_item/iwms_stock_item_create.html', 'iwms',\
            form=form, data=data, scripts=scripts, modals=modals)

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.stock_items'))

    try:
        new = StockItem()
        new.number = si_generated_number
        new.status = "active"
        new.stock_item_type_id = form.stock_item_type_id.data if not form.stock_item_type_id.data == '' else None 
        new.category_id = form.category_id.data if not form.category_id.data == '' else None
        new.has_serial = 1 if form.has_serial.data == 'on' else 0
        new.monitor_expiration = 1 if form.monitor_expiration.data == 'on' else 0
        new.brand = form.brand.data
        new.name = form.name.data
        new.description = form.description.data
        new.cap_size,new.cap_profile,new.compound,new.clients = None, None, None, None
        new.packaging = form.packaging.data
        new.tax_code_id = form.tax_code_id.data if not form.tax_code_id.data == '' else None
        new.reorder_qty = form.reorder_qty.data if not form.reorder_qty.data == '' else None
        new.description_plu = form.description_plu.data
        new.barcode = form.barcode.data if not form.barcode.data == '' else None
        new.qty_plu = form.qty_plu.data if not form.qty_plu.data == '' else None
        new.length = form.length.data
        new.width = form.width.data
        new.height = form.height.data
        new.unit_id = form.unit_id.data if not form.unit_id.data == '' else None
        new.default_cost = form.default_cost.data if not form.default_cost.data == '' else None
        new.default_price = form.default_price.data if not form.default_price.data == '' else None
        new.weight = form.weight.data
        new.cbm = form.cbm.data
        new.qty_per_pallet = form.qty_per_pallet.data if not form.qty_per_pallet.data == '' else None
        new.shelf_life = form.shelf_life.data if not form.shelf_life.data == '' else None
        new.qa_lead_time = form.qa_lead_time.data if not form.qa_lead_time.data == '' else None
        new.created_by = "{} {}".format(current_user.fname,current_user.lname)

        supplier_ids = request.form.getlist('suppliers')
        if supplier_ids:
            for s_id in supplier_ids:
                supplier = Supplier.query.get_or_404(int(s_id))
                new.suppliers.append(supplier)

        uom_ids = request.form.getlist('uoms[]')
        if uom_ids:
            for u_id in uom_ids:
                uom = UnitOfMeasure.query.get(u_id)
                # qty = request.form.get("qty_{}".format(u_id))
                # barcode = request.form.get("barcode_{}".format(u_id))
                # _cost = request.form.get("default_cost_{}".format(u_id))
                # _price = request.form.get("default_price_{}".format(u_id))
                # default_cost = _cost if not _cost == '' else None
                # default_price = _price if not _price == '' else None
                # length = request.form.get("length_{}".format(u_id))
                # width = request.form.get("width_{}".format(u_id))
                # height = request.form.get("height_{}".format(u_id))
                line = StockItemUomLine(uom=uom,qty=None,barcode=None,default_cost=None,default_price=None,\
                    length=None,width=None,height=None)
                new.uom_line.append(line)

        db.session.add(new)
        db.session.commit()
        create_log('New stock item added','SIID={}'.format(new.id))
        flash('New Stock Item added Successfully!','success')
    except Exception as exc:
        flash(str(exc),'error')
    
    return redirect(url_for('bp_iwms.stock_items'))


@bp_iwms.route('/stock-items/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_stock_item(oid):
    ins = StockItem.query.get_or_404(oid)
    form = StockItemCreateForm(obj=ins)

    if request.method == "GET":
        categories = Category.query.all()
        types = StockItemType.query.all()
        suppliers = Supplier.query.all()
        tax_codes = TaxCode.query.all()
        units = UnitOfMeasure.query.all()

        selected_suppliers = []
        for selected in ins.suppliers:
            selected_suppliers.append(selected.id)

        query1 = db.session.query(StockItemUomLine.uom_id).filter_by(stock_item_id=oid)
        uoms = db.session.query(UnitOfMeasure).filter(~UnitOfMeasure.id.in_(query1))
        
        data = {
            'categories': categories,
            'types': types,
            'suppliers': suppliers,
            'tax_codes': tax_codes,
            'units': units,
            'uoms': uoms,
            'selected_suppliers': selected_suppliers,
            'uom_lines': ins.uom_line 
        }

        CONTEXT['model'] = 'stock_item'

        return admin_render_template('iwms/stock_item/iwms_stock_item_edit.html', 'iwms',form=form,\
            title="Edit stock item", oid=oid, scripts=scripts, modals=modals, data=data)

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.stock_items'))
        
    try:
        ins.status = "active"
        ins.stock_item_type_id = form.stock_item_type_id.data if not form.stock_item_type_id.data == '' else None 
        ins.category_id = form.category_id.data if not form.category_id.data == '' else None
        ins.has_serial = 1 if form.has_serial.data == 'on' else 0
        ins.monitor_expiration = 1 if form.monitor_expiration.data == 'on' else 0
        ins.brand = form.brand.data
        ins.name = form.name.data
        ins.description = form.description.data
        ins.cap_size, ins.cap_profile, ins.compound, ins.clients = None, None, None, None
        ins.packaging = form.packaging.data
        ins.tax_code_id = form.tax_code_id.data if not form.tax_code_id.data == '' else None
        ins.reorder_qty = form.reorder_qty.data if not form.reorder_qty.data == '' else None
        ins.description_plu = form.description_plu.data
        ins.barcode = form.barcode.data if not form.barcode.data == '' else None
        ins.qty_plu = form.qty_plu.data if not form.qty_plu.data == '' else None
        ins.length = form.length.data
        ins.width = form.width.data
        ins.height = form.height.data
        ins.unit_id = form.unit_id.data if not form.unit_id.data == '' else None
        ins.default_cost = form.default_cost.data if not form.default_cost.data == '' else None
        ins.default_price = form.default_price.data if not form.default_price.data == '' else None
        ins.weight = form.weight.data
        ins.cbm = form.cbm.data
        ins.qty_per_pallet = form.qty_per_pallet.data if not form.qty_per_pallet.data == '' else None
        ins.shelf_life = form.shelf_life.data if not form.shelf_life.data == '' else None
        ins.qa_lead_time = form.qa_lead_time.data if not form.qa_lead_time.data == '' else None
        ins.updated_by = "{} {}".format(current_user.fname,current_user.lname)
        ins.updated_at = datetime.now()

        supplier_ids = request.form.getlist('suppliers')
        if supplier_ids:
            ins.suppliers = []
            for new_sup in supplier_ids:
                supp = Supplier.query.get_or_404(new_sup)
                ins.suppliers.append(supp)

        uom_ids = request.form.getlist('uoms[]')
        if uom_ids:
            ins.uom_line = []
            for u_id in uom_ids:
                uom = UnitOfMeasure.query.get(u_id)
                # qty = request.form.get("qty_{}".format(u_id))
                # barcode = request.form.get("barcode_{}".format(u_id))
                # default_cost = request.form.get("default_cost_{}".format(u_id))
                # default_price = request.form.get("default_price_{}".format(u_id))
                # length = request.form.get("length_{}".format(u_id))
                # width = request.form.get("width_{}".format(u_id))
                # height = request.form.get("height_{}".format(u_id))
                line = StockItemUomLine(uom=uom,qty=None,barcode=None,default_cost=None,default_price=None,\
                    length=None,width=None,height=None)
                ins.uom_line.append(line)
                
        db.session.commit()
        create_log('Stock item update','SIID={}'.format(ins.id))
        flash('Stock Item updated Successfully!','success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.stock_items'))
