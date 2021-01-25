from re import T
from app.core import CoreModule
from app.admin.models import Admin
from .models import (
    Warehouse, Zone, BinLocation, Category, UnitOfMeasure, StockItem, StockItemType, StockReceipt,
    Putaway, PurchaseOrder, Term, Supplier, Source, ShipVia, Client, InventoryItem, SalesOrder,
    Picking, StockTransfer, WarehouseBinLocation, ColdStorage
)



class IwmsModule(CoreModule):
    module_name = 'iwms'
    module_icon = 'fa-cubes'
    module_link = 'bp_iwms.warehouse_bin_location'
    module_short_description = 'Warehouse Management'
    module_long_description = "Warehouse Management system"
    models = [
        Warehouse,Zone,BinLocation,Category,UnitOfMeasure,StockItem,StockItemType,StockReceipt,
        Putaway,PurchaseOrder, Term,Supplier,Source,ShipVia,Client,InventoryItem,SalesOrder, 
        Picking,StockTransfer, WarehouseBinLocation, ColdStorage
        ]
    version = '1.0'

    sidebar = {
        'Warehouse Bin Location': [
            WarehouseBinLocation, ColdStorage
        ],
        'Inventory':[
            Warehouse, Zone, BinLocation, Category, StockItem, StockItemType, 
            UnitOfMeasure, Source, StockReceipt, Putaway, InventoryItem, Picking, StockTransfer,
        ],
        'Sales':[
            ShipVia, Client, Term, SalesOrder
        ],
        'Purchase':[
            Supplier, PurchaseOrder
        ]
    }


