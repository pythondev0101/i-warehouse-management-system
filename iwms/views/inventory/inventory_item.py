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



@bp_iwms.route('/inventory-items')
@login_required
def inventory_items():
    fields = [InventoryItem.id,InventoryItem.default_cost,InventoryItem.default_price,StockItem.name,StockItemType.name,Category.description]
    query1 = db.session.query(InventoryItem,StockItem,StockItemType,Category)
    models = query1.outerjoin(StockItem, InventoryItem.stock_item_id == StockItem.id).outerjoin(StockItemType, InventoryItem.stock_item_type_id == StockItemType.id).\
        outerjoin(Category, InventoryItem.category_id  == Category.id).\
            with_entities(InventoryItem.id,StockItem.name,InventoryItem.default_cost,InventoryItem.default_price,StockItemType.name,Category.description).all()    
    # Dahil hindi ko masyadong kabisado ang ORM, ito muna
    mmodels = [list(ii) for ii in models]

    for ii in mmodels:
        _ibl = ItemBinLocations.query.with_entities(func.sum(ItemBinLocations.qty_on_hand)).filter_by(inventory_item_id=ii[0]).all()
        ii.append(_ibl[0][0])
        
    CONTEXT['mm-active'] = 'inventory_item'
    return admin_table(InventoryItem,fields=fields,form=InventoryItemForm(), \
        template='iwms/inventory_item/iwms_inventory_item_index.html',edit_url="bp_iwms.inventory_item_edit",\
            create_modal=True,view_modal="iwms/inventory_item/iwms_inventory_item_view_modal.html",create_url=False,kwargs={'active':'inventory',
            'models': mmodels
            })

@bp_iwms.route('/inventory_item_edit/<int:oid>',methods=['GET','POST'])
@login_required
def inventory_item_edit(oid):
    ii = InventoryItem.query.get_or_404(oid)
    f = InventoryItemEditForm(obj=ii)
    if request.method == "GET":
        # Hardcoded html ang irerender natin hindi yung builtin ng admin
        CONTEXT['active'] = 'inventory'
        CONTEXT['mm-active'] = 'inventory_item'
        CONTEXT['module'] = 'iwms'
        CONTEXT['model'] = 'inventory_item'
        categories = Category.query.all()
        types = StockItemType.query.all()

        stocks = ItemBinLocations.query.filter_by(inventory_item_id=oid).all()

        return render_template('iwms/inventory_item/iwms_inventory_item_edit.html', oid=oid,context=CONTEXT,form=f,stocks=stocks,\
            title="View inventory item",number=ii.stock_item.number,name=ii.stock_item.name,categories=categories,types=types)
    elif request.method == "POST":
        if f.validate_on_submit():
            ii.default_price = f.default_price.data
            ii.default_cost = f.default_cost.data
            ii.stock_item_type_id = f.stock_item_type_id.data if not f.stock_item_type_id.data == '' else None
            ii.category_id = f.category_id.data if not f.category_id.data == '' else None
            ii.updated_by = "{} {}".format(current_user.fname,current_user.lname)
            ii.updated_at = datetime.now()
            db.session.commit()
            flash('Inventory Item update Successfully!','success')
            return redirect(url_for('bp_iwms.inventory_items'))
        else:
            for key, value in form.errors.items():
                flash(str(key) + str(value), 'error')
            return redirect(url_for('bp_iwms.inventory_items'))
