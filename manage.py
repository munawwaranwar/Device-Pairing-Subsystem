import sys
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from sqlalchemy import text
from app.Models.owner import Owner
from app.Models.devices import Devices
from app.Models.imeis import Imei
from app.Models.pairing_codes import Pairing_Codes
from app.Models.pairings import Pairing
from app import app, db



migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def create_view():
    try:
        query = text("""CREATE OR REPLACE VIEW public.test_view AS  SELECT owner.contact,
        imei.imei,
        devices.brand,
        devices.model,
        devices.serial_no,
        devices.mac,
        pairing_codes.pair_code,
        pairing_codes.is_active
       FROM owner
         JOIN devices ON devices.owner_id = owner.id
         JOIN imei ON imei.device_id = devices.id
         JOIN pairing_codes ON pairing_codes.device_id = devices.id;""")

        db.engine.execute(query)

    except Exception as e:
        db.session.rollback()

    finally:
        db.session.close()

@manager.command
def create_indexes():
    """ method to create indexes on the database """
    with db.engine.connect() as conn:
        with conn.execution_options(isolation_level='AUTOCOMMIT'):
            try:
                app.logger.info(Pairing.create_index(conn))
                app.logger.info(Pairing_Codes.create_index(conn))
                app.logger.info(Imei.create_index(conn))
                app.logger.info(Devices.create_index(conn))
                app.logger.info(Owner.create_index(conn))
            except Exception as e:
                app.logger.error('an unknown error occured during indexing, see the logs below for details')
                app.logger.exception(e)
                sys.exit(1)


if __name__ == '__main__':
    manager.run()


