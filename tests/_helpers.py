"""
Copyright (c) 2018-2021 Qualcomm Technologies, Inc.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written permission.
* The origin of this software must not be misrepresented; you must not claim that you wrote the original software.
If you use this software in a product, an acknowledgment is required by displaying the trademark/log as per the details
provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
* Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
* This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.
"""


from sqlalchemy import text
from time import strftime
from app.api.v1.models.owner import Owner
from app.api.v1.models.devices import Devices
from app.api.v1.models.imeis import Imei
from app.api.v1.models.pairings import Pairing
from app.api.v1.models.pairing_codes import Pairing_Codes


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


def complete_db_insertion(session, db, t_owner_id, t_contact, t_device_id, t_model, t_brand, t_serial, t_rat,
                          t_paircode, t_imei_id, t_imei, t_mac=None):

    owner_add = Owner(id=t_owner_id, contact=t_contact)
    session.add(owner_add)
    device_add = Devices(id=t_device_id, model=t_model, brand=t_brand, serial_no=t_serial, rat=t_rat,
                         owner_id=t_owner_id, mac=t_mac)
    session.add(device_add)
    paircode_add = Pairing_Codes(pair_code=t_paircode, is_active=True, device_id=t_device_id)
    session.add(paircode_add)
    imei_add = Imei(id=t_imei_id, imei=t_imei, device_id=t_device_id)
    session.add(imei_add)
    db.session.commit()


def first_pair_db_insertion(session, db, t_pair_id, t_msisdn, t_mno, t_imei_id):

    primary_add = Pairing(id=t_pair_id,
                          primary_id=0,
                          msisdn=t_msisdn,
                          is_primary=True,
                          creation_date=strftime("%Y-%m-%d %H:%M:%S"),
                          operator_name=t_mno,
                          add_pair_status=True,
                          imei_id=t_imei_id)
    session.add(primary_add)
    db.session.commit()


def add_pair_db_insertion(session, db, t_sec_id, t_primary_id, t_sec_msisdn, t_imei_id):
    sec_add = Pairing(id=t_sec_id,  # adding secondary pair incase one or more secondary pairs already exists
                      primary_id=t_primary_id,
                      msisdn=t_sec_msisdn,
                      is_primary=False,
                      creation_date=strftime("%Y-%m-%d %H:%M:%S"),
                      add_pair_status=False,
                      imei_id=t_imei_id)
    session.add(sec_add)
    db.session.commit()


def add_pair_confrm_db_insertion(session, db, t_sec_no, t_primary_id, t_mno):
    chks = Pairing.query.filter(db.and_(Pairing.msisdn == '{}'.format(t_sec_no),
                                             Pairing.is_primary == False,
                                             Pairing.primary_id == '{}'.format(t_primary_id),
                                             Pairing.end_date == None,
                                             Pairing.add_pair_status == False)).first()
    if chks:
        chks.add_pair_status = True
        chks.operator_name = t_mno
        chks.updated_at = '{}'.format(strftime("%Y-%m-%d %H:%M:%S"))
        db.session.commit()


def athty_input_payload(sn, model, brand, serial_no, rat, imei, mac=None, cond=0):
    if cond == 0:       # all parameters present
        data = {
            "contact_no": sn,
            "model": model,
            "brand": brand,
            "serial_no": serial_no,
            "mac": mac,
            "rat": rat,
            "imei": imei
            }
    elif cond == 1:     # contact_no is missing
        data = {
            "model": model,
            "brand": brand,
            "serial_no": serial_no,
            "mac": mac,
            "rat": rat,
            "imei": imei
        }
    elif cond == 2:     # model is missing
        data = {
            "contact_no": sn,
            "brand": brand,
            "serial_no": serial_no,
            "mac": mac,
            "rat": rat,
            "imei": imei
        }
    elif cond == 3:     # brand is missing
        data = {
            "contact_no": sn,
            "model": model,
            "serial_no": serial_no,
            "mac": mac,
            "rat": rat,
            "imei": imei
        }
    elif cond == 4:     # serial_no is missing
        data = {
            "contact_no": sn,
            "model": model,
            "brand": brand,
            "mac": mac,
            "rat": rat,
            "imei": imei
        }
    elif cond == 5:     # rat is missing
        data = {
            "contact_no": sn,
            "model": model,
            "brand": brand,
            "serial_no": serial_no,
            "mac": mac,
            "imei": imei
        }
    elif cond == 6:     # imei is missing
        data = {
            "contact_no": sn,
            "model": model,
            "brand": brand,
            "serial_no": serial_no,
            "mac": mac,
            "rat": rat,
        }
    elif cond == 7:     # mac is missing
        data = {
            "contact_no": sn,
            "model": model,
            "brand": brand,
            "serial_no": serial_no,
            "rat": rat,
            "imei": imei
        }
    return data


