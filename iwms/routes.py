from datetime import datetime
import pdfkit
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
from flask_mail import Message
from sqlalchemy import and_, func, desc
from flask_cors import cross_origin
from app import CONTEXT
from app import db, mail
from app.core.models import CoreLog
from app.auth.models import User
from app.admin.routes import admin_table, admin_edit
from iwms import bp_iwms
from .models import (
    Group,Department,TransactionType,Warehouse,Zone,BinLocation,Category,StockItem,UnitOfMeasure,
    Reason,StockReceipt,Putaway, Email as EAddress, PurchaseOrder, Supplier, Term, 
    PurchaseOrderProductLine,StockItemType,TaxCode, StockItemUomLine,StockReceiptItemLine,
    PutawayItemLine,Source, ShipVia, ClientGroup, Client, InventoryItem, 
    ItemBinLocations,SalesOrder,SalesOrderLine,Picking,PickingItemLine
    )
from .forms import *



"""----------------------INTERNAL FUNCTIONS-------------------------"""



def _check_create(model_name):
    #TODO: Temporary lang to pang check, maganda sana gawing decorator siguro 
    if current_user.is_superuser:
        return True
    else:
        user = User.query.get(current_user.id)
        for perm in user.permissions:
            if model_name == perm.model.name:
                if not perm.create:
                    return False
        return False

def _log_create(description,data):
    log = CoreLog()
    log.user_id = current_user.id
    log.date = datetime.utcnow()
    log.description = description
    log.data = data
    db.session.add(log)
    db.session.commit()
    print("Log created!")




"""----------------------APIs-------------------------"""

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



@bp_iwms.route('/_get_PO_status',methods=['POST'])
def _get_PO_status():
    if request.method == 'POST':
        _id = request.json['id']
        _po = PurchaseOrder.query.get(_id)
        editable = False
        if _po.status == "LOGGED":
            editable = True
        return jsonify({'editable':editable})


@bp_iwms.route('/_get_SO_status',methods=['POST'])
def _get_SO_status():
    if request.method == 'POST':
        _id = request.json['id']
        _so = SalesOrder.query.get(_id)
        editable = False
        if _so.status == "LOGGED":
            editable = True
        return jsonify({'editable':editable})


@bp_iwms.route('/_update_bin_coord', methods=['POST'])
def _update_bin_coord():
    if request.method == 'POST':
        _bin_code = request.json['bin_code']
        _x,_y = request.json['x'], request.json['y']
        print(_x,_y);
        bin = BinLocation.query.filter_by(code=_bin_code).first()
        bin.x = _x / 2
        bin.y = _y / 2
        db.session.commit()
        return jsonify({'Result':True})

@bp_iwms.route('/_get_bin_items',methods=['POST'])
def _get_bin_items():
    if request.method == 'POST':
        _bin_code = request.json['bin_code']
        bin = BinLocation.query.filter_by(code=_bin_code).first()
        items = []
        for x in bin.item_bin_locations:
            items.append({
                'name': x.inventory_item.stock_item.name,
                'qty_on_hand': x.qty_on_hand,
                'lot_no': x.lot_no,
                'expiry_date': x.expiry_date,
            })
        return jsonify(res=items)

@bp_iwms.route('/_create_bin',methods=['POST'])
def _create_bin():
    _bin_code = request.json['bin_code']
    bin = BinLocation()
    bin.code = _bin_code
    bin.x = 0
    bin.y = 0
    db.session.add(bin)
    db.session.commit()
    return jsonify({"Result":True})







@bp_iwms.route('/_get_so_line',methods=['POST'])
def _get_so_line():
    if request.method == "POST":
        so_id = request.json['so_id']
        so = SalesOrder.query.get_or_404(so_id)
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


"""----------------------ROUTE FUNCTIONS-------------------------"""

@bp_iwms.route('/users')
@login_required
def users():
    from app.auth.routes import index
    # TODO: CONTEXT['mm-active'] para lang sa gui ilagay na to sa admin index at edit,dapat wala dito to
    CONTEXT['mm-active'] = 'Users'
    return index(template='iwms/iwms_index.html',active='system',edit_url='bp_iwms.iwms_user_edit',create_url='bp_iwms.iwms_user_create')

@bp_iwms.route('/user_edit/<int:oid>', methods=['GET', 'POST'])
def iwms_user_edit(oid):
    from app.auth.routes import user_edit
    CONTEXT['mm-active'] = 'Users'
    return user_edit(oid=oid,template='iwms/iwms_edit.html',active='system',update_url='bp_iwms.iwms_user_edit')

@bp_iwms.route('/user_create/',methods=['POST'])
def iwms_user_create():
    from app.auth.routes import user_create
    CONTEXT['mm-active'] = 'Users'
    return user_create(url='bp_iwms.users')

@bp_iwms.route('/groups')
@login_required
def groups():
    fields = [Group.id,Group.name,Group.created_by,Group.created_at,Group.updated_by,Group.updated_at]
    CONTEXT['mm-active'] = 'Groups'
    return admin_table(Group,fields=fields,create_url='bp_iwms.group_create',edit_url='bp_iwms.group_edit' , \
        form=GroupForm(),template="iwms/iwms_index.html",kwargs={'active':'system'})

