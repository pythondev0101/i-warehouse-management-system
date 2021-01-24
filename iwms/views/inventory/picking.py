from flask import (
    render_template, request, redirect, flash, url_for
    )
from flask_login import login_required, current_user
from app.admin.routes import admin_table, admin_edit
from iwms import bp_iwms


@bp_iwms.route('/pickings')
@login_required
def pickings():
    fields = [Picking.id,Picking.number,Picking.created_by,Picking.created_at,Picking.status]
    CONTEXT['mm-active'] = 'picking'
    CONTEXT['create_modal']['create_url'] = False
    return admin_table(Picking,fields=fields,form=PickingIndexForm(),\
        create_modal=True,template="iwms/iwms_index.html",kwargs={'active':'inventory'})


@bp_iwms.route('/picking_create',methods=['GET','POST'])
@login_required
def picking_create():
    pck_generated_number = ""
    pck = db.session.query(Picking).order_by(Picking.id.desc()).first()
    if pck:
        pck_generated_number = _generate_number("PCK",pck.id)
    else:
        # MAY issue to kasi kapag hindi na truncate yung table magkaiba na yung id at number ng po
        # Make sure nakatruncate ang mga table ng po para reset yung auto increment na id
        pck_generated_number = "PCK00000001"

    f = PickingCreateForm()
    if request.method == "GET":
        # Hardcoded html ang irerender natin hindi yung builtin ng admin
        warehouses = Warehouse.query.all()
        sales_orders = SalesOrder.query.filter(SalesOrder.status.in_(['ON HOLD','LOGGED']))
        CONTEXT['active'] = 'inventory'
        CONTEXT['mm-active'] = 'picking'
        CONTEXT['module'] = 'iwms'
        CONTEXT['model'] = 'picking'
        
        return render_template('iwms/picking/iwms_picking_create.html',context=CONTEXT,form=f,title="Create picking"\
            ,pck_generated_number=pck_generated_number,warehouses=warehouses,sales_orders=sales_orders)
    elif request.method == "POST":
        if f.validate_on_submit():
            try:
                obj = Picking()
                so = SalesOrder.query.filter_by(number=f.so_number.data).first()
                obj.sales_order = so
                obj.number = pck_generated_number
                obj.status = "LOGGED"
                obj.remarks = f.remarks.data
                obj.created_by = "{} {}".format(current_user.fname,current_user.lname)
                
                _remaining = 0
                items_list = request.form.getlist('pick_items[]')
                if items_list:
                    for item_id in items_list:
                        bin_item = ItemBinLocations.query.get_or_404(item_id)
                        lot_no = request.form.get('lot_no_{}'.format(item_id))
                        expiry_date = request.form.get('expiry_{}'.format(item_id)) if not request.form.get('expiry_{}'.format(item_id)) == '' else None
                        uom = request.form.get('uom_{}'.format(item_id))
                        qty = request.form.get('qty_{}'.format(item_id)) if not request.form.get('qty_{}'.format(item_id)) == '' else None
                        line = PickingItemLine(item_bin_location=bin_item,lot_no=lot_no,expiry_date=expiry_date,uom=uom,qty=qty)
                        obj.item_line.append(line)

                        """ DEDUCTING QUANTITY TO THE PICKED ITEMS """

                        bin_item.qty_on_hand = bin_item.qty_on_hand - int(qty)
                      
                        for pi in so.product_line:

                            if int(item_id) == pi.item_bin_location_id:
                                pi.issued_qty = pi.issued_qty + int(qty)
                                pi.qty = pi.qty - int(qty)
                                db.session.commit()

                for pi in so.product_line:
                    _remaining = _remaining + pi.qty               

                if _remaining == 0:
                    so.status = "CONFIRMED"
                else:
                    so.status = "ON HOLD"

                db.session.add(obj)
                db.session.commit()
                _log_create('New picking added','PCKID={}'.format(obj.id))
                flash('New Picking added Successfully!','success')
                return redirect(url_for('bp_iwms.pickings'))
            except Exception as e:
                flash(str(e),'error')
                return redirect(url_for('bp_iwms.pickings'))
        else:
            for key, value in f.errors.items():
                flash(str(key) + str(value), 'error')
            return redirect(url_for('bp_iwms.pickings'))
