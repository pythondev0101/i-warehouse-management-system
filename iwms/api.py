from sqlalchemy import func
from flask import request, jsonify
from flask_cors import cross_origin
from iwms import bp_iwms
from iwms.models import StockItem, PurchaseOrder, UnitOfMeasure, Warehouse, BinLocation,\
    StockReceipt, InventoryItem, ItemBinLocations, SalesOrder
from iwms.functions import check_fast_slow



@bp_iwms.route("/api/get-supplier-products",methods=['GET'])
def get_supplier_products():
    sup_id = request.args.get('sup_id')
    po_number = request.args.get('po_number', None)
    db_items = StockItem.query.filter(StockItem.suppliers.any(id=sup_id)).all()
    po_line = []

    if po_number is not None:
        po = PurchaseOrder.query.filter_by(po_number=po_number).first()
        
        if po:
            po_line = [x.stock_item.id for x in po.product_line]
        
    list_items = []
    
    for item in db_items:
        if item.id not in po_line:
            list_items.append({
                'id':item.id,
                'number':item.number,
                'name':item.name,
                'description':item.description,
                'barcode':item.barcode,
                'default_cost':str(item.default_cost)
                })
    
    response = jsonify(items=list_items)
    response.status_code = 200

    return response


@bp_iwms.route('/api/get-product-uom-line',methods=['GET'])
def get_product_uom_line():

    stock_item_id = int(request.args.get('stock_item_id'))

    # Pag 0 means kukunin nya lahat ang uom
    if stock_item_id == 0:
        obj = UnitOfMeasure.query.all()
        uom_line = []

        for line in obj:
            uom_line.append({'id':line.id,'code':line.code})
        response = jsonify(uom_lines=uom_line)

    else:
        obj = StockItem.query.get_or_404(stock_item_id)
        uom_line = []
        for line in obj.uom_line:
            default = "false"
            if line.uom_id == obj.unit_id:
                default = 'true'
            uom_line.append({'id':line.uom_id,'code':line.uom.code,'default':default})
        response = jsonify(uom_lines=uom_line)
    
    response.status_code = 200

    return response


@bp_iwms.route('/api/purchase-orders/<int:poID>/products',methods=["GET"])
def get_po_products(poID):
    po = PurchaseOrder.query.get_or_404(poID)
    po_line = []
    
    for line in po.product_line:
        po_line.append({
            'id':line.stock_item.id,'name':line.stock_item.name,
            'uom':line.uom.code if line.uom is not None else '',
            'number':line.stock_item.number,
            'qty':line.qty,
            'remaining_qty':line.remaining_qty,
            'received_qty':line.received_qty
            })
    
    response = jsonify(items=po_line)
    response.status_code = 200

    return response


@bp_iwms.route('/api/bin-locations',methods=['GET'])
def get_bin_locations():

    _fast_slow = request.args.get('fast_slow')
    _warehouse_name = request.args.get('warehouse')
    _bin_list = []
    _warehouse = Warehouse.query.filter_by(name=_warehouse_name).first()
    _cold_storage = Warehouse.query.filter_by(name="COLD STORAGE").first()

    if _fast_slow == 'FAST':
        
        if _warehouse_name == 'COLD STORAGE':
            _bins = BinLocation.query.filter_by(warehouse_id=_warehouse.id).order_by(BinLocation.code).limit(50).all()
        else:
            _bins = BinLocation.query.filter(BinLocation.warehouse_id != _cold_storage.id).order_by(BinLocation.code).limit(50).all()

        for x in _bins:
            _bin_list.append({
                'id': x.id,
                'code': x.code,
            })
    elif _fast_slow == 'SLOW':

        if _warehouse_name == 'COLD STORAGE':
            _bins = BinLocation.query.filter_by(warehouse_id=_warehouse.id).order_by(BinLocation.code.desc()).limit(50).all()
        else:
            _bins = BinLocation.query.filter(BinLocation.warehouse_id != _cold_storage.id).order_by(BinLocation.code.desc()).limit(50).all()
        
        for x in _bins:
            _bin_list.append({
                'id': x.id,
                'code': x.code,
            })
    else:
        if _cold_storage:
            _bins = BinLocation.query.filter(BinLocation.warehouse_id != _cold_storage.id).order_by(BinLocation.code).all()
        _bins = BinLocation.query.order_by(BinLocation.code).all()

        for x in _bins:
            _bin_list.append({
                'id': x.id,
                'code': x.code,
            })

    response = jsonify(bins=_bin_list)
    response.status_code = 200

    return response