@bp_iwms.route('/group_create',methods=['POST'])
@login_required
def group_create():
    if _check_create('Groups'):
        form = GroupForm()
        if request.method == "POST":
            if form.validate_on_submit():
                try:
                    group = Group()
                    group.name = form.name.data
                    group.created_by = "{} {}".format(current_user.fname,current_user.lname)
                    db.session.add(group)
                    db.session.commit()
                    flash('New group added successfully!','success')
                    _log_create('New group added',"GroupID={}".format(group.id))
                    return redirect(url_for('bp_iwms.groups'))
                except Exception as e:
                    flash(str(e),'error')
                    return redirect(url_for('bp_iwms.groups'))
            else:
                for key, value in form.errors.items():
                    flash(str(key) + str(value), 'error')
                return redirect(url_for('bp_iwms.groups'))
    else:
        return render_template("auth/authorization_error.html")

@bp_iwms.route('/group_edit/<int:oid>',methods=['GET','POST'])
@login_required
def group_edit(oid):
    group = Group.query.get_or_404(oid)
    form = GroupEditForm(obj=group)
    if request.method == "GET":
        CONTEXT['mm-active'] = 'Groups'
        return admin_edit(form,'bp_iwms.group_edit',oid,model=Group,template='iwms/iwms_edit.html',kwargs={'active':'system'})
    elif request.method == "POST":
        if form.validate_on_submit():
            try:
                group.name = form.name.data
                group.updated_at = datetime.now()
                group.updated_by = "{} {}".format(current_user.fname,current_user.lname)
                db.session.commit()
                flash('Group update Successfully!','success')
                _log_create("Group update","GroupID={}".format(group.id))
                return redirect(url_for('bp_iwms.groups'))
            except Exception as e:
                flash(str(e),'error')
                return redirect(url_for('bp_iwms.groups'))
        else:    
            for key, value in form.errors.items():
                flash(str(key) + str(value), 'error')
            return redirect(url_for('bp_iwms.groups'))


@bp_iwms.route("/backup")
@login_required
def backup():
    from .backup import backup
    try:
        _backup,_db = backup()
        return send_from_directory(directory=_backup,filename=_db,as_attachment=True)
    except Exception as e:
        flash(str(e),'error')
        return redirect(url_for('bp_iwms.logs'))


@bp_iwms.route('/logs')
@login_required
def logs():
    from app.auth.models import User
    fields = [CoreLog.id,User.fname,CoreLog.date,CoreLog.description,CoreLog.data]
    models = [CoreLog,User]
    CONTEXT['mm-active'] = 'logs'
    return admin_table(*models,fields=fields,template='iwms/iwms_index.html',action="iwms/iwms_system_actions.html",create_modal=False,view_modal=False,kwargs={
        'index_title':'System Logs and backup','index_headers':['User','Date','Description','Data'],'index_message':'List of items',
        'active':'system'})


@bp_iwms.route('/client_groups')
@login_required
def client_groups():
    fields = [ClientGroup.id,ClientGroup.name,ClientGroup.updated_by,ClientGroup.updated_at]
    CONTEXT['mm-active'] = 'client_group'
    return admin_table(ClientGroup,fields=fields,form=ClientGroupForm(), \
        template='iwms/iwms_index.html', edit_url='bp_iwms.client_group_edit',\
            create_url="bp_iwms.client_group_create",kwargs={'active':'sales'})

@bp_iwms.route('/client_group_create',methods=['POST'])
@login_required
def client_group_create():
    f = ClientGroupForm()
    if request.method == "POST":
        if f.validate_on_submit():
            obj = ClientGroup()
            obj.name = f.name.data
            obj.created_by = "{} {}".format(current_user.fname,current_user.lname)
            db.session.add(obj)
            db.session.commit()
            _log_create('New client group added','ClientGroupID={}'.format(obj.id))
            flash("New client group added successfully!",'success')
            return redirect(url_for('bp_iwms.client_groups'))
        else:
            for key, value in f.errors.items():
                flash(str(key) + str(value), 'error')
            return redirect(url_for('bp_iwms.client_groups'))

@bp_iwms.route('/client_group_edit/<int:oid>',methods=['GET','POST'])
@login_required
def client_group_edit(oid):
    obj = ClientGroup.query.get_or_404(oid)
    f = ClienGroupEditForm(obj=obj)
    if request.method == "GET":
        CONTEXT['mm-active'] = 'client_group'
        return admin_edit(f,'bp_iwms.client_group_edit',oid, \
            model=ClientGroup,template='iwms/iwms_edit.html',kwargs={'active':'sales'})
    elif request.method == "POST":
        if f.validate_on_submit():
            obj.name = f.name.data
            obj.updated_by = "{} {}".format(current_user.fname,current_user.lname)
            obj.updated_at = datetime.now()
            db.session.commit()
            _log_create('Client group update','ClientGroupID={}'.format(obj.id))
            flash('Client group update Successfully!','success')
            return redirect(url_for('bp_iwms.client_groups'))
        else:
            for key, value in form.errors.items():
                flash(str(key) + str(value), 'error')
            return redirect(url_for('bp_iwms.client_groups'))


