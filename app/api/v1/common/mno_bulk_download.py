"""
DPS MNOs' Bulk-MSISDN Download package.
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

from app import db, conf, app
from app.api.v1.models.pairings import Pairing
import os
from time import strftime


def bulk_msisdns(mno):
    """ Function that leads to a method that provides MSISDNs for MNOs to provide IMSIs"""

    chk_mno = False

    for key, val in conf.items():  # checking valid MNOs
        if mno == val:
            chk_mno = True

    if chk_mno:
        c_path = mno_all_data(mno)

    else:
        rtn_msg = "wrong mno"
        return rtn_msg

    return c_path


def mno_all_data(mno):
    """ Method to provide actual file containing all MSISDNs for MNOs to provide IMSIs"""
    try:

        msisdn_list = []
        DOWNLOAD_FOLDER = app.config['DPS_DOWNLOADS']

        chk_imsi = Pairing.query.filter(Pairing.operator_name == '{}'.format(mno)) \
                                .filter(Pairing.imsi == None) \
                                .filter(Pairing.add_pair_status == True) \
                                .filter(Pairing.end_date == None).all()
                            # to check which MSISDNs require IMSI from MNO
        if chk_imsi:

            filename = "MSISDNs-List_" + mno + '_' + strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
            download_path = os.path.join(DOWNLOAD_FOLDER, filename)

            file = open(download_path, 'w')

            for c in chk_imsi:
                msisdn_list.append(c.msisdn)

            msisdn_list = set(msisdn_list)
            msisdn_list = list(msisdn_list)

            file.write('MSISDN,IMSI\n')

            for ml in msisdn_list:
                file.write(ml + ',\n')

            file.close()

            return download_path
            # send_from_directory(directory=path, filename=filename)

        else:
            return "No File found"

    except Exception as e:
        db.session.rollback()

    finally:
        db.session.close()