def athty_search_db_insertion(session, db, t_owner_id, t_contact, t_device_id, t_model, t_brand, t_serial,
                              t_rat, t_paircode, t_imei_id, t_imei, t_mac=None):

    owner_add = Owner(id=t_owner_id, contact=t_contact)
    session.add(owner_add)
    device_add = Devices(id=t_device_id, model=t_model, brand=t_brand, serial_no=t_serial,
                         rat=t_rat, owner_id=t_owner_id, mac=t_mac)

    session.add(device_add)

    imei_id = t_imei_id
    for val in t_imei:
        imei_add = Imei(id=imei_id, imei=val, device_id=t_device_id)
        session.add(imei_add)
        imei_id += 1

    paircode_add = Pairing_Codes(pair_code=t_paircode, is_active=True, device_id=t_device_id)
    session.add(paircode_add)

    db.session.commit()


def athty_search_payload(start, limit, t_imei, t_mac, t_serial, t_contact, cond=0):
    url = 'api/v1/device-search'
    if cond == 0:
        data = '{api}?start={st}&limit={lt}&contact={msisdn}&imei={imei}&mac={mac}&serial_no={sno}'. \
            format(api=url, st=start, lt=limit, msisdn=t_contact, imei=t_imei, mac=t_mac, sno=t_serial)

    elif cond == 1:     # contact is missing
        data = '{api}?start={st}&limit={lt}&imei={imei}&mac={mac}&serial_no={sno}'.\
                format(api=url, st=start, lt=limit, imei=t_imei, mac=t_mac, sno=t_serial)

    elif cond == 2:     # imei is missing
        data = '{api}?start={st}&limit={lt}&contact={msisdn}&mac={mac}&serial_no={sno}'. \
            format(api=url, st=start, lt=limit, msisdn=t_contact, mac=t_mac, sno=t_serial)

    elif cond == 3:     # mac is missing
        data = '{api}?start={st}&limit={lt}&contact={msisdn}&imei={imei}&serial_no={sno}'. \
            format(api=url, st=start, lt=limit, msisdn=t_contact, imei=t_imei, sno=t_serial)

    elif cond == 4:     # serial_no is missinf
        data = '{api}?start={st}&limit={lt}&contact={msisdn}&imei={imei}&mac={mac}'. \
            format(api=url, st=start, lt=limit, msisdn=t_contact, imei=t_imei, mac=t_mac)

    elif cond == 5:     # searching through MAC only
        data = '{api}?start={st}&limit={lt}&mac={mac}'.\
            format(api=url, st=start, lt=limit, mac=t_mac)

    elif cond == 6:     # searching through CONTACT only
        data = '{api}?start={st}&limit={lt}&contact={msisdn}'. \
            format(api=url, st=start, lt=limit, msisdn=t_contact)

    elif cond == 7:     # searching through Serial_No only
        data = '{api}?start={st}&limit={lt}&serial_no={sno}'. \
            format(api=url, st=start, lt=limit, sno=t_serial)

    elif cond == 8:     # searching through IMEI only
        data = '{api}?start={st}&limit={lt}&imei={imei}'. \
            format(api=url, st=start, lt=limit, imei=t_imei)

    elif cond == 9:
        data = '{api}?start={st}&limit={lt}'. \
            format(api=url, st=start, lt=limit)

    elif cond == 10:
        data = {
            "start": start,
            "limit": limit,
            "search_a": {
                "MAC": t_mac,
                "CONTACT": t_contact,
                "Serial_No": t_serial,
                "IMEI": t_imei
            }
        }
    return data


def mno_imsi_upload(sn, mno, imsi, cond=0):

    if cond == 0:
        data = {
            "msisdn": sn,
            "operator": mno,
            "imsi": imsi
            }
    elif cond == 1:     # MSISDN is missing
        data = {
            "operator": mno,
            "imsi": imsi
            }
    elif cond == 2:     # Operator is missing
        data = {
            "msisdn": sn,
            "imsi": imsi
            }
    elif cond == 3:     # IMSI is missing
        data = {
            "msisdn": sn,
            "operator": mno
        }

    return data
