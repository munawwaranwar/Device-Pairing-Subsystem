"""
DPS Additional-Pair package.
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

from time import strftime
from sqlalchemy import func
from app import db
from app import conf
from app.api.v1.models.pairings import Pairing
import requests
import re


def add_pair(add_msisdn, sender_num):
    """ Function to create additional/secondary pairs for a particular device """
    try:
        rtn_msg = ""
        chk_1, chk_2, chk_3, cnfm_sms = False, False, False, False

        pattern_msisdn = re.compile(r'923\d{9,12}')
        match_primary = pattern_msisdn.fullmatch(sender_num)
        match_secondary = pattern_msisdn.fullmatch(add_msisdn)

        if match_primary and match_secondary:

            chk_primary = Pairing.query.filter(db.and_(Pairing.msisdn == '{}'.format(sender_num),
                                                       Pairing.is_primary == True,
                                                       Pairing.end_date == None,
                                                       Pairing.msisdn != add_msisdn)).all()

            if chk_primary:

                chk_1 = True
                max_pair_id = db.session.query(func.max(Pairing.id)).scalar()  # query to get maximum Pairing_id

                if max_pair_id is None:
                    max_pair_id = 1

                else:
                    max_pair_id = max_pair_id + 1

                for q in chk_primary:

                    chk_sec = Pairing.query.filter(Pairing.primary_id == '{}'.format(q.id))\
                                           .filter(Pairing.end_date == None).all()

                    if chk_sec:
                        for r in chk_sec:

                            if r.msisdn != add_msisdn:      # checking if MSISDN is already paired or not
                                chk_2 = True

                                if len(chk_sec) < conf['pair_limit']:      # checking if pair-limit is exceeded or not
                                    chk_3 = True

                                else:
                                    chk_3 = False
                                    return conf['sms_pair_limit_breached']

                            else:
                                chk_2 = False
                                return "MSISDN ({})already paired with the device".format(add_msisdn)

                        if chk_1 and chk_2 and chk_3:

                            adding1 = Pairing(id=max_pair_id,
                                              primary_id=q.id,
                                              msisdn=add_msisdn,
                                              is_primary=False,
                                              creation_date=strftime("%Y-%m-%d %H:%M:%S"),
                                              add_pair_status=False,
                                              imei_id=q.imei_id)
                            # adding secondary pair incase one or more secondary pairs already exists

                            db.session.add(adding1)
                            db.session.commit()

                            max_pair_id += 1

                            cnfm_sms = True

                            rtn_msg = "Secondary pair is added by ({}). Confirmation is awaited from ({})".\
                                format(sender_num, add_msisdn)

                    else:
                        adding2 = Pairing(id=max_pair_id,       # adding secondary pair for first time
                                          primary_id=q.id,
                                          msisdn=add_msisdn,
                                          is_primary=False,
                                          creation_date=strftime("%Y-%m-%d %H:%M:%S"),
                                          add_pair_status=False,
                                          imei_id=q.imei_id)

                        db.session.add(adding2)
                        db.session.commit()

                        max_pair_id += 1

                        cnfm_sms = True

                        rtn_msg = "Secondary pair is added by ({}). Confirmation is awaited from ({})".\
                            format(sender_num, add_msisdn)

            else:

                rtn_msg = "Request not made by Primary-Pair or number-to-be-added is Primary number"

                chk_1 = False

            if cnfm_sms:

                chg_msisdn = '0' + add_msisdn[2:]

                message = "CONFIRM [{}]\nPlease reply with Yes/No space {}".format(sender_num, sender_num)

                payload = {'username': 'tester', 'password': 'foobar', 'smsc': 'at', 'from': '7787',
                           'to': chg_msisdn, 'text': message}

                r = requests.get(conf['kannel_sms'], params=payload)
                cnfm_sms = False

            return rtn_msg

        elif not match_primary:
            return "Primary MSISDN format is not correct"

        elif not match_secondary:
            return "Secondary MSISDN format is not correct"

    except Exception as e:
        db.session.rollback()

    finally:
        db.session.close()
