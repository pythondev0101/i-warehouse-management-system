from flask import redirect, current_app
from flask_login import login_required
from iwms import bp_iwms


@bp_iwms.route('/cold-storage')
@login_required
def cold_storage():
    url = current_app.config['COLD_STORAGE_URL']
    return redirect(url, 302)
