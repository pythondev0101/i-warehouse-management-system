import platform
import pdfkit
from datetime import datetime
from sqlalchemy.ext.declarative.api import instrument_declarative
from flask import (
    render_template, request, redirect, flash, url_for, current_app, send_from_directory
    )
from flask_login import login_required, current_user
from flask_mail import Message
from app import db, CONTEXT, mail
from app import admin
from iwms.logging import create_log
from app.admin import admin_render_template
from app.admin.routes import admin_table, admin_edit
from app.auth.permissions import check_create
from iwms import bp_iwms
from iwms.models import PurchaseOrder, Warehouse, Supplier, StockItem, UnitOfMeasure,\
    PurchaseOrderProductLine
from iwms.forms import PurchaseOrderCreateForm, PurchaseOrderViewForm
from iwms.functions import generate_number



scripts = [
    {'bp_iwms.static': "js/purchase_order.js"}
]

modals = [
    "iwms/purchase_order/add_product_modal.html",
]


@bp_iwms.route('/purchase-orders')
@login_required
def purchase_orders():
    fields = [PurchaseOrder.id,PurchaseOrder.po_number,PurchaseOrder.created_at,PurchaseOrder.created_by,PurchaseOrder.status.name]
    return admin_table(PurchaseOrder,fields=fields,form=PurchaseOrderViewForm(), \
        create_modal=False, create_button=True, edit_url="bp_iwms.edit_purchase_order",\
            create_url="bp_iwms.create_purchase_order")

@bp_iwms.route('/purchase-orders/create',methods=['GET','POST'])
@login_required
def create_purchase_order():
    po_generated_number = ""
    po = db.session.query(PurchaseOrder).order_by(PurchaseOrder.id.desc()).first()

    if po:
        po_generated_number = generate_number("PO",po.id)
    else:
        po_generated_number = "PO00000001"
    
    form = PurchaseOrderCreateForm()

    if request.method == "GET":
        warehouses = Warehouse.query.all()
        suppliers = Supplier.query.all()

        data = {
            'warehouses': warehouses,
            'suppliers': suppliers,
            'po_generated_number': po_generated_number
        }

        CONTEXT['model'] = 'purchase_order'

        return admin_render_template('iwms/purchase_order/iwms_purchase_order_create.html', 'iwms', \
            form=form,title="Create purchase order", data=data, scripts=scripts,\
                modals=modals)
    
    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.purchase_orders'))

    try:
        r = request.form
        po = PurchaseOrder()
        po.po_number = po_generated_number
        po.supplier_id = form.supplier_id.data if form.supplier_id.data != '' else None
        po.warehouse_id = form.warehouse_id.data if form.warehouse_id.data != '' else None
        po.ship_to = form.ship_to.data
        po.address = form.address.data
        po.remarks = form.remarks.data
        po.ordered_date = form.ordered_date.data if not form.ordered_date.data == '' else None
        po.delivery_date = form.delivery_date.data if not form.delivery_date.data == '' else None
        po.approved_by = form.approved_by.data
        po.created_by = "{} {}".format(current_user.fname,current_user.lname)

        product_list = r.getlist('products[]')
        
        if product_list:
            for product_id in r.getlist('products[]'):
                product = StockItem.query.get(product_id)
                qty = r.get("qty_{}".format(product_id))
                cost = r.get("cost_{}".format(product_id))
                amount = r.get("amount_{}".format(product_id))
                uom = UnitOfMeasure.query.get(r.get("uom_{}".format(product_id)))
                line = PurchaseOrderProductLine(stock_item=product,qty=qty,unit_cost=cost,\
                    amount=amount,uom=uom,remaining_qty=qty)
                po.product_line.append(line)

        db.session.add(po)
        db.session.commit()
        create_log('New purchase order added','POID={}'.format(po.id))

        if request.form['btn_submit'] == 'Save and Print':
            file_name = po_generated_number + '.pdf'
            file_path = current_app.config['PDF_FOLDER'] + po_generated_number + '.pdf'
            
            """ CONVERT HTML STRING TO PDF THEN RETURN PDF TO BROWSER TO PRINT
            """
            if platform.system() == "Windows":
                path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe' # CHANGE THIS to the location of wkhtmltopdf
                config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
                pdfkit.from_string(_makePOPDF(po.supplier,po.product_line),file_path,configuration=config)
            else:
                pdfkit.from_string(_makePOPDF(po.supplier,po.product_line),file_path)

            """ SEND EMAIL TO SUPPLIER'S EMAIL ADDRESS AND ATTACHED THE SAVED PDF IN /STATIC/PDFS FOLDER
            """

            msg = Message('Purchase Order', sender = current_app.config['MAIL_USERNAME'], recipients = [po.supplier.email_address])
            msg.body = "Here attached purchase order quotation"

            with open(file_path,'rb') as pdf_file:
                msg.attach(filename=file_path,disposition="attachment",content_type="application/pdf",data=pdf_file.read())
            mail.send(msg)
            flash('New Purchase Order added Successfully!','success')
            return send_from_directory(directory=current_app.config['PDF_FOLDER'],filename=file_name,as_attachment=True)
        else:
            flash('New Purchase Order added Successfully!','success')
    except Exception as e:
        flash(str(e),'error')
    
    return redirect(url_for('bp_iwms.purchase_orders'))


