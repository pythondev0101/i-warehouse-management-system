from datetime import datetime
from flask import render_template
from flask_login import login_required
from app import CONTEXT
from iwms import bp_iwms
from iwms.models import (
    SalesOrder, Client, InventoryItem, PurchaseOrder, PurchaseOrderProductLine, ItemBinLocations
)



@bp_iwms.route('/reports')
@login_required
def reports():
    CONTEXT['module'] = 'iwms'
    CONTEXT['active'] = 'reports'
    CONTEXT['mm-active'] = ""

    _top_clients = db.session.query(Client.code,Client.name,func.count(Client.id))\
        .join(SalesOrder.client).group_by(Client.id).order_by(func.count(Client.id).desc()).all()

    _sales_clients = db.session.query(Client.name,func.sum(SalesOrder.total_price))\
        .join(SalesOrder.client).group_by(Client.id).all()

    _sales_clients_dict = []

    for x in _sales_clients:
        _sales_clients_dict.append({
            'name':x[0],
            'sales':str(x[1])
        })

    _pos = PurchaseOrder.query.join(PurchaseOrderProductLine).order_by(PurchaseOrder.po_number.desc()).all()

    _sos = SalesOrder.query.join(SalesOrderLine).order_by(SalesOrder.number.desc()).all()

    _top_items = db.session.query(StockItem.name,StockItem.description,func.count(StockItem.id))\
        .join(PurchaseOrderProductLine.stock_item).group_by(StockItem.id).order_by(func.count(StockItem.id).desc()).all()

    _top_sale_items = db.session.query(StockItem.name,StockItem.description,func.count(InventoryItem.id))\
        .join(InventoryItem, StockItem.id == InventoryItem.stock_item_id)\
        .join(SalesOrderLine, InventoryItem.id == SalesOrderLine.inventory_item_id).group_by(InventoryItem.id).order_by(func.count(InventoryItem.id).desc()).all()

    _low_sale_items = db.session.query(StockItem.name,StockItem.description,func.count(InventoryItem.id))\
        .join(InventoryItem, StockItem.id == InventoryItem.stock_item_id)\
        .join(SalesOrderLine, InventoryItem.id == SalesOrderLine.inventory_item_id).group_by(InventoryItem.id).order_by(func.count(InventoryItem.id)).all()

    _srs = StockReceipt.query.join(StockReceiptItemLine).order_by(StockReceipt.sr_number.desc()).all()

    _item_expiration = ItemBinLocations.query.order_by(desc(ItemBinLocations.expiry_date)).all()

    _item_expiration_list = []
    if _item_expiration:
        for item in _item_expiration:
            status = ''
            if item.expiry_date < datetime.now():
                status = 'EXPIRED'
            else:
                status = 'GOOD'
                
                if (item.expiry_date - datetime.now()).days < 30:
                    status = "NEARLY EXPIRED"

            _item_expiration_list.append([item,status])

    report_data = {
        'top_clients': _top_clients,
        'sales_clients': _sales_clients_dict,
        'pos':_pos,
        'sos': _sos,
        'top_items': _top_items,
        'top_so_items': _top_sale_items,
        'low_so_items': _low_sale_items,
        'srs': _srs,
        'item_expiration': _item_expiration_list
    }

    return render_template('iwms/iwms_reports.html',context=CONTEXT,title="Reports",rd=report_data)
