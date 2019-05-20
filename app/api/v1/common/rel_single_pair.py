"""
DPS Single-Pair Deletion package.
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
from app import db
from app.api.v1.models.pairings import Pairing
import re


def rel_single(del_msisdn, sender_no):
    """ Function to remove secondary/additonal pairs """

    try:
        rtn_msg = ""

        pattern_msisdn = re.compile(r'923\d{9,12}')
        match_primary = pattern_msisdn.fullmatch(sender_no)
        match_secondary = pattern_msisdn.fullmatch(del_msisdn)

        if match_primary and match_secondary:
            chk_primary = Pairing.query.filter(Pairing.msisdn == '{}'.format(sender_no),
                                               Pairing.is_primary == True,Pairing.end_date == None,
                                               Pairing.msisdn != del_msisdn).all()

                                        # checking primary and checking deletion request is not for Primary-Pair

            if chk_primary:

                for p in chk_primary:

                    num_exist = Pairing.query.filter(Pairing.msisdn == '{}'.format(del_msisdn),
                                                     Pairing.end_date == None,
                                                     Pairing.primary_id == p.id).first()

                    # checking the condition whether, to-be-deleted MSISDN is paired with Primary, or not"

                    if num_exist:

                        num_exist.end_date = strftime("%Y-%m-%d")

                        if num_exist.imsi is not None and num_exist.add_pair_status:
                            num_exist.change_type = 'REMOVE'
                            num_exist.export_status = False

                        db.session.commit()

                        rtn_msg = "Deletion request is successfully registered. " \
                                  "Pair will be removed in next 24 to 48 hours"

                    else:

                        rtn_msg = "MSISDN ({}) is not Paired with the device".format(del_msisdn)

            else:

                rtn_msg = "Request is not made by Primary-MSISDN or number-to-be-deleted belongs to primary pair"

            return rtn_msg

        elif not match_primary:
            return "Primary MSISDN format is not correct"

        elif not match_secondary:
            return "Secondary MSISDN format is not correct"

    except Exception as e:
        db.session.rollback()

    finally:
        db.session.close()