@bp_iwms.route('/purchase-orders/<int:oid>/edit',methods=['GET','POST'])
@login_required
def edit_purchase_order(oid):
    ins = PurchaseOrder.query.get_or_404(oid)
    form = PurchaseOrderCreateForm(obj=ins)

    if request.method == "GET":
        warehouses = Warehouse.query.all()
        suppliers = Supplier.query.all()

        data = {
            'warehouses': warehouses,
            'suppliers': suppliers,
            'line_items': ins.product_line,
            'stock_items': '',
        }

        CONTEXT['model'] = 'purchase_order'

        return admin_render_template('iwms/purchase_order/iwms_purchase_order_edit.html', 'iwms',\
            oid=oid, form=form,title="Edit purchase order", data=data, scripts=scripts,\
                modals=modals)

    if not form.validate_on_submit():
        for key, value in form.errors.items():
            flash(str(key) + str(value), 'error')
        return redirect(url_for('bp_iwms.purchase_orders'))

    try:
        ins.supplier_id = form.supplier_id.data if not form.supplier_id.data == '' else None
        ins.warehouse_id = form.warehouse_id.data if not form.warehouse_id.data == '' else None
        ins.ship_to = form.ship_to.data
        ins.address = form.address.data
        ins.remarks = form.remarks.data
        ins.ordered_date = form.ordered_date.data if not form.ordered_date.data == '' else None
        ins.delivery_date = form.delivery_date.data if not form.delivery_date.data == '' else None
        ins.approved_by = form.approved_by.data
        ins.updated_by = "{} {}".format(current_user.fname,current_user.lname)

        product_list = request.form.getlist('products[]')
        ins.product_line = []
        
        if product_list:
            for product_id in product_list:
                product = StockItem.query.get(product_id)
                qty = request.form.get("qty_{}".format(product_id))
                cost = request.form.get("cost_{}".format(product_id))
                amount = request.form.get("amount_{}".format(product_id))
                uom = UnitOfMeasure.query.get(request.form.get("uom_{}".format(product_id)))
                line = PurchaseOrderProductLine(stock_item=product,qty=qty,unit_cost=cost,amount=amount,uom=uom,remaining_qty=qty)
                ins.product_line.append(line)

        db.session.commit()
        create_log('Purchase order update','POID={}'.format(ins.id))
        
        if request.form['btn_submit'] == 'Save and Print':
            file_name = ins.po_number + '.pdf'
            file_path = current_app.config['PDF_FOLDER'] + ins.po_number + '.pdf'
            """ CONVERT HTML STRING TO PDF THEN RETURN PDF TO BROWSER TO PRINT
            """
            if platform.system() == "Windows":
                path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe' # CHANGE THIS to the location of wkhtmltopdf
                config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
                pdfkit.from_string(_makePOPDF(ins.supplier,ins.product_line),file_path,configuration=config)
            else:
                pdfkit.from_string(_makePOPDF(ins.supplier,ins.product_line),file_path)
            
            """ SEND EMAIL TO SUPPLIER'S EMAIL ADDRESS AND ATTACHED THE SAVED PDF IN /STATIC/PDFS FOLDER
            """

            msg = Message('Purchase Order', sender = current_app.config['MAIL_USERNAME'], recipients = [ins.supplier.email_address])
            msg.body = "Here attached purchase order quotation"

            with open(file_path,'rb') as pdf_file:
                msg.attach(filename=file_path,disposition="attachment",content_type="application/pdf",data=pdf_file.read())
            mail.send(msg)
            flash('Purchase Order updated Successfully!','success')
            return send_from_directory(directory=current_app.config['PDF_FOLDER'],filename=file_name,as_attachment=True)

        flash('Purchase Order updated Successfully!','success')

    except Exception as exc:
        flash(str(exc),'error')
    
    return redirect(url_for('bp_iwms.purchase_orders'))            


