"""
DPS MNO's Single-IMSI upload package.
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

from app.api.v1.models.pairings import Pairing
from app import db
from time import strftime
import re
from app import conf
from flask_babel import lazy_gettext as _


def sngl_imsi(mno, msisdn, imsi):
    """ Function that provide method to upload single IMSI against provided MSISDN """
    try:

        rtn_msg = ""
        cases = ""
        chk_mno, chk_msisdn = False, False

        if msisdn['CC'] == conf['CC']:
            if msisdn['SN'].isdigit() and len(msisdn['SN']) < 13:
                f_msisdn = msisdn['CC'] + msisdn['SN']
                chk_msisdn = True

        pattern_imsi = re.compile(r'\d{15}')
        match_imsi = pattern_imsi.fullmatch(imsi)

        if chk_msisdn and match_imsi:

            for key, val in conf.items():
                if mno == val:
                    chk_mno = True

            if chk_mno:
                chk_imsi = Pairing.query.filter(Pairing.imsi == '{}'.format(imsi)).first()

                if chk_imsi:
                    data = {
                        "Error": _("IMSI already exists")
                    }
                    return data, 422
                else:
                    cases = sngl_imsi_update(mno, f_msisdn, imsi)
            else:
                data = {
                        "Error": _("Improper Operator-Name provided")
                       }
                return data, 422
            data = {
                     "msg": cases
                   }
            if cases == 'IMSI added successfully':
                return data, 200
            else:
                return data, 422

        elif not chk_msisdn:
            rtn_msg = {
                        "Error": _("MSISDN format is not correct")
                      }
            return rtn_msg, 422

        elif not match_imsi:
            rtn_msg = {
                        "Error": _("IMSI format is not correct")
                      }
            return rtn_msg, 422

    except Exception as e:
        db.session.rollback()

    finally:
        db.session.close()


def sngl_imsi_update(mno, msisdn, imsi):
    """ Method to upload Single-IMSI against provided MSISDN """

    try:
        chk_msisdn = Pairing.query.filter(Pairing.operator_name == '{}'.format(mno),
                                          Pairing.msisdn == '{}'.format(msisdn),
                                          Pairing.imsi == None,
                                          Pairing.add_pair_status == True,
                                          Pairing.end_date == None).all()
                        # checking criteria for MSISDN to get IMSI
        if chk_msisdn:

            for m in chk_msisdn:
                m.imsi = imsi
                m.updated_at = strftime("%Y-%m-%d %H:%M:%S")
                m.change_type = 'ADD'
                m.export_status = False
            db.session.commit()
            rtn_msg = _("IMSI added successfully")

        else:
            rtn_msg = _("IMSI addition Failed")

        return rtn_msg

    except Exception as e:
        db.session.rollback()

    finally:
        db.session.close()
