from flask import (
    render_template, request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from app.admin.routes import admin_table, admin_edit
from iwms import bp_iwms

@bp_iwms.route('/sales_orders')
@login_required
def sales_orders():
    fields = [SalesOrder.id,SalesOrder.number,SalesOrder.created_at,SalesOrder.created_by,SalesOrder.status]
    CONTEXT['mm-active'] = 'sales_order'
    CONTEXT['create_modal']['create_url'] = False
    return admin_table(SalesOrder,fields=fields,form=SalesOrderViewForm(),create_modal=True,\
        template="iwms/iwms_index.html",kwargs={'active':'sales'},edit_url="bp_iwms.sales_order_edit")


@bp_iwms.route('/sales_order_create',methods=['GET','POST'])
@login_required
def sales_order_create():
    so_generated_number = ""
    so = db.session.query(SalesOrder).order_by(SalesOrder.id.desc()).first()
    if so:
        so_generated_number = _generate_number("SO",so.id)
    else:
        # MAY issue to kasi kapag hindi na truncate yung table magkaiba na yung id at number ng po
        # Make sure nakatruncate ang mga table ng po para reset yung auto increment na id
        so_generated_number = "SO00000001"

    f = SalesOrderCreateForm()
    if request.method == "GET":
        # Hardcoded html ang irerender natin hindi yung builtin ng admin
        clients = Client.query.all()
        terms = Term.query.all()
        ship_vias = ShipVia.query.all()
        items = ItemBinLocations.query.filter(ItemBinLocations.qty_on_hand>0).all()

        CONTEXT['active'] = 'sales'
        CONTEXT['mm-active'] = 'sales_order'
        CONTEXT['module'] = 'iwms'
        CONTEXT['model'] = 'sales_order'
        return render_template('iwms/sales_order/iwms_sales_order_create.html',context=CONTEXT,form=f,title="Create sales order"\
            ,so_generated_number=so_generated_number,clients=clients,terms=terms,ship_vias=ship_vias,inventory_items=items)
    elif request.method == "POST":
        if f.validate_on_submit():
            try:
                if f.client_name.data == '':
                    raise Exception('No Customer included')
                r = request.form
                so = SalesOrder()
                so.number = so_generated_number
                client = Client.query.filter_by(name=f.client_name.data).first()
                so.client = client
                so.ship_to = f.ship_to.data
                so.end_user = f.end_user.data
                so.tax_info = f.tax_info.data
                so.reference = f.reference.data
                so.sales_representative = f.sales_representative.data
                so.inco_terms = f.inco_terms.data
                so.destination_port = f.destination_port.data
                so.term_id = None
                so.ship_via_id = None
                so.order_date = f.order_date.data if not f.order_date.data == '' else None
                so.delivery_date = f.delivery_date.data if not f.delivery_date.data == '' else None
                so.remarks = f.remarks.data
                so.approved_by = f.approved_by.data
                so.created_by = "{} {}".format(current_user.fname,current_user.lname)
                
                _total_price = 0
                product_list = r.getlist('products[]')
                if product_list:
                    for product_id in product_list:
                        item_bin_location= ItemBinLocations.query.get_or_404(product_id)
                        product = InventoryItem.query.get_or_404(item_bin_location.inventory_item.id)
                        qty = r.get("qty_{}".format(product_id))
                        unit_price = r.get("price_{}".format(product_id))
                        uom = UnitOfMeasure.query.get(r.get("uom_{}".format(product_id)))
                        line = SalesOrderLine(inventory_item=product,item_bin_location=item_bin_location,\
                            qty=qty,uom=uom,unit_price=unit_price,issued_qty=0)
                        _subtotal = int(qty) * float(line.unit_price)
                        _total_price += _subtotal
                        so.product_line.append(line)

                so.total_price = _total_price

                db.session.add(so)
                db.session.commit()
                _log_create('New sales order added','SOID={}'.format(so.id))
                flash('New Sales Order added Successfully!','success')
                return redirect(url_for('bp_iwms.sales_orders'))
            except Exception as e:
                flash(str(e),'error')
                return redirect(url_for('bp_iwms.sales_orders'))
        else:
            for key, value in f.errors.items():
                flash(str(key) + str(value), 'error')
            return redirect(url_for('bp_iwms.sales_orders'))


@bp_iwms.route('/sales_order_edit/<int:oid>',methods=['GET','POST'])
@login_required
def sales_order_edit(oid):
    so = SalesOrder.query.get_or_404(oid)
    f = SalesOrderCreateForm(obj=so)
    if request.method == "GET":
        clients = Client.query.all()
        _so_items = [x.item_bin_location_id for x in so.product_line]
        items = ItemBinLocations.query.filter(ItemBinLocations.qty_on_hand>0, ~ItemBinLocations.id.in_(_so_items)).all()
        f.client_name.data = so.client.name if not so.client == None else ''
        if so.client is None:
            f.term_id.data = ''
            f.ship_via_id.data = ''
        else:
            f.term_id.data = so.client.term.description if not so.client.term == None else ''
            f.ship_via_id.data = so.client.ship_via.description if not so.client.ship_via == None else ''
        CONTEXT['active'] = 'sales'
        CONTEXT['mm-active'] = 'sales_order'
        CONTEXT['module'] = 'iwms'
        CONTEXT['model'] = 'sales_order'

        return render_template('iwms/sales_order/iwms_sales_order_edit.html', oid=oid,\
            context=CONTEXT,form=f,title="Edit sales order",clients=clients,inventory_items=items,line_items=so.product_line)
    
    elif request.method == "POST":
        if f.validate_on_submit():
            try:
                if f.client_name.data == '':
                    raise Exception('No Customer included')

                r = request.form
                client = Client.query.filter_by(name=f.client_name.data).first()
                so.client = client
                so.ship_to = f.ship_to.data
                so.end_user = f.end_user.data
                so.tax_info = f.tax_info.data
                so.reference = f.reference.data
                so.sales_representative = f.sales_representative.data
                so.inco_terms = f.inco_terms.data
                so.destination_port = f.destination_port.data
                so.term_id = None
                so.ship_via_id = None
                so.order_date = f.order_date.data if not f.order_date.data == '' else None
                so.delivery_date = f.delivery_date.data if not f.delivery_date.data == '' else None
                so.remarks = f.remarks.data
                so.approved_by = f.approved_by.data
                so.updated_by = "{} {}".format(current_user.fname,current_user.lname)

                _total_price = 0
                product_list = r.getlist('products[]')
                if product_list:
                    so.product_line = []
                    for product_id in product_list:
                        item_bin_location= ItemBinLocations.query.get_or_404(product_id)
                        product = InventoryItem.query.get_or_404(item_bin_location.inventory_item.id)
                        qty = r.get("qty_{}".format(product_id))
                        unit_price = r.get("price_{}".format(product_id))
                        uom = UnitOfMeasure.query.get(r.get("uom_{}".format(product_id)))
                        line = SalesOrderLine(inventory_item=product,item_bin_location=item_bin_location,\
                            qty=qty,uom=uom,unit_price=unit_price,issued_qty=0)

                        _total_price = _total_price + float(line.unit_price)
                        so.product_line.append(line)

                so.total_price = _total_price

                db.session.commit()
                _log_create('Sales order update','SOID={}'.format(so.id))
                flash('Sales Order updated Successfully!','success')
                return redirect(url_for('bp_iwms.sales_orders'))
            except Exception as e:
                flash(str(e),'error')
                return redirect(url_for('bp_iwms.sales_orders'))
        else:
            for key, value in f.errors.items():
                flash(str(key) + str(value), 'error')
            return redirect(url_for('bp_iwms.sales_orders'))



@bp_iwms.route('/sales_order_view/<int:oid>')
@login_required
def sales_order_view(oid):
    """ First view function for viewing only and not editable html """
    so = SalesOrder.query.get_or_404(oid)
    f = SalesOrderCreateForm(obj=so)
    if request.method == "GET":
        clients = Client.query.all()
        _so_items = [x.item_bin_location_id for x in so.product_line]
        items = ItemBinLocations.query.filter(ItemBinLocations.qty_on_hand>0, ~ItemBinLocations.id.in_(_so_items)).all()
        f.client_name.data = so.client.name if not so.client == None else ''
        if so.client is None:
            f.term_id.data = ''
            f.ship_via_id.data = ''
        else:
            f.term_id.data = so.client.term.description if not so.client.term == None else ''
            f.ship_via_id.data = so.client.ship_via.description if not so.client.ship_via == None else ''
        CONTEXT['active'] = 'sales'
        CONTEXT['mm-active'] = 'sales_order'
        CONTEXT['module'] = 'iwms'
        CONTEXT['model'] = 'sales_order'

        return render_template('iwms/sales_order/iwms_sales_order_view.html', oid=oid,\
            context=CONTEXT,form=f,title="View sales order",clients=clients,inventory_items=items,line_items=so.product_line)
    