@bp_iwms.route('/api/stock-receipts/<int:srID>/products',methods=["GET"])
def get_sr_products(srID):

    sr = StockReceipt.query.get_or_404(srID)
    sr_line = []

    for line in sr.item_line:
        if line:
            _expiry_date = ''
            if line.expiry_date is not None:
                _expiry_date = line.expiry_date.strftime("%Y-%m-%d")

            _ii = InventoryItem.query.filter_by(stock_item_id=line.stock_item.id).first()
            if not _ii == None:
                _ibl = ItemBinLocations.query.with_entities(func.sum(ItemBinLocations.qty_on_hand)).filter_by(inventory_item_id=_ii.id).all()
            else:
                _ibl = [[0]]

            fast_slow = ""
            if not line.stock_item.inventory_stock_item == []:
                if check_fast_slow(line.stock_item.inventory_stock_item[0].id):
                    fast_slow = "FAST"
                else:
                    fast_slow = "SLOW"

            sr_line.append({
                'id':line.stock_item.id,'name':line.stock_item.name,
                'uom':line.uom,'number':line.stock_item.number,
                'lot_no':line.lot_no,'expiry_date': _expiry_date,
                'received_qty':line.received_qty,
                'prev_stored': str(_ibl[0][0]) if not _ibl[0][0] == None else 0,
                'is_putaway': line.is_putaway,
                'fast_slow': fast_slow
                })

    response = jsonify(items=sr_line)
    response.status_code = 200

    return response


@bp_iwms.route('/api/sales-orders/<int:oid>/products',methods=['GET'])
def get_sales_orders_products(oid):
    so = SalesOrder.query.get_or_404(oid)
    so_line = []

    for line in so.product_line:
        if line:
            _expiry_date = ''
            if line.item_bin_location.expiry_date is not None:
                _expiry_date = line.item_bin_location.expiry_date.strftime("%Y-%m-%d")

            so_line.append({
                'id':line.item_bin_location_id,'name':line.inventory_item.stock_item.name,
                'uom':line.uom.code,'number':line.inventory_item.stock_item.number,
                'lot_no':line.item_bin_location.lot_no,'expiry_date': _expiry_date,
                'qty':line.qty,'bin_location': line.item_bin_location.bin_location.code,
                'issued_qty': line.issued_qty
                })

    res = jsonify(items=so_line)
    res.status_code = 200
    return res


@bp_iwms.route('/api/inventory-items/<int:oid>',methods=["GET"])
@cross_origin()
def get_ii_view_modal_data(oid):
    ii = InventoryItem.query.get_or_404(oid)
    res = {}
    res['name'] = ii.stock_item.name
    res['number'] = ii.stock_item.number
    res['price'] = str(ii.default_price)
    res['cost'] = str(ii.default_cost)
    res['stock_item_type_id'] = ii.stock_item_type_id
    res['category_id'] = ii.category_id

    resp = jsonify(result=res)
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.status_code = 200
    
    return resp


@bp_iwms.route('/_get_SO_status',methods=['POST'])
def _get_SO_status():
    if request.method == 'POST':
        _id = request.json['id']
        _so = SalesOrder.query.get(_id)
        editable = False
        if _so.status == "LOGGED":
            editable = True
        return jsonify({'editable':editable})


@bp_iwms.route('/_get_PO_status',methods=['POST'])
def _get_PO_status():
    if request.method == 'POST':
        _id = request.json['id']
        _po = PurchaseOrder.query.get(_id)
        editable = False
        if _po.status == "LOGGED":
            editable = True
        return jsonify({'editable':editable})


@bp_iwms.route('/_barcode_check', methods=['POST'])
def _barcode_check():
    if request.method == 'POST':
        barcode = request.json['barcode']
        check = StockItem.query.filter(StockItem.barcode == barcode).first()
        if check:
            resp = jsonify(result=0)
            resp.status_code = 200
            return resp
        else:
            resp = jsonify(result=1)
            resp.status_code = 200
            return resp