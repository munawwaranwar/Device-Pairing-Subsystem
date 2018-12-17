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

from app.api.v1.views.pagination import Pagination
from app import db, conf
import re


class Search_authority:
    """ Class to provide search methods for authority to find registered devices  """

    def authority_search(startt, limit, data, para_cnt, para_exists):
        """ Method to search registered devices """

        try:

            chk_mac, chk_serial, chk_contact, chk_imei = False, False, False, False
            fst = False

            if para_exists['mac_exist']:
                if data['MAC'] is not None:
                    if type(data['MAC']) is str:
                        mac_pat_1 = re.compile(r'[A-Za-z0-9:.-]{0,200}')
                        mac_match1 = mac_pat_1.fullmatch(data['MAC'])

                        if mac_match1:
                            chk_mac = True
            else:
                chk_mac = True

            if para_exists['serial_exist']:
                if data['Serial_No'] is not None:
                    if type(data['Serial_No']) is str:
                        pattern_serial_no = re.compile(r'[a-zA-Z0-9]{0,1000}')
                        match_serial = pattern_serial_no.fullmatch(data['Serial_No'])
                        if match_serial:
                            chk_serial = True
            else:
                chk_serial = True

            if para_exists['contact_exist']:
                if data['CONTACT'] is not None:
                    if type(data['CONTACT']) is str:
                        pattern_contact = re.compile(r'\d{0,200}')
                        match_contact = pattern_contact.fullmatch(data['CONTACT'])
                        if match_contact:
                            chk_contact = True
            else:
                chk_contact = True

            if para_exists['imei_exist']:
                if data['IMEI'] is not None:
                    if type(data['IMEI']) is str:
                        pattern_imei = re.compile(r'[A-Za-z0-9]{0,200}')
                        match_imei = pattern_imei.fullmatch(data['IMEI'])
                        if match_imei:
                            chk_imei = True
            else:
                chk_imei = True

            if (type(startt) is int and type(limit) is int and chk_mac and chk_serial
                    and chk_contact and chk_imei):

                qry = "select contact, brand, model, serial_no, string_agg(imei,',') as imei, mac, " \
                      "pair_code, is_active " \
                      "from test_view where "

                if para_cnt > 0:

                    for p in data:
                                                            # building the database query
                        if p == "IMEI" and not fst:
                            qry = qry + """{} = '{}' """.format(p, (data.get(p)))
                            fst = True
                        elif p == "IMEI" and fst:
                            qry = qry + """ and {} = '{}' """.format(p, (data.get(p)))
                        elif p == "Serial_No" and not fst:
                            qry = qry + """{} = '{}' """.format(p, (data.get(p)))
                            fst = True
                        elif p == "Serial_No" and fst:
                            qry = qry + """ and {} = '{}' """.format(p, (data.get(p)))
                        elif p == "MAC" and not fst:
                            qry = qry + """{} = '{}' """.format(p, (data.get(p)))
                            fst = True
                        elif p == "MAC" and fst:
                            qry = qry + """ and {} = '{}' """.format(p, (data.get(p)))
                        elif p == "CONTACT" and not fst:
                            qry = qry + """{} = '{}' """.format(p, (data.get(p)))
                            fst = True
                        elif p == "CONTACT" and fst:
                            qry = qry + """ and {} = '{}' """.format(p, (data.get(p)))

                    qry = qry + " group by serial_no, mac,contact, brand, model, pair_code, is_active; "
                    rslt = db.engine.execute(qry)
                    cases = []

                    for rows in rslt:
                        cases.append(dict((a, b) for a, b in rows.items()))

                    if cases:
                        paginated_data = Pagination.get_paginated_list(cases, '/authority-search', start=startt,
                                                                       limit=limit)
                        return paginated_data, 200

                    else:
                        data = {
                            "start": startt,
                            "previous": "",
                            "next": "",
                            "cases": cases,
                            "count": 0,
                            "Country_Code": conf['CC'],
                            "limit": limit
                        }

                        return data, 200

                else:
                    data = {
                        "start": startt,
                        "previous": "",
                        "next": "",
                        "cases": [],
                        "count": 0,
                        "Country_Code": conf['CC'],
                        "limit": limit
                    }

                    return data, 200

            elif not chk_mac:

                rtn_msg = {
                            "Error": "MAC format is not correct"
                          }
                return rtn_msg, 422

            elif not chk_serial:

                rtn_msg = {
                            "Error": "Serial-Number format is not correct"
                          }
                return rtn_msg, 422

            elif not chk_contact:

                rtn_msg = {
                            "Error": "Contact-MSISDN format is not correct"
                          }
                return rtn_msg, 422

            elif not chk_imei:

                rtn_msg = {
                            "Error": "IMEI format is not correct"
                          }
                return rtn_msg, 422

            elif type(startt) is not int or type(limit) is not int:

                rtn_msg = {
                            "Error": "Start or Limit is not integer"
                          }
                return rtn_msg, 422

        except Exception as e:
            db.session.rollback()

        finally:
            db.session.close()
