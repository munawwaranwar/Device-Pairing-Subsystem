"""
DPS First-Pair package.
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
from app.api.v1.models.pairing_codes import Pairing_Codes
from app.api.v1.models.imeis import Imei
from app.api.v1.models.pairings import Pairing
from app import db
import re


def first_pair(sms_paircode, sender_num, mno):
    """ Function to create the first/primary pair for the mobile devices """

    try:
        rtn_msg = ""
        max_pair_count = 0

        pattern_sender_no = re.compile(r'923\d{9,12}')
        match_sender_no = pattern_sender_no.fullmatch(sender_num)

        pattern_paircode = re.compile(r'[a-zA-Z0-9]{8}')
        match_paircode = pattern_paircode.fullmatch(sms_paircode)

        pattern_mno = re.compile(r'[a-zA-Z0-9]{1,20}')
        match_mno = pattern_mno.fullmatch(mno)

        if match_sender_no and match_paircode and match_mno:
            chk_pc = Pairing_Codes.query.filter(Pairing_Codes.pair_code == '{}'.format(sms_paircode),
                                                Pairing_Codes.is_active == True).first()

            if chk_pc:

                chk_primary = Pairing.query.filter(Pairing.msisdn == '{}'.format(sender_num))\
                                           .filter(Pairing.is_primary == True)\
                                           .filter(Pairing.end_date == None).first()

                if not chk_primary:

                    max_pair_count = db.session.query(func.max(Pairing.id)).scalar()  # query to get maximum Pairing_id

                    if max_pair_count is None:
                        max_pair_count = 1

                    else:
                        max_pair_count += 1

                    chk_imei = Imei.query.filter(Imei.device_id == '{}'.format(chk_pc.device_id)).all()

                    for q in chk_imei:

                        first_add = Pairing(id=max_pair_count,   # Inserting Primary-Pair in pairing table
                                            primary_id=0,
                                            msisdn=sender_num,
                                            is_primary=True,
                                            creation_date=strftime("%Y-%m-%d %H:%M:%S"),
                                            operator_name=mno,
                                            add_pair_status=True,
                                            imei_id=q.id)

                        db.session.add(first_add)

                        max_pair_count += 1

                        db.session.commit()

                    chk_pc.is_active = False           # de-activating pair-code in PairCodes Table

                    db.session.commit()

                    return "PairCode ({}) is valid and your pair will be " \
                           "added in next 24 to 48 hours".format(sms_paircode), 200

                else:
                    return "MSISDN already exists as Primary-Pair", 422

            else:
                return "Pair Code ({}) is not Valid".format(sms_paircode), 422

        elif not match_sender_no:
            return "Sender MSISDN format is not correct", 422

        elif not match_paircode:
            return "Pair-Code format is not correct", 422

        elif not match_mno:
            return "MNO's name is not in correct format", 422

    except Exception as e:
        db.session.rollback()

    finally:
        db.session.close()
