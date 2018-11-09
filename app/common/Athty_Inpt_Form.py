"""
DPS notification resource package.
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

from sqlalchemy import func
from app.common.generate_PairCode import gen_paircode
from app.Models.owner import Owner
from app.Models.devices import Devices
from app.Models.imeis import Imei
from app.Models.pairing_codes import Pairing_Codes
from app import db
import re
import requests
from app import conf



def authority_input(contact_no, model, brand, serial_no, mac, rat,imei):
    """ Function to register device parameters from Authority's portal and assigns pair-code """
    try:

        rtn_msg = ""
        chk_imei, chk_mac, chk_contact = False, False, False

        if mac is not None:
            mac_pat_1 = re.compile(
                r'[A-F0-9]{2}[:.-][A-F0-9]{2}[:.-][A-F0-9]{2}[:.-][A-F0-9]{2}[:.-][A-F0-9]{2}[:.-][A-F0-9]{2}')
            mac_match1 = mac_pat_1.fullmatch(mac)
            mac_pat_2 = re.compile(r'[A-F0-9]{3}[:.-][A-F0-9]{3}[:.-][A-F0-9]{3}[:.-][A-F0-9]{3}')
            mac_match2 = mac_pat_2.fullmatch(mac)
            mac_pat_3 = re.compile(
                r'[A-F0-9]{2}[:.-][A-F0-9]{2}[:.-][A-F0-9]{2}[:.-][A-F0-9]{2}[:.-][A-F0-9]{2}[:.-][A-F0-9]{2}[:.-][A-F0-9]{2}[:.-][A-F0-9]{2}')
            mac_match3 = mac_pat_3.fullmatch(mac)
            mac_pat_4 = re.compile(r'[A-F0-9]{4}[:.-][A-F0-9]{4}[:.-][A-F0-9]{4}[:.-][A-F0-9]{4}')
            mac_match4 = mac_pat_4.fullmatch(mac)

            if (mac_match1 or mac_match2 or mac_match3 or mac_match4):
                chk_mac = True
        else:
            chk_mac = True

        pattern_rat = re.compile(r'(2G|3G|4G|5G)[,]?(2G|3G|4G|5G)?[,]?(2G|3G|4G|5G)?[,]?(2G|3G|4G|5G)?')
        match_rat = pattern_rat.fullmatch(rat)

        pattern_model_brand = re.compile(r'[a-zA-Z0-9_ .\'-]{1,1000}')
        match_model = pattern_model_brand.fullmatch(model)
        match_brand = pattern_model_brand.fullmatch(brand)

        pattern_serial_no = re.compile(r'[a-zA-Z0-9]{1,1000}')
        match_serial = pattern_serial_no.fullmatch(serial_no)

        if contact_no['CC'] == conf['CC']:
            if (contact_no['SN'].isdigit()) and (len(contact_no['SN']) < 13):
                contact_msisdn = contact_no['CC'] + contact_no['SN']
                chk_contact = True

        for i in imei:

            pattern_imei = re.compile(r'[A-F0-9]{14,16}')
            match_imei = pattern_imei.fullmatch(i)

            if len(i) < 17 and match_imei:
                chk_imei = True

            else:
                chk_imei = False
                break

        if (match_model and match_brand and match_serial and match_rat and chk_mac == True and chk_imei == True and chk_contact == True):

            chk_duplicate = Devices.query.filter(Devices.serial_no == '{}'.format(serial_no)).first()
                                        # to check if device is not already registered
            if chk_duplicate:
                rtn_msg = {
                    "Error": "Device with same Serial number already exists"
                }
                return rtn_msg, 422

            else:
                chk_owner_id = Owner.query.filter(Owner.contact == '{}'.format(contact_msisdn)).first()

                if not chk_owner_id:

                    max_owner_id = db.session.query(func.max(Owner.id)).scalar()  # query to get maximum owner_id

                    if max_owner_id == None:
                        max_owner_id = 1

                    else:
                        max_owner_id += 1

                    add_owner = Owner(id=max_owner_id, contact=contact_msisdn)

                    db.session.add(add_owner)

                    tmp_id = max_owner_id

                else:

                    tmp_id = chk_owner_id.id

                max_dev_id = db.session.query(func.max(Devices.id)).scalar()  # query to get maximum device_id

                if max_dev_id == None:
                    max_dev_id = 1

                else:
                    max_dev_id += 1

                add_device = Devices(id=max_dev_id,
                                     model=model,
                                     brand=brand,
                                     serial_no=serial_no,
                                     mac=mac,
                                     rat=rat.strip(','),
                                     owner_id=tmp_id)

                db.session.add(add_device)

                max_imei_id = db.session.query(func.max(Imei.id)).scalar()  # query to get maximum IMEI_id

                if max_imei_id == None:
                    max_imei_id = 1

                else:
                    max_imei_id += 1

                for i in imei:
                    add_imei = Imei(id=max_imei_id,
                                    imei=i,
                                    device_id=max_dev_id)

                    db.session.add(add_imei)

                    max_imei_id += 1

                pair_code = gen_paircode()
                add_paircode = Pairing_Codes(pair_code=pair_code,
                                             is_active=True,
                                             device_id=max_dev_id)

                db.session.add(add_paircode)

                db.session.commit()

                rtn_msg = {
                    "msg": "Device's information has been successfully loaded",
                    "pair_code": pair_code
                }

                message = "Device has been registered with Authority. Your Activation Pair-Code is ({})".format(pair_code)

                payload = {'username': 'tester', 'password': 'foobar', 'smsc': 'at', 'from': '7787',
                           'to': contact_msisdn, 'text': message}

                r = requests.get(conf['kannel_sms'], params=payload)

                return rtn_msg, 200

        elif chk_contact == False:

            rtn_msg = {
                "Error": "Contact-MSISDN format is not correct"
            }
            return rtn_msg, 422

        elif not match_model:

            rtn_msg = {
                "Error": "Model format is not correct"
            }
            return rtn_msg, 422

        elif not match_brand:

            rtn_msg = {
                "Error": "Brand format is not correct"
            }
            return rtn_msg, 422

        elif not match_rat:

            rtn_msg = {
                "Error": "RAT format is not correct"
            }
            return rtn_msg, 422

        elif not match_serial:

            rtn_msg = {
                "Error": "Serial-Number format is not correct"
            }
            return rtn_msg, 422

        elif chk_mac == False:

            rtn_msg = {
                "Error": "MAC format is not correct"
            }
            return rtn_msg, 422

        elif chk_imei == False:

            rtn_msg = {
                "Error": "IMEI format is not correct"
            }
            return rtn_msg, 422

    except Exception as e:
        db.session.rollback()

    finally:
        db.session.close()

