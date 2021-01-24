from flask import Blueprint

bp_iwms = Blueprint(
    'bp_iwms', __name__,template_folder='templates', static_folder='static', 
    static_url_path='/static'
    )


from . import views
from . import routes
from . import models
from . import functions
from . import cli
from . import api