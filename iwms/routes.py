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
from .models import (Email as EAddress, ClientGroup, ItemBinLocations
    )
from .forms import *



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