@bp_iwms.route('/purchase_order_view/<int:oid>')
@login_required
def purchase_order_view(oid):
    """ First view function for viewing only and not editable html """
    po = PurchaseOrder.query.get_or_404(oid)
    f = PurchaseOrderCreateForm(obj=po)
    if request.method == "GET":
        warehouses = Warehouse.query.all()
        suppliers = Supplier.query.all()
        # stock_items = StockItem.query.all()
        # Hardcoded html ang irerender natin hindi yung builtin ng admin
        CONTEXT['active'] = 'purchases'
        CONTEXT['mm-active'] = 'purchase_order'
        CONTEXT['module'] = 'iwms'
        CONTEXT['model'] = 'purchase_order'

        return render_template('iwms/purchase_order/iwms_purchase_order_view.html', oid=oid,stock_items='',line_items=po.product_line, \
            context=CONTEXT,form=f,title="View purchase order",warehouses=warehouses,suppliers=suppliers)


def _makePOPDF(vendor,line_items):
    total = 0
    html = """<html><head><style>
    #invoice-POS{box-shadow: 0 0 1in -0.25in rgba(0, 0, 0, 0.5);padding:2mm;margin: 0 auto;width: 50%;background: #FFF;}
    ::selection {background: #f31544; color: #FFF;}
    ::moz-selection {background: #f31544; color: #FFF;}
    h1{font-size: 1.5em;color: #222;}
    h2{font-size: .9em;}
    h3{font-size: 1.2em;font-weight: 300;line-height: 2em;}
    p{font-size: .7em;color: #666;line-height: 1.2em;}
    #top, #mid,#bot{ /* Targets all id with 'col-' */border-bottom: 1px solid #EEE;}
    #mid{min-height: 80px;} 
    #bot{ min-height: 50px;}
    /*#top .logo{//float: left;height: 60px;width: 60px;background: url(http://michaeltruong.ca/images/logo1.png) no-repeat;background-size: 60px 60px;}*/
    /*.clientlogo{float: left;height: 60px;width: 60px;background: url(http://michaeltruong.ca/images/client.jpg) no-repeat;background-size: 60px 60px;border-radius: 50px;}*/
    .info{display: block;//float:left;margin-left: 0;}
    .title{float: right;}.title p{text-align: right;} 
    table{width: 100%;border-collapse: collapse;}
    td{//padding: 5px 0 5px 15px;//border: 1px solid #EEE}
    .tabletitle{//padding: 5px;font-size: .5em;background: #EEE;}
    .service{border-bottom: 1px solid #EEE;}
    .item{width: 24mm;}
    .itemtext{font-size: .5em;}
    #legalcopy{margin-top: 5mm;}
    </style>
    </head>
    <body><div id="invoice-POS">
    <center id="top"><div class="info">
    <h2>Purchase Order</h2></div><!--End Info-->
    </center><!--End InvoiceTop-->
    
    <div id="mid">
      <div class="info">
        <h2>Vendor</h2>"""
    html = html + """<p> 
            Company Name : {name}</br>
            Address : {add}</br>
            Email   : {email}</br>
            Phone   : {phone}</br>
        </p>""".format(name=vendor.name,add=vendor.address,email=vendor.email_address,phone=vendor.contact_number)
    
    html = html + """</div>
    </div><!--End Invoice Mid-->
    <div id="bot">
    <div id="table">
    <table>
    <tr class="tabletitle">
    <td class="item"><h2>Item</h2></td>
    <td class="item"><h2>Description</h2></td>
    <td class="Hours"><h2>Qty</h2></td>
    <td class="Hours"><h2>Unit Price</h2></td>
    <td class="Rate"><h2>Total</h2></td></tr>
    """

    for line in line_items:
        html = html + """
            <tr class='service'><td class='tableitem'><p class='itemtext'>{no}</p></td>
            <td class="tableitem"><p class="itemtext">{desc}</p></td>
            <td class="tableitem"><p class="itemtext">{qty}</p></td>
            <td class="tableitem"><p class="itemtext">{price}</p></td>
            <td class="tableitem"><p class="itemtext">{amount}</p></td>
            </tr>""".format(no=line.stock_item.number,desc=line.stock_item.description,\
                qty=line.qty,price=line.unit_cost,amount=line.amount)
        total = total + line.amount

    html = html + """
    <tr class="tabletitle">
    <td></td><td></td><td></td>
    <td class="Rate"><h2>Total</h2></td>
    <td class="payment"><h2>{total}</h2></td>
    </tr>
    </table>
    </div><!--End Table-->
    <div id="legalcopy">
    <p class="legal" style="text-align: center;">
    If you have any question about this purchase order,please contact
	</p>
    </div>
    </div><!--End InvoiceBot-->
    </div><!--End Invoice-->
    </body></html>
    """.format(total=total)
    return html