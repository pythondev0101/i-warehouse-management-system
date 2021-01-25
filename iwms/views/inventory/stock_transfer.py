from datetime import datetime
from sqlalchemy import func
from flask import (
    render_template, request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from sqlalchemy.sql.expression import false
from app import db, CONTEXT
from iwms.logging import create_log
from app.admin import admin_render_template
from app.admin.routes import admin_table, admin_edit
from app.auth.permissions import check_create
from iwms import bp_iwms
from iwms.models import InventoryItem, StockItem, Category, StockItemType, ItemBinLocations,\
    BinLocation, StockTransfer
from iwms.forms import StockTransferForm, InventoryItemEditForm



@bp_iwms.route('/stock-transfers')
@login_required
def stock_transfers():
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

    return admin_table(StockTransfer,fields=fields,form=StockTransferForm(), \
        template='iwms/stock_transfer/iwms_stock_transfer_index.html',edit_url="bp_iwms.stock_transfer_edit",\
            create_modal=False,view_modal="iwms/stock_transfer/iwms_stock_transfer_view_modal.html",\
                kwargs={'model_data': mmodels})


@bp_iwms.route('/stock-transfers/<int:oid>/edit',methods=['GET'])
@login_required
def stock_transfer_edit(oid):
    ii = InventoryItem.query.get_or_404(oid)
    f = InventoryItemEditForm(obj=ii)
    if request.method == "GET":

        CONTEXT['model'] = 'stock_transfer'
        categories = Category.query.all()
        types = StockItemType.query.all()

        stocks = ItemBinLocations.query.filter_by(inventory_item_id=oid).all()
        bin_locations = BinLocation.query.all()

        return admin_render_template('iwms/stock_transfer/iwms_stock_transfer_edit.html', 'iwms',oid=oid,form=f,stocks=stocks,\
            title="Transfer stock",number=ii.stock_item.number,name=ii.stock_item.name,categories=categories,types=types,bin_locations=bin_locations)
