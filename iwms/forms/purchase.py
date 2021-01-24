from wtforms import StringField, SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from app.admin.forms import AdminIndexForm,AdminEditForm, AdminField



class PurchaseOrderCreateForm(FlaskForm):
    po_number = StringField()
    status = StringField()
    supplier_id = StringField()
    ship_to = SelectField('Ship To',choices=[
        ('warehouse','Warehouse')])
    warehouse_id = StringField()
    address = StringField()
    ordered_date = StringField()
    delivery_date = StringField()
    approved_by = StringField()
    remarks = StringField()


class PurchaseOrderViewForm(AdminIndexForm):
    from iwms.models import Supplier, Warehouse

    index_headers = ['Po no.','date created','created by','status']
    index_title = 'Purchase Orders'
    po_number = AdminField(label='PO No.')
    status = AdminField(label="Status")
    supplier_id = AdminField(label="Supplier",model=Supplier)
    warehouse_id = AdminField(label='Warehouse',model=Warehouse)
    ordered_date = AdminField(label='Ordered',input_type='date')
    delivery_date = AdminField(label='Delivery',input_type='date')

    def create_fields(self):
        return [
            [self.po_number,self.status],[self.supplier_id,self.warehouse_id],
            [self.ordered_date,self.delivery_date]
            ]


class SupplierForm(AdminIndexForm):
    index_headers = ['code','name','created by','created at','updated by','updated at']
    index_title = 'Suppliers'
    
    code = AdminField(label='Code',validators=[DataRequired()],readonly=True)
    name = AdminField(label='Name',validators=[DataRequired()])
    address = AdminField(label='Address',required=False)
    email_address = AdminField(label='Email Address',required=False,input_type='email')
    contact_number = AdminField(label='Contact Number',required=False)
    contact_person = AdminField(label='Contact Person',required=False)
    
    def create_fields(self):
        return [[self.code,self.name],[self.address,self.email_address],[self.contact_number,self.contact_person]]


class SupplierEditForm(AdminEditForm):
    code = AdminField(label='Code',validators=[DataRequired()],readonly=True)
    name = AdminField(label='Name',validators=[DataRequired()])
    address = AdminField(label='Address',required=False)
    email_address = AdminField(label='Email Address',required=False,input_type='email')
    contact_number = AdminField(label='Contact Number',required=False)
    contact_person = AdminField(label='Contact Person',required=False)

    def edit_fields(self):
        return [[self.code,self.name],[self.address,self.email_address],[self.contact_number,self.contact_person]]
   
    edit_title = 'Edit supplier'
