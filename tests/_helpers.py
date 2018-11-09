"""
DRS Unit Test helper module.

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
from app.Models.owner import Owner
from app.Models.devices import Devices
from app.Models.imeis import Imei
from app.Models.pairings import Pairing
from app.Models.pairing_codes import Pairing_Codes
from sqlalchemy import text

def create_view(db):
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


def complete_db_insertion(session,db,t_owner_id,t_contact,t_device_id,t_model,t_brand,t_serial,t_rat,t_paircode,t_imei_id,t_imei):
    owner_add = Owner(id=t_owner_id, contact= t_contact)
    session.add(owner_add)
    device_add = Devices(id=t_device_id, model=t_model, brand=t_brand, serial_no=t_serial, rat=t_rat,owner_id=t_owner_id)
    session.add(device_add)
    paircode_add = Pairing_Codes(pair_code = t_paircode, is_active=True, device_id=t_device_id)
    session.add(paircode_add)
    imei_add = Imei(id= t_imei_id, imei= t_imei, device_id= t_device_id)
    session.add(imei_add)




# def seed_database(db):
#     """Helper method to seed data into the database."""
#     seeder = Seed(db)
#     seeder.seed_technologies()
#     seeder.seed_status()
#     seeder.seed_device_types()
#     seeder.seed_documents()


# def create_database(db):
#     """Helper method to index database and create views."""
#     database = CreateDatabase(db)
#     database.run()
