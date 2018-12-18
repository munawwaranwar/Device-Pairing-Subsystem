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

from time import strftime
from app.api.v1.models.pairings import Pairing
from app import db
import requests
import re
from app import conf


def add_pair_cnfrm(confirm, primary_msisdn, sender_no, mno):
    """ Function to verify confirmations from secondary pairs """
    try:
        rtn_msg = ""
        cnfm_sms = False

        pattern_msisdn = re.compile(r'923\d{9,12}')
        match_sender = pattern_msisdn.fullmatch(sender_no)
        match_primary = pattern_msisdn.fullmatch(primary_msisdn)

        pattern_mno = re.compile(r'[a-zA-Z0-9]{1,20}')
        match_mno = pattern_mno.fullmatch(mno)

        pattern_confirm = re.compile(r'(YES|Yes|yes|NO|No|no){1}')
        match_confirm = pattern_confirm.fullmatch(confirm)

        if match_sender and match_primary and match_mno and match_confirm:

            chk_primary = Pairing.query.filter(Pairing.msisdn == '{}'.format(primary_msisdn))\
                                       .filter(Pairing.is_primary == True)\
                                       .filter(Pairing.end_date == None).all()

            if chk_primary:

                for q in chk_primary:

                    if confirm == "NO" or confirm == "no" or confirm == "No":

                        othr_chks = Pairing.query.filter(Pairing.msisdn == '{}'.format(sender_no),
                                                         Pairing.is_primary == False,
                                                         Pairing.primary_id == '{}'.format(q.id),
                                                         Pairing.end_date == None,
                                                         Pairing.add_pair_status == False).first()

                        if othr_chks:

                            db.session.delete(othr_chks)
                            db.session.commit()
                            rtn_msg = "Request of additional pair is rejected by ({})".format(sender_no)
                            cnfm_sms = True

                        else:

                            rtn_msg = "Confirmation of additional pair request is not done by valid MSISDN"

                    elif confirm == "YES" or confirm == "Yes" or confirm == "yes":

                        othr_chks = Pairing.query.filter(db.and_(Pairing.msisdn == '{}'.format(sender_no),
                                                                 Pairing.is_primary == False,
                                                                 Pairing.primary_id == '{}'.format(q.id),
                                                                 Pairing.end_date == None,
                                                                 Pairing.add_pair_status == False)).first()

                        if othr_chks:

                            othr_chks.add_pair_status = True
                            othr_chks.operator_name = mno
                            othr_chks.updated_at = '{}'.format(strftime("%Y-%m-%d %H:%M:%S"))
                            db.session.commit()
                            rtn_msg = "Request of additional pair from ({}) is accepted by ({})".\
                                format(primary_msisdn, sender_no)

                            cnfm_sms = True

                        else:

                            rtn_msg = "Confirmation of additional pair request is not done by valid MSISDN"

            else:
                rtn_msg = "Wrong Primary number mentioned in SMS"

            if cnfm_sms:

                chg_msisdn = '0' + primary_msisdn[2:]

                payload = {'username': 'tester', 'password': 'foobar', 'smsc': 'at', 'from': '7787',
                           'to': chg_msisdn, 'text': rtn_msg}

                r = requests.get(conf['kannel_sms'], params=payload)

                cnfm_sms = False

            return rtn_msg

        elif not match_sender:
            return "Sender MSISDN format is not correct"

        elif not match_primary:
            return "Primary MSISDN format is not correct"

        elif not match_mno:
            return "Operator name is not correct"

        elif not match_confirm:
            return "Confirmation is not proprely done"

    except Exception as e:
        db.session.rollback()

    finally:
        db.session.close()
