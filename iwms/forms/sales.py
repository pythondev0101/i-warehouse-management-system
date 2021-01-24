from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,IntegerField, DecimalField, SelectField,DateTimeField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.admin.forms import AdminIndexForm,AdminEditForm, AdminInlineForm, AdminField
from datetime import datetime


class ShipViaForm(AdminIndexForm):
    index_headers = ['description','created by','created at','updated by', 'updated at']
    index_title = 'Ship Via'
    
    description = AdminField(label='Description',validators=[DataRequired()])

    def create_fields(self):
        return [[self.description]]


class ShipViaEditForm(AdminEditForm):
    description = AdminField(label='Description',validators=[DataRequired()])
    edit_title = 'Edit sales via'

    def edit_fields(self):
        return [[self.description]]


class ClientForm(AdminIndexForm):
    from iwms.models import Term,ShipVia

    index_headers = ['code','name','created by','created at','updated by','updated at']
    index_title = 'Clients'
    
    name = AdminField(label='Name',required=False)
    code = AdminField(label='Code',validators=[DataRequired()],readonly=True)
    # status = AdminField(label='Status',required=False,input_tye="checkbox")
    term_id = AdminField(label='Term',model=Term,required=False)
    ship_via_id = AdminField(label='Ship Via',model=ShipVia,required=False)

    def create_fields(self):
        return [[self.code,self.name],[self.term_id,self.ship_via_id]]


class ClientEditForm(AdminEditForm):
    from iwms.models import Term, ShipVia
    
    edit_title = 'Edit client'
    name = AdminField(label='Name',required=False)
    code = AdminField(label='Code',validators=[DataRequired()],readonly=True)
    term_id = AdminField(label='Term',model=Term,required=False)
    ship_via_id = AdminField(label='Ship Via',model=ShipVia,required=False)    
    # status = AdminField(label='Status',required=False,input_type="checkbox")
    def edit_fields(self):
        return [[self.code,self.name],[self.term_id,self.ship_via_id]]


class TermForm(AdminIndexForm):
    index_headers = ['code','description','days','created by','created at','updated by', 'updated at']
    index_title = 'Terms'
    
    code = AdminField(label='Code',validators=[DataRequired()])
    description = AdminField(label='Description',required=False)
    days = AdminField(label='Days',required=False,input_type="number")

    def create_fields(self):
        return [[self.code,self.description],[self.days]]


class TermEditForm(AdminEditForm):
    code = AdminField(label='Code',validators=[DataRequired()])
    description = AdminField(label='Description',required=False)
    days = AdminField(label='Days',required=False,input_type="number")
    edit_title = 'Edit term'
    def edit_fields(self):
        return [[self.code,self.description],[self.days]]


class ClientGroupForm(AdminIndexForm):
    index_headers = ['Name','updated by','update at']
    index_title = 'Client Group'
    
    name = AdminField(label='Name',validators=[DataRequired()])

    def create_fields(self):
        return [[self.name]]


class ClienGroupEditForm(AdminEditForm):
    edit_title = 'edit client group'
    
    name = AdminField(label='Name',validators=[DataRequired()])

    def edit_fields(self):
        return [[self.name]]


class SalesOrderViewForm(AdminIndexForm):
    index_headers = ['SO no.','date created','created by','status']
    index_title = 'Sales Order'
    number = AdminField(label='SO No.')
    status = AdminField(label="Status")

    def create_fields(self):
        return [[self.number,self.status]]


class SalesOrderCreateForm(FlaskForm):
    number = StringField()
    status = StringField()
    client_name = StringField()
    ship_to = StringField()
    end_user = StringField()
    tax_info = StringField()
    reference = StringField()
    sales_representative = StringField()
    inco_terms = StringField()
    destination_port = StringField()
    term_id = StringField()
    ship_via_id = StringField()
    order_date = StringField(default=datetime.today)
    delivery_date = StringField()
    remarks = StringField()
    approved_by = StringField()

        
