from datetime import datetime
from flask_login import current_user
from app import db
from iwms.models import SystemLog



def create_log(description, data):
    log = SystemLog()
    log.user_id = current_user.id
    log.date = datetime.utcnow()
    log.description = description
    log.data = data

    db.session.add(log)
    db.session.commit()
    
    print("Log created!")