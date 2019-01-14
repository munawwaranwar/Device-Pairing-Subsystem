"""
DPS DB Migration package.
Copyright (c) 2018 Qualcomm Technologies, Inc.
 All rights reserved.
 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
 limitations in the disclaimer below) provided that the following conditions are met:
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
 disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
 disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
 products derived from this software without specific prior written permission.
 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
 THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
 TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.
"""

import sys
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from sqlalchemy import text
from app.api.v1.models.owner import Owner
from app.api.v1.models.devices import Devices
from app.api.v1.models.imeis import Imei
from app.api.v1.models.pairing_codes import Pairing_Codes
from app.api.v1.models.pairings import Pairing
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
