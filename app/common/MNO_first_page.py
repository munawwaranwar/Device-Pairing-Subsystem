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

import string
import re
from random import choice
from app.Models.pairings import Pairing
from app import conf, db
from app.views.Pagination import Pagination


def fetch_msisdns(mno,st,lt):
    """ Function leads to method that fetches MSISDNs for MNOs """

    try:
        cases = []
        chk_mno = False

        pattern_start_limit = re.compile(r'\d+')

        match_start = pattern_start_limit.fullmatch(st)
        match_limit = pattern_start_limit.fullmatch(lt)

        if (match_start and match_limit):

            start = int(st)
            limit = int(lt)

            for key,val in conf.items():
                if mno == val:
                    chk_mno = True

            if chk_mno == True:
                cases = mno_records(mno, start, limit)
            else:
                data = {
                        "Error": "improper Operator's name provided"
                       }
                return data, 422

            return cases

        else:
            data = {
                     "Error": "Start or limit is not correct"
                   }
            return data, 422


    except Exception as e:

        db.session.rollback()

    finally:
        db.session.close()

def mno_records(mno,start,limit):
    """ Function to fetch MSISDNs from database which need IMSIs from MNO and provide paginated view to MNO's portal """

    try:
        mno_info = []
        msisdn_list = []

        chk_imsi = Pairing.query.filter(Pairing.operator_name == '{}'.format(mno)) \
                                .filter(Pairing.imsi == None) \
                                .filter(Pairing.add_pair_status == True) \
                                .filter(Pairing.end_date == None).all()

        if chk_imsi:

            for c in chk_imsi:
                msisdn_list.append(c.msisdn)

            msisdn_list = set(msisdn_list)
            msisdn_list = list(msisdn_list)

            for r in msisdn_list:
                a = gen_req_id()
                data = {
                    "Req_id": a,
                    "MSISDN": r
                }
                mno_info.append(data)

            if mno_info:
                paginated_data = Pagination.get_paginated_list(mno_info,'/get-pairs',start = start,limit = limit)

                if paginated_data:
                    return paginated_data, 200
                else:
                    data = {
                            "msg": "no data found"
                           }
                    return data, 200

        else:
            data = {
                "msg" : "no record found"
            }

            return data, 200

    except Exception as e:
        db.session.rollback()

    finally:
        db.session.close()


def gen_req_id():

    all_char = string.ascii_letters + string.digits

    req_id = "".join(choice(all_char) for x in range(8))

    return req_id
