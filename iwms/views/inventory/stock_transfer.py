from flask import (
    render_template, request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from app.admin.routes import admin_table, admin_edit
from iwms import bp_iwms

@bp_iwms.route('/stock_transfers')
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
        
    CONTEXT['mm-active'] = 'stock_transfer'
    return admin_table(InventoryItem,fields=fields,form=StockTransferForm(), \
        template='iwms/stock_transfer/iwms_stock_transfer_index.html',edit_url="bp_iwms.stock_transfer_edit",\
            create_modal=True,view_modal="iwms/stock_transfer/iwms_stock_transfer_view_modal.html",create_url=False,kwargs={'active':'inventory',
            'models': mmodels
            })


@bp_iwms.route('/stock_transfer_edit/<int:oid>',methods=['GET'])
@login_required
def stock_transfer_edit(oid):
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
        bin_locations = BinLocation.query.all()

        return render_template('iwms/stock_transfer/iwms_stock_transfer_edit.html', oid=oid,context=CONTEXT,form=f,stocks=stocks,\
            title="Transfer stock",number=ii.stock_item.number,name=ii.stock_item.name,categories=categories,types=types,bin_locations=bin_locations)
