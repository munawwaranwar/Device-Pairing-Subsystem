"""
Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

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

from sqlalchemy import func
from app.api.v1.common.generate_paircode import gen_paircode
from app.api.v1.models.owner import Owner
from app.api.v1.models.devices import Devices
from app.api.v1.models.imeis import Imei
from app.api.v1.models.pairing_codes import Pairing_Codes
from app import db
import re
import requests
from app import conf
from flask_babel import lazy_gettext as _


# noinspection PyUnboundLocalVariable,PyUnusedLocal
def authority_input(contact_no, model, brand, serial_no, mac, rat, imei):
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
                r'[A-F0-9]{2}[:.-][A-F0-9]{2}[:.-][A-F0-9]{2}[:.-][A-F0-9]{2}[:.-][A-F0-9]{2}[:.-]'
                r'[A-F0-9]{2}[:.-][A-F0-9]{2}[:.-][A-F0-9]{2}')
            mac_match3 = mac_pat_3.fullmatch(mac)
            mac_pat_4 = re.compile(r'[A-F0-9]{4}[:.-][A-F0-9]{4}[:.-][A-F0-9]{4}[:.-][A-F0-9]{4}')
            mac_match4 = mac_pat_4.fullmatch(mac)

            if mac_match1 or mac_match2 or mac_match3 or mac_match4:
                chk_mac = True
        else:
            chk_mac = True

        pattern_rat = re.compile(r'(2G|3G|4G|5G)[,]?(2G|3G|4G|5G)?[,]?(2G|3G|4G|5G)?[,]?(2G|3G|4G|5G)?')
        match_rat = pattern_rat.fullmatch(rat)

        lang_model = re.match(conf['regex'][conf['supported_languages']['default_language']]['model_name'], model)
        lang_brand = re.match(conf['regex'][conf['supported_languages']['default_language']]['brand'], brand)
        # pattern_model_brand = re.compile(r'[a-zA-Z0-9_ .\'-]{1,1000}')
        # match_model = pattern_model_brand.fullmatch(model)
        # match_brand = pattern_model_brand.fullmatch(brand)

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

        if lang_model and lang_brand and match_serial and match_rat and chk_mac and chk_imei and chk_contact:
            chk_duplicate = Devices.query.filter(Devices.serial_no == '{}'.format(serial_no)).first()
                                        # to check if device is not already registered
            if chk_duplicate:
                rtn_msg = {
                    "Error": _("Device with same Serial number already exists")
                }
                return rtn_msg, 422

            else:
                chk_owner_id = Owner.query.filter(Owner.contact == '{}'.format(contact_msisdn)).first()

                if not chk_owner_id:

                    max_owner_id = db.session.query(func.max(Owner.id)).scalar()  # query to get maximum owner_id

                    if not max_owner_id:
                        max_owner_id = 1

                    else:
                        max_owner_id += 1

                    add_owner = Owner(id=max_owner_id, contact=contact_msisdn)

                    db.session.add(add_owner)

                    tmp_id = max_owner_id

                else:

                    tmp_id = chk_owner_id.id

                max_dev_id = db.session.query(func.max(Devices.id)).scalar()  # query to get maximum device_id

                if not max_dev_id:
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

                if not max_imei_id:
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
                    "msg": _("Device's information has been successfully loaded"),
                    "pair_code": pair_code
                }

                message = "Device has been registered with Authority. " \
                          "Your Activation Pair-Code is ({})".format(pair_code)

                payload = {'username': 'tester', 'password': 'foobar', 'smsc': 'at', 'from': '7787',
                           'to': contact_msisdn, 'text': message}

                r = requests.get(conf['kannel_sms'], params=payload)

                return rtn_msg, 200

        elif not chk_contact:

            rtn_msg = {
                "Error": _("Contact-MSISDN format is not correct")
            }
            return rtn_msg, 422

        elif not lang_model:

            rtn_msg = {
                "Error": _("Model format is not correct")
            }
            return rtn_msg, 422

        elif not lang_brand:

            rtn_msg = {
                "Error": _("Brand format is not correct")
            }
            return rtn_msg, 422

        elif not match_rat:

            rtn_msg = {
                "Error": _("RAT format is not correct")
            }
            return rtn_msg, 422

        elif not match_serial:

            rtn_msg = {
                "Error": _("Serial-Number format is not correct")
            }
            return rtn_msg, 422

        elif not chk_mac:

            rtn_msg = {
                "Error": _("MAC format is not correct")
            }
            return rtn_msg, 422

        elif not chk_imei:

            rtn_msg = {
                "Error": _("IMEI format is not correct")
            }
            return rtn_msg, 422

    except Exception as e:
        db.session.rollback()

    finally:
        db.session.close()
