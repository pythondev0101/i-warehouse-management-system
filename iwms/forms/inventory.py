from datetime import datetime
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from app.admin.forms import AdminIndexForm,AdminEditForm, AdminField



class BinLocationForm(AdminIndexForm):
    from iwms.models import Warehouse,Zone

    index_headers = [
        'Code','Description','Warehouse',
        'Zone'
        ]
    index_title = 'Bin Locations'

    code = AdminField(label='Code',validators=[DataRequired()])
    description = AdminField(label='Description',validators=[DataRequired()])
    index = AdminField(label='Index',required=False,input_type='number')
    warehouse_id = AdminField(label='Warehouse',required=False,model=Warehouse)
    zone_id = AdminField(label='Zone',required=False,model=Zone)
    pallet_slot = AdminField(label='Pallet Slot',required=False,input_type='number')
    pallet_cs = AdminField(label='Pallet CS',required=False,input_type='number')
    capacity = AdminField(label='Capacity',required=False,input_type='number')
    weight_cap = AdminField(label='Weight Cap',required=False,input_type='number')
    cbm_cap = AdminField(label='CBM Cap',required=False,input_type='number')

    def create_fields(self):
        return [
            [self.code,self.description],
            [self.warehouse_id,self.zone_id],
            ]


class BinLocationEditForm(AdminEditForm):
    from iwms.models import Warehouse,Zone

    code = AdminField(label='Code',validators=[DataRequired()])
    description = AdminField(label='Description',validators=[DataRequired()])
    index = AdminField(label='Index',required=False)
    warehouse_id = AdminField(label='Warehouse',required=False,model=Warehouse)
    zone_id = AdminField(label='Zone',required=False,model=Zone)
    pallet_slot = AdminField(label='Pallet Slot',required=False)
    pallet_cs = AdminField(label='Pallet CS',required=False)
    capacity = AdminField(label='Capacity',required=False)
    weight_cap = AdminField(label='Weight Cap',required=False)
    cbm_cap = AdminField(label='CBM Cap',required=False)

    def edit_fields(self):
        return [
            [self.code,self.description],
            [self.warehouse_id,self.zone_id],
            ]
    edit_title = 'Edit Bin Location'


class CategoryForm(AdminIndexForm):
    index_headers = ['code','description','created by','created at','updated by','updated at']
    index_title = 'Categories'
    
    code = AdminField(label='Code',validators=[DataRequired()])
    description = AdminField(label='Description',validators=[DataRequired()])

    def create_fields(self):
        return [[self.code,self.description]]


class CategoryEditForm(AdminEditForm):
    code = AdminField(label='Code',validators=[DataRequired()])
    description = AdminField(label='Description',validators=[DataRequired()])
    
    def edit_fields(self):
        return [
            [self.code,self.description]
        ]

    edit_title = 'Edit category'


class InventoryItemForm(AdminIndexForm):
    from iwms.models import StockItemType, Category
    index_headers = ['name','Cost','Price','Product type','Product Category','Quantity on hand']
    index_title = 'Inventory Items'

    number = AdminField(label='Item No.')
    name = AdminField(label='Item Name')
    cost = AdminField(label='Default Cost')
    price = AdminField(label='Default Price')
    stock_item_type_id = AdminField(label='Product Type',model=StockItemType)
    category_id = AdminField(label='Category',model=Category)


    def create_fields(self):
        return [
            [self.number,self.name],
            [self.price,self.cost],
            [self.stock_item_type_id,self.category_id]
            ]


