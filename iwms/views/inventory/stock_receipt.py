from datetime import datetime
from flask import (
    render_template, request, redirect, flash, url_for, jsonify 
    )
from flask_login import login_required, current_user
from app import db, CONTEXT
from iwms.logging import create_log
from app.admin import admin_render_template
from app.admin.routes import admin_table, admin_edit
from app.auth.permissions import check_create
from iwms import bp_iwms
from iwms.models import StockReceipt, PurchaseOrder, Source, StockItem, Warehouse,\
    StockReceiptItemLine
from iwms.forms import StockReceiptViewForm, StockReceiptCreateForm
from iwms.functions import generate_number



scripts = [
    {'bp_iwms.static': 'js/stock_receipt.js'}
]

modals = [
    "iwms/stock_receipt/search_po_modal.html",
    "iwms/stock_receipt/po_line_modal.html",
    "iwms/stock_receipt/confirm_modal.html"
]


@bp_iwms.route('/stock-receipts')
@login_required
def stock_receipts():
    fields = [StockReceipt.id,StockReceipt.sr_number,StockReceipt.created_at,StockReceipt.created_by,StockReceipt.status]
    models = StockReceipt.query.with_entities(*fields).filter(StockReceipt.status.in_(['LOGGED','PENDING'])).all()
    
    return admin_table(StockReceipt,fields=fields,form=StockReceiptViewForm(),create_modal=False,\
        create_button=True, kwargs={'model_data': models}, create_url="bp_iwms.create_stock_receipt")


@bp_iwms.route('/stock-receipts/create', methods=['GET','POST'])
@login_required
def create_stock_receipt():
    sr_generated_number = ""
    sr = db.session.query(StockReceipt).order_by(StockReceipt.id.desc()).first()

    if sr:
        sr_generated_number = generate_number("SR",sr.id)
    else:
        sr_generated_number = "SR00000001"
    
    form = StockReceiptCreateForm()
    
    if request.method == "GET":
        po_list = PurchaseOrder.query.filter(PurchaseOrder.status.in_(['LOGGED','PENDING']))
        sources = Source.query.all()
        
        data = {
            'po_list': po_list,
            'sources': sources,
            'sr_generated_number': sr_generated_number
        }

        CONTEXT['model'] = 'stock_receipt'

        return admin_render_template('iwms/stock_receipt/iwms_stock_receipt_create.html', 'iwms',\
            form=form,title="Create stock receipt", data=data, scripts=scripts, modals=modals)

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.stock_receipts'))
    
    try:
        obj = StockReceipt()
        obj.sr_number = sr_generated_number
        po = PurchaseOrder.query.filter_by(po_number=form.po_number.data).first()
        obj.purchase_order = po
        obj.status = "LOGGED"
        obj.warehouse_id = po.warehouse_id
        obj.source_id = form.source.data if not form.source.data == '' else None
        obj.po_number = form.po_number.data
        obj.supplier = form.supplier.data
        obj.reference = form.reference.data
        obj.si_number = form.si_number.data
        obj.bol = form.bol.data
        obj.remarks = form.remarks.data
        obj.date_received = form.date_received.data
        obj.putaway_txn = form.putaway_txn.data
        obj.created_by = "{} {}".format(current_user.fname,current_user.lname)

        """ po.status = RELEASED if no remaining qty in the PO items """
        _remaining = 0
        
        item_list = request.form.getlist('sr_items[]')
        if item_list:
            for item_id in item_list:

                """ Add SR confirm PO items """

                item = StockItem.query.get(item_id)
                lot_no = request.form.get("lot_no_{}".format(item_id))
                expiry_date = request.form.get("expiry_date_{}".format(item_id)) if not request.form.get("expiry_date_{}".format(item_id)) == '' else None
                uom = request.form.get("uom_{}".format(item_id))
                received_qty = request.form.get("received_qty_{}".format(item_id)) if not request.form.get("received_qty_{}".format(item_id)) == '' else None
                net_weight = request.form.get("net_weight_{}".format(item_id)) if not request.form.get("net_weight_{}".format(item_id)) == '' else None
                timestamp = request.form.get("timestamp_{}".format(item_id))
                line = StockReceiptItemLine(stock_item=item,lot_no=lot_no,expiry_date=expiry_date,\
                    uom=uom,received_qty=received_qty,net_weight=net_weight)
                obj.item_line.append(line)

                """ Updates PO remaining qty and received qty product line """

                for ip in po.product_line:
                    if int(item_id) == ip.stock_item_id:
                        if not ip.received_qty is None:
                            ip.received_qty = ip.received_qty + int(received_qty)
                        else:
                            ip.received_qty = int(received_qty)
                        ip.remaining_qty = ip.remaining_qty - int(received_qty)

        for ip in po.product_line:
            _remaining = _remaining + ip.remaining_qty               

        if _remaining == 0:
            po.status = "RELEASED"
        else:
            po.status = "PENDING"

        db.session.add(obj)
        db.session.commit()
        create_log('New stock receipt added','SRID={}'.format(obj.id))
        flash('New Stock Receipt added Successfully!','success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.stock_receipts'))



@bp_iwms.route("/_create_label",methods=['POST'])
def _create_label():
    import os
    basedir = os.path.abspath(os.path.dirname(__file__))
    basedir = basedir + "/pallet_tag/barcodetxtfile.txt"

    _lot_no = request.json['lot_no']
    _expiry_date = request.json['expiry_date']
    _label = request.json['label']
    _quantity = request.json['quantity']
    _sr_number = request.json['sr_number']
    _po_number = request.json['po_number']
    _stock_id = request.json['stock_id']
    _supplier = request.json['supplier']

    stock_item = StockItem.query.get_or_404(_stock_id)
    _description = stock_item.description
    # SR ,PO ,LOTNUM,EXPIRY DAT,Description ,QTY,Supplier ,SR ,number_of_label

    with open(basedir, 'w+') as the_file:
        txt = "{},{},{},{},{},{},{},{},{}".format(_sr_number,_po_number,\
            _lot_no,_expiry_date,_description,_quantity,_supplier,_sr_number,_label)
        the_file.write(txt)
    
    """ Call .bat to generate pallet tag """
    import subprocess

    filepath= r"D:\iWMS\app\iwms\pallet_tag\printPalletTag.bat"
    p = subprocess.Popen(filepath, shell=True, stdout = subprocess.PIPE)

    stdout, stderr = p.communicate()
    print(p.returncode) # is 0 if success

    res = jsonify({'result':True})
    return res