@bp_iwms.route('/_transfer_location',methods=['POST'])
@login_required
def _transfer_location():
    if request.method == 'POST':
        _item_bin_location_id = request.json['item_bin_location_id']
        _new_bin_location_id = request.json['new_bin_location_id']
        item_bin_location = ItemBinLocations.query.get_or_404(_item_bin_location_id)
        _old_location = item_bin_location.bin_location.code

        item_bin_location.bin_location_id = _new_bin_location_id
        db.session.commit()

        msg = Message('Transfer Location', sender = current_app.config['MAIL_USERNAME'], recipients = ["iwarehouseonline2020@gmail.com"])
        msg.body = "Your stock items - ({}) was transferred to better bin location from {} to {}."\
            .format(item_bin_location.inventory_item.stock_item.name,_old_location,item_bin_location.bin_location.code)
        mail.send(msg)

        resp = jsonify({'result':True})
        resp.headers.add('Access-Control-Allow-Origin', '*')
        resp.status_code = 200
        return resp


@bp_iwms.route('/_get_ii_view_modal_data',methods=["POST"])
@cross_origin()
def get_ii_view_modal_data():
    id = request.json['id']
    # query = "select {} from {} where id = {} limit 1".format(column,table,id)
    # sql = text(query)
    # row = db.engine.execute(sql)
    # res = [x[0] if x[0] is not None else '' for x in row]

    # resp = jsonify(result=str(res[0]),column=column)
    res = {}
    ii = InventoryItem.query.get_or_404(id)
    res['name'] = ii.stock_item.name
    res['number'] = ii.stock_item.number
    res['price'] = str(ii.default_price)
    res['cost'] = str(ii.default_cost)
    res['stock_item_type_id'] = ii.stock_item_type_id
    res['category_id'] = ii.category_id
    print(res)
    resp = jsonify(result=res)
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.status_code = 200
    return resp


@bp_iwms.route('/excel', methods=['POST'])
def excel():
    import pymysql.cursors
    from xlsxwriter.workbook import Workbook
    import os
    import datetime

    _from_date = request.form['from_date']
    _to_date = request.form['to_date']

    # Connect to the database
    connection = pymysql.connect(host=os.environ.get('DATABASE_HOST'),
                                user=os.environ.get('DATABASE_USER'),
                                password=os.environ.get('DATABASE_PASSWORD'),
                                db=os.environ.get('DATABASE_NAME'),
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        sql = "SELECT po_number, status, ship_to, address, remarks, ordered_date, delivery_date FROM `iwms_purchase_order` WHERE `ordered_date` between '{}' and '{}'".format(_from_date, _to_date)
        cursor.execute(sql)
        results = cursor.fetchall()

        workbook_name = "po" + str(datetime.datetime.now())
        file_path = current_app.config['PDF_FOLDER'] + workbook_name + '.xlsx'
        print(file_path)

        workbook = Workbook(file_path)
        sheet = workbook.add_worksheet()
        for r, row in enumerate(results):
            for c, col in enumerate(row):
                sheet.write(r, c, row[col])
        workbook.close()

    connection.close()
    flash('Export to {}'.format(file_path),'success')
    return redirect(url_for('bp_iwms.reports'))


@bp_iwms.route('/excel_so', methods=['POST'])
def excel_so():
    import pymysql.cursors
    from xlsxwriter.workbook import Workbook
    import os
    import datetime
    import platform
    from config import basedir

    _from_date = request.form['so_from_date']
    _to_date = request.form['so_to_date']

    # Connect to the database
    connection = pymysql.connect(host=os.environ.get('DATABASE_HOST'),
                                user=os.environ.get('DATABASE_USER'),
                                password=os.environ.get('DATABASE_PASSWORD'),
                                db=os.environ.get('DATABASE_NAME'),
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        sql = "SELECT * FROM `iwms_sales_order` WHERE `ordered_date` between '{}' and '{}'".format(_from_date, _to_date)
        cursor.execute(sql)
        results = cursor.fetchall()

        workbook_name = "so" + str(datetime.datetime.now())
        
        file_path = current_app.config['PDF_FOLDER'] + workbook_name + '.xlsx'
        
        if platform.system() == 'Windows':
            file_path = basedir + '\\app\\static\\pdfs\\' + workbook_name + '.xlsx'

        print(file_path)

        workbook = Workbook(file_path)
        sheet = workbook.add_worksheet()
        for r, row in enumerate(results):
            for c, col in enumerate(row):
                sheet.write(r, c, row[col])
        workbook.close()

    connection.close()
    flash('Export to {}'.format(file_path),'success')
    return redirect(url_for('bp_iwms.reports'))
