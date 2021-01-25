from datetime import datetime
from re import S
from flask_login import login_required
from app import db
from app.admin.routes import admin_table
from app.auth.models import User
from app.admin import bp_admin
from iwms.models import SystemLog



@bp_admin.route('/system-logs')
@login_required
def system_logs():
    fields = [SystemLog.id,User.fname,SystemLog.date,SystemLog.description,SystemLog.data]
    models = [SystemLog,User]
    
    index_headers = ['User','Date','Description','Data']

    return admin_table(*models,fields=fields,action="iwms/iwms_system_actions.html",\
        create_modal=False,view_modal=False,kwargs={'index_title':'System Logs and backup',\
            'index_headers': index_headers,'index_message':'List of items'
            })