class InventoryItemEditForm(FlaskForm):
    number = AdminField(label='number')
    status = AdminField(label='status',required=False)
    stock_item_type_id = AdminField(label='stock_item_type_id',required=False)
    category_id = AdminField(label='category_id',required=False)
    has_serial = AdminField(label='has_serial',required=False)
    monitor_expiration = AdminField(label='monitor_expiration',required=False)
    brand = AdminField(label='brand',required=False)
    name = AdminField(label='name',required=False)
    description = AdminField(label='description',required=False)
    packaging = AdminField(label='packaging',required=False)
    tax_code_id = AdminField(label='tax_code_id',required=False)
    reorder_qty = AdminField(label='reorder_qty',required=False)
    description_plu = AdminField(label='description_plu',required=False)
    barcode = AdminField(label='barcode',required=False)
    qty_plu = AdminField(label='qty_plu',required=False)
    length = AdminField(label='length',required=False)
    width = AdminField(label='width',required=False)
    height = AdminField(label='height',required=False)
    unit_id = AdminField(label='unit_id',required=False)
    default_cost = AdminField(label='default_cost',required=False)
    default_price = AdminField(label='default_price',required=False)
    weight = AdminField(label='weight',required=False)
    cbm = AdminField(label='cbm',required=False)
    qty_per_pallet = AdminField(label='qty_per_pallet',required=False)
    shelf_life = AdminField(label='shelf_life',required=False)
    qa_lead_time = AdminField(label='qa_lead_time',required=False)


class PickingIndexForm(AdminIndexForm):
    index_headers = ['PCK No.','created by','date created','status']
    index_title = 'Pickings'
    number = AdminField(label='PCK No.')
    status = AdminField(label="Status")

    def create_fields(self):
        return [[self.number,self.status]]


class PickingCreateForm(FlaskForm):
    so_number = StringField()
    remarks = StringField()


class PutawayCreateForm(FlaskForm):
    pwy_number = StringField()
    sr_number = StringField()
    status = StringField()
    receipt_no = StringField()
    reference = StringField()
    remarks = StringField()


class PutawayViewForm(AdminIndexForm):
    index_headers = ['PWY no.','date created','created by','status']
    index_title = 'Putaways'
    pwy_number = AdminField(label='PWY No.')
    status = AdminField(label="Status")

    def create_fields(self):
        return [[self.pwy_number,self.status]]


class StockReceiptCreateForm(FlaskForm):
    status = StringField('Status')
    warehouse_id = AdminField(label='warehouse',required=False)
    source = AdminField(label='Source',required=False)
    po_number = StringField('PO No.')
    supplier = StringField('Supplier')
    reference = StringField('Reference')
    si_number = StringField('SI Number')
    bol = StringField('BOL')
    remarks = StringField('Remarks')
    date_received = StringField(default=datetime.today)
    putaway_txn = StringField('Putaway Txn')


class StockReceiptViewForm(AdminIndexForm):
    index_headers = ['SR no.','date created','created by','status']
    index_title = 'Stock Receipts'
    sr_number = AdminField(label='SR No.')
    status = AdminField(label="Status")

    def create_fields(self):
        return [[self.sr_number,self.status]]


class StockTransferForm(AdminIndexForm):
    from iwms.models import StockItemType, Category
    index_headers = ['name','Cost','Price','Product type','Product Category','Quantity on hand']
    index_title = 'Stock Transfers'

    number = AdminField(label='Item No.')
    name = AdminField(label='Item Name')
    cost = AdminField(label='Default Cost')
    price = AdminField(label='Default Price')
    stock_item_type_id = AdminField(label='Product Type',model=StockItemType)
    category_id = AdminField(label='Category',model=Category)


    def create_fields(self):
        return [
            [self.number,self.name],
            [self.price,self.cost],
            [self.stock_item_type_id,self.category_id]
            ]


class SourceForm(AdminIndexForm):
    index_headers = ['name','description','created by','created at','updated by','updated at']
    index_title = 'Sources'
    
    name = AdminField(label='Name',validators=[DataRequired()])
    description = AdminField(label='Description',required=False)

    def create_fields(self):
        return [[self.name,self.description]]


class SourceEditForm(AdminEditForm):
    name = AdminField(label='Name',validators=[DataRequired()])
    description = AdminField(label='Description',required=False)

    def edit_fields(self):
        return [
            [self.name,self.description]
        ]    
    edit_title = 'Edit source'


    edit_title = 'Edit unit of measure'


class StockItemView(AdminIndexForm):
    index_headers = ['SI No.','Name','Description','created by','created at','updated by','updated at']
    index_title = 'Stock Items'
    number = AdminField(label='SI No.')
    name = AdminField(label='Name',required=False)
    description = AdminField(label='Description',required=False)
    
    def create_fields(self):
        return [[self.number],[self.name,self.description]]


