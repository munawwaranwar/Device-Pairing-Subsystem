"""
SPDX-License-Identifier: BSD-4-Clause-Clear

Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following
  disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
  disclaimer in the documentation and/or other materials provided with the distribution.
* All advertising materials mentioning features or use of this software, or any deployment of this software, or
  documentation accompanying any distribution of this software, must display the trademark/logo as per the details
  provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
* Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
  products derived from this software without specific prior written permission.

SPDX-License-Identifier: ZLIB-ACKNOWLEDGEMENT

Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable
for any damages arising from the use of this software.

Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter
it and redistribute it freely, subject to the following restrictions:

* The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If
  you use this software in a product, an acknowledgment is required by displaying the trademark/logo as per the details
  provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
* Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
* This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
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


def athty_input_payload(cc, sn, model, brand, serial_no, rat, imei, mac=None, cond=0):
    if cond == 0:
        data = {
            "CONTACT": {
                        "CC": cc,
                        "SN": sn
                    },
            "MODEL": model,
            "BRAND": brand,
            "Serial_No": serial_no,
            "MAC": mac,
            "RAT": rat,
            "IMEI": imei
            }
    elif cond == 1:
        data = {
            "CONTACT": {
                    "SN": sn
            },
            "MODEL": model,
            "BRAND": brand,
            "Serial_No": serial_no,
            "MAC": mac,
            "RAT": rat,
            "IMEI": imei
        }
    elif cond == 2:
        data = {
            "CONTACT": {
                "CC": cc
            },
            "MODEL": model,
            "BRAND": brand,
            "Serial_No": serial_no,
            "MAC": mac,
            "RAT": rat,
            "IMEI": imei
        }
    elif cond == 3:
        data = {
            "CONTACT": {
                "CC": cc,
                "SN": sn
            },
            "BRAND": brand,
            "Serial_No": serial_no,
            "MAC": mac,
            "RAT": rat,
            "IMEI": imei
        }
    elif cond == 4:
        data = {
            "CONTACT": {
                "CC": cc,
                "SN": sn
            },
            "MODEL": model,
            "Serial_No": serial_no,
            "MAC": mac,
            "RAT": rat,
            "IMEI": imei
        }
    elif cond == 5:
        data = {
            "CONTACT": {
                "CC": cc,
                "SN": sn
            },
            "MODEL": model,
            "BRAND": brand,
            "MAC": mac,
            "RAT": rat,
            "IMEI": imei
        }
    elif cond == 6:
        data = {
            "CONTACT": {
                "CC": cc,
                "SN": sn
            },
            "MODEL": model,
            "BRAND": brand,
            "Serial_No": serial_no,
            "MAC": mac,
            "IMEI": imei
        }
    elif cond == 7:
        data = {
            "CONTACT": {
                "CC": cc,
                "SN": sn
            },
            "MODEL": model,
            "BRAND": brand,
            "Serial_No": serial_no,
            "MAC": mac,
            "RAT": rat
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
    if cond == 0:
            data = {
                "start": start,
                "limit": limit,
                "search_args": {
                    "MAC": t_mac,
                    "CONTACT": t_contact,
                    "Serial_No": t_serial,
                    "IMEI": t_imei
                }
        }
    elif cond == 1:
        data = {
            "start": start,
            "limit": limit,
            "search_args": {
                "MAC": t_mac,
                "CONTACT": t_contact,
                "Serial_No": t_serial
            }
        }
    elif cond == 2:
        data = {
            "start": start,
            "limit": limit,
            "search_args": {
                "MAC": t_mac,
                "CONTACT": t_contact,
                "IMEI": t_imei
            }
        }
    elif cond == 3:
        data = {
            "start": start,
            "limit": limit,
            "search_args": {
                "MAC": t_mac,
                "Serial_No": t_serial,
                "IMEI": t_imei
            }
        }
    elif cond == 4:
        data = {
            "start": start,
            "limit": limit,
            "search_args": {
                "CONTACT": t_contact,
                "Serial_No": t_serial,
                "IMEI": t_imei
            }
        }
    elif cond == 5:
        data = {
            "start": start,
            "limit": limit,
            "search_args": {
                "MAC": t_mac
            }
        }
    elif cond == 6:
        data = {
            "start": start,
            "limit": limit,
            "search_args": {
                "CONTACT": t_contact
            }
        }
    elif cond == 7:
        data = {
            "start": start,
            "limit": limit,
            "search_args": {
                "Serial_No": t_serial
            }
        }
    elif cond == 8:
        data = {
            "start": start,
            "limit": limit,
            "search_args": {
                "IMEI": t_imei
            }
        }
    elif cond == 9:
        data = {
            "start": start,
            "limit": limit,
            "search_args": {
            }
        }
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


def mno_imsi_upload(cc, sn, mno, imsi, cond=0):
    if cond == 0:
        data = {
            "MSISDN": {
                        "CC": cc,
                        "SN": sn
                    },
            "mno": mno,
            "IMSI": imsi
            }
    elif cond == 1:
        data = {
            "MSISDN": {
                        "SN": sn
                    },
            "mno": mno,
            "IMSI": imsi
            }
    elif cond == 2:
        data = {
            "MSISDN": {
                        "CC": cc
                    },
            "mno": mno,
            "IMSI": imsi
            }
    elif cond == 3:
        data = {
            "MSISDN": {
                "CC": cc,
                "SN": sn
            },
            "IMSI": imsi
        }
    elif cond == 4:
        data = {
            "MSISDN": {
                "CC": cc,
                "SN": sn
            },
            "mno": mno
        }
    elif cond == 5:
        data = {
            "": {
                "CC": cc,
                "SN": sn
            },
            "mno": mno,
            "IMSI": imsi
        }
    return data
