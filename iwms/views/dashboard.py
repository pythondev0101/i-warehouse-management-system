from sqlalchemy import func
from flask import render_template
from flask_login import login_required
from app import CONTEXT
from app.admin.routes import admin_dashboard
from iwms import bp_iwms
from iwms.models import (
    ItemBinLocations, StockReceipt, StockReceiptItemLine, InventoryItem, PurchaseOrder,
    Putaway, PurchaseOrderProductLine, SalesOrder, SalesOrderLine
)



@bp_iwms.route('/')
@bp_iwms.route('/dashboard')
@login_required
def dashboard():
    
    """ DATA SA DASHBOARD """
    _qty_on_hand = ItemBinLocations.query.with_entities(func.sum(ItemBinLocations.qty_on_hand)).all()
    _qty_to_be_received = StockReceipt.query.filter_by(status="LOGGED").join(StockReceiptItemLine)\
        .with_entities(func.sum(StockReceiptItemLine.received_qty)).all()
    _all_items = InventoryItem.query.count()
    _to_be_purchased = PurchaseOrder.query.count()
    _to_be_receipted = StockReceipt.query.count()
    _to_be_stored = Putaway.query.count()

    _po_logged = PurchaseOrder.query.filter_by(status="LOGGED").count()
    _po_pending = PurchaseOrder.query.filter_by(status="PENDING").count()
    _po_released = PurchaseOrder.query.filter_by(status="RELEASED").count()
    _po_completed = PurchaseOrder.query.filter_by(status="COMPLETED").count()
    _po_data ={
        'logged': _po_logged,
        'pending': _po_pending,
        'released': _po_released,
        'completed': _po_completed
    }

    _sr_remaining_items = PurchaseOrder.query.filter_by(status="PENDING").join(PurchaseOrderProductLine)\
        .with_entities(func.sum(PurchaseOrderProductLine.remaining_qty)).all()
    _sr_incomplete_items = PurchaseOrder.query.filter(PurchaseOrder.status.in_(["LOGGED","PENDING"]))\
        .join(PurchaseOrderProductLine).filter_by(received_qty=None)\
        .with_entities(func.sum(PurchaseOrderProductLine.remaining_qty)).all()
    _sr_data = {
        'completed': str(_qty_to_be_received[0][0]),
        'remaining': str(_sr_remaining_items[0][0]),
        'incomplete': str(_sr_incomplete_items[0][0]),
    }

    _pwy_data = {
        'to_be_stored_qty': str(_qty_to_be_received[0][0]),
        'stored': str(_qty_on_hand[0][0]),
    }

    _to_be_pick_qty = SalesOrder.query.filter(SalesOrder.status.in_(["LOGGED","ON HOLD"])).join(SalesOrderLine)\
        .with_entities(func.sum(SalesOrderLine.qty)).all()
    _picked_qty = SalesOrder.query.join(SalesOrderLine)\
        .with_entities(func.sum(SalesOrderLine.issued_qty)).all()

    _pck_data = {
        'to_be_pick_qty': str(_to_be_pick_qty[0][0]),
        'picked_qty': str(_picked_qty[0][0]),
    }

    _total_orders = SalesOrder.query.count()
    _items_to_be_confirmed = SalesOrderLine.query.count()
    _items_confirmed = SalesOrderLine.query.join(SalesOrder).filter(SalesOrder.status.in_(["CONFIRMED"]))\
        .count()

    dashboard_data = {
        'qty_on_hand': str(_qty_on_hand[0][0]),
        'qty_to_be_received': str(_qty_to_be_received[0][0]),
        'all_items': _all_items,
        'to_be_purchased': _to_be_purchased,
        'to_be_receipted': _to_be_receipted,
        'to_be_stored': _to_be_stored,
        'po_data': _po_data,
        'sr_data': _sr_data,
        'pwy_data': _pwy_data,
        'total_orders': _total_orders,
        'items_to_be_confirmed': _items_to_be_confirmed,
        'pck_data': _pck_data,
        'items_confirmed': _items_confirmed
    }

    return admin_dashboard('iwms/iwms_dashboard.html', data=dashboard_data,title="Dashboard")
