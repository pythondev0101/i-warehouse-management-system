import platform
import csv
from config import basedir
from app import db
from app.core.cli import core_install
from iwms import bp_iwms
from iwms.models import UnitOfMeasure



@bp_iwms.cli.command("install")
def install():
    if not core_install():
        print("Installation failed!")
        return False

    if platform.system() == "Windows":
        # bin_locations_path = basedir + "\\app" + "\\core" + "\\csv" + "\\iwms_bin_location.csv"
        # suppliers_path = basedir + "\\app" + "\\core" + "\\csv" + "\\iwms_supplier.csv"
        # stock_item_types_path = basedir + "\\app" + "\\core" + "\\csv" + "\\iwms_stock_item_type.csv"
        uom_path = basedir + "\\iwms" + "\\static" + "\\csv" + "\\iwms_unit_of_measure.csv"
        # categories_path = basedir + "\\app" + "\\core" + "\\csv" + "\\iwms_category.csv"
        # zones_path = basedir + "\\app" + "\\core" + "\\csv" + "\\iwms_zone.csv"
        # stock_items_path = basedir + "\\app" + "\\core" + "\\csv" + "\\iwms_stock_item.csv"
        # terms_path = basedir + "\\app" + "\\core" + "\\csv" + "\\iwms_term.csv"
        # ship_vias_path = basedir + "\\app" + "\\core" + "\\csv" + "\\iwms_ship_via.csv"
        # clients_path = basedir + "\\app" + "\\core" + "\\csv" + "\\iwms_client.csv"
        # item_uom_line_path = basedir + "\\app" + "\\core" + "\\csv" + "\\iwms_stock_item_uom_line.csv"
        # item_suppliers_path = basedir + "\\app" + "\\core" + "\\csv" + "\\iwms_suppliers.csv"

    elif platform.system() == "Linux":
        # bin_locations_path = basedir + "/app/core/csv/iwms_bin_location.csv"
        # suppliers_path = basedir + "/app/core/csv/iwms_supplier.csv"
        # stock_item_types_path = basedir + "/app/core/csv/iwms_stock_item_type.csv"
        uom_path = basedir + "/iwms/static/csv/iwms_unit_of_measure.csv"
        # categories_path = basedir + "/app/core/csv/iwms_category.csv"
        # zones_path = basedir + "/app/core/csv/iwms_zone.csv"
        # stock_items_path = basedir + "/app/core/csv/iwms_stock_item.csv"
        # terms_path = basedir + "/app/core/csv/iwms_term.csv"
        # ship_vias_path = basedir + "/app/core/csv/iwms_ship_via.csv"
        # clients_path = basedir + "/app/core/csv/iwms_client.csv"
        # item_uom_line_path = basedir + "/app/core/csv/iwms_stock_item_uom_line.csv"
        # item_suppliers_path = basedir + "/app/core/csv/iwms_suppliers.csv"
    else:
        print("Installation failed: Not supported OS!")
        return False

    print("Inserting unit of measures...")
    if not UnitOfMeasure.query.count() > 0:
        with open(uom_path) as f:
            csv_file = csv.reader(f)
            for rid,row in enumerate(csv_file):
                if not rid == 0:
                    uom = UnitOfMeasure()
                    uom.code, uom.description = row[0], row[1]
                    uom.created_by = "System"
                    db.session.add(uom)
            db.session.commit()
        print("Unit of measures done!")
    else:
        print("Unit of measures exists!")

    print("Installation complete!")
    return True