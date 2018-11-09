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
from app.common.generate_PairCode import gen_paircode
from app.Models.pairing_codes import Pairing_Codes
from app.Models.imeis import Imei
from app.Models.pairings import Pairing
from app import db
import re


def rel_all(sender_no):
    """ Function to remove all pairs simultaneously including the primary pair """
    try:
        rtn_msg = ""
        rel_all_cond = 3

        pattern_msisdn = re.compile(r'923\d{9,12}')
        match_primary = pattern_msisdn.fullmatch(sender_no)

        if match_primary:

            chk_primary = Pairing.query.filter(db.and_(Pairing.msisdn == '{}'.format(sender_no),
                                               Pairing.is_primary == True)).all()

                                    # checking if request is originated from primary-pair
            if chk_primary:

                for q1 in chk_primary:

                    if q1.end_date == None:

                        rel_all_cond = 1

                        q1.end_date = '{}'.format(strftime("%Y-%m-%d"))

                        if q1.imsi != None and q1.add_pair_status == True:

                            q1.change_type = 'REMOVE'
                            q1.export_status = False

                        db.session.commit()

                        chk_sec_pairs = Pairing.query.filter(Pairing.primary_id == q1.id).all()
                                            # checking if secondary pairs exist under primary
                        if chk_sec_pairs:

                            for q2 in chk_sec_pairs:

                                q2.end_date = '{}'.format(strftime("%Y-%m-%d"))

                                if q2.imsi != None and q2.add_pair_status == True:
                                    q2.change_type = 'REMOVE'
                                    q2.export_status = False

                                db.session.commit()

                    else:

                        rel_all_cond = 2

            else:

                rel_all_cond = 3

            if rel_all_cond == 1:

                paircode = gen_paircode()       # generating new pair-code & assigning it to the particular mobile device

                chk_dev_id = Imei.query.filter(Imei.id == q1.imei_id).first()

                add_pc = Pairing_Codes(pair_code = paircode,
                                       is_active = True,
                                       device_id = chk_dev_id.device_id)

                db.session.add(add_pc)
                db.session.commit()

                rtn_msg = "Release All-Pairs request is registered. New Pair Code is ({})".format(paircode)

            elif rel_all_cond == 2:

                chk_dev_id = Imei.query.filter(Imei.id == q1.imei_id).first()

                chk_paircode = Pairing_Codes.query.filter(Pairing_Codes.device_id == chk_dev_id.device_id,
                                                          Pairing_Codes.is_active == True).first()

                rtn_msg = "Your new Pair-Code is ({}). " \
                          "Release-All request is already registered and will be implemented within 24-48 hours"\
                          .format(chk_paircode.pair_code)

            elif rel_all_cond == 3:

                rtn_msg = "Release-All request not made by Primary-MSISDN"

            return rtn_msg

        elif not match_primary:
            return "Primary MSISDN format is not correct"

    except Exception as e:
        db.session.rollback()

    finally:
        db.session.close()
