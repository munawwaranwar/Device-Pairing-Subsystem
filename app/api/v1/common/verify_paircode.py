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

from app import db
from app.api.v1.models.pairing_codes import Pairing_Codes
from app.api.v1.models.imeis import Imei
import re


def vfy_paircode(pair_code, sms_imei):
    """ Function to verify if provided pair-code is active and related to that particular mobile device"""
    try:
        rtn_rcv = ""

        pattern_paircode = re.compile(r'[a-zA-Z0-9]{8}')
        match_paircode = pattern_paircode.fullmatch(pair_code)

        pattern_imei = re.compile(r'[A-F0-9]{14,16}')
        match_imei = pattern_imei.fullmatch(sms_imei)

        if match_paircode and match_imei:
            chk_pc = Pairing_Codes.query.filter(Pairing_Codes.pair_code == '{}'.format(pair_code),
                                                Pairing_Codes.is_active == True).first()

                                    # checking pair-code's validity

            if chk_pc:

                chk_imei = Imei.query.filter(Imei.imei == '{}'.format(sms_imei),
                                             Imei.device_id == '{}'.format(chk_pc.device_id)).all()

                                # verify that IMEI is related to that pair-code

                if chk_imei:
                    rtn_rcv = "Pair-Code ({}) is active & associated with provided IMEI".format(pair_code)
                else:
                    rtn_rcv = "Pair-Code ({}) is not valid or not associated with provided IMEI".format(pair_code)

            else:
                rtn_rcv = "Pair-Code ({}) is not valid or not associated with provided IMEI".format(pair_code)

            return rtn_rcv

        elif not match_imei:
            return "IMEI format is not correct"

        elif not match_paircode:
            return "Pair-Code format is not correct"

    except Exception as e:
       db.session.rollback()

    finally:
       db.session.close()