class StockItemCreateForm(FlaskForm):
    number = AdminField(label='number')
    status = AdminField(label='status',required=False)
    stock_item_type_id = AdminField(label='stock_item_type_id',required=False)
    category_id = AdminField(label='category_id',required=False)
    has_serial = AdminField(label='has_serial',required=False)
    monitor_expiration = AdminField(label='monitor_expiration',required=False)
    brand = AdminField(label='brand',required=False)
    name = AdminField(label='name',required=False)
    description = AdminField(label='description',required=False)
    packaging = AdminField(label='packaging',required=False)
    tax_code_id = AdminField(label='tax_code_id',required=False)
    reorder_qty = AdminField(label='reorder_qty',required=False)
    description_plu = AdminField(label='description_plu',required=False)
    barcode = AdminField(label='barcode',required=False)
    qty_plu = AdminField(label='qty_plu',required=False)
    length = AdminField(label='length',required=False)
    width = AdminField(label='width',required=False)
    height = AdminField(label='height',required=False)
    unit_id = AdminField(label='unit_id',required=False)
    default_cost = AdminField(label='default_cost',required=False)
    default_price = AdminField(label='default_price',required=False)
    weight = AdminField(label='weight',required=False)
    cbm = AdminField(label='cbm',required=False)
    qty_per_pallet = AdminField(label='qty_per_pallet',required=False)
    shelf_life = AdminField(label='shelf_life',required=False)
    qa_lead_time = AdminField(label='qa_lead_time',required=False)


class TypeForm(AdminIndexForm):
    index_headers = ['name','created by','created at','updated by','updated at']
    index_title = 'Types'
    
    name = AdminField(label='Name',validators=[DataRequired()])

    def create_fields(self):
        return [[self.name]]


class TypeEditForm(AdminEditForm):
    name = AdminField(label='Name',validators=[DataRequired()])
    def edit_fields(self):
        return [[self.name]]
   
    edit_title = 'Edit type'


class UnitOfMeasureForm(AdminIndexForm):
    index_headers = ['code','description','active','created by','created at ','updated by','updated at']
    index_title = 'Unit of Measurements'
    
    code = AdminField(label='Code',validators=[DataRequired()])
    description = AdminField(label='Description',validators=[DataRequired()])
    active = AdminField(label='Active',required=False,input_type='checkbox')

    def create_fields(self):
        return [[self.code,self.description],[self.active]]


class UnitOfMeasureEditForm(AdminEditForm):
    code = AdminField(label='Code',validators=[DataRequired()])
    description = AdminField(label='Description',validators=[DataRequired()])
    active = AdminField(label='Active',required=False,input_type='checkbox')

    def edit_fields(self):
        return [
            [self.code,self.description],[self.active]
        ]


class WarehouseForm(AdminIndexForm):
    index_headers = ['Code','Name','created by','created at','updated by','updated at']
    index_title = 'Warehouses'

    code = AdminField(label='Code',validators=[DataRequired()])
    name = AdminField(label='Name',validators=[DataRequired()])
    # active = AdminField(label='Active Flag',required=False,input_type='checkbox')
    # main_warehouse = AdminField(label="Main Warehouse",required=False,input_type='checkbox')
    
    def create_fields(self):
        return [[self.code,self.name]]
    

class WarehouseEditForm(AdminEditForm):
    code = AdminField(label='Code',validators=[DataRequired()])
    name = AdminField(label='Name',validators=[DataRequired()])
    # active = AdminField(label='Active Flag',required=False,input_type='checkbox')
    # main_warehouse = AdminField(label="Main Warehouse",required=False,input_type='checkbox')
    
    def edit_fields(self):
        return [
            [self.code,self.name]
        ]
    edit_title = 'Edit warehouse'


class ZoneForm(AdminIndexForm):
    index_headers = ['Code','Description','created by','created by','updated by','updated at']
    index_title = 'Zones'

    code = AdminField(label='Code',validators=[DataRequired()])
    description = AdminField(label='Description',validators=[DataRequired()])

    def create_fields(self):
        return [[self.code,self.description]]


class ZoneEditForm(AdminEditForm):
    code = AdminField(label='Code',validators=[DataRequired()])
    description = AdminField(label='Description',validators=[DataRequired()])

    def edit_fields(self):
        return [[
            self.code,self.description
        ]]    
    edit_title = 'Edit zone'