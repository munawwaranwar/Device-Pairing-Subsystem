"""
Copyright (c) 2018-2021 Qualcomm Technologies, Inc.

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

from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from app.api.common.validations import Validations
from app.api.v1.resources.find_pairs import FindPairs
from app.api.v1.resources.first_pair import FirstPair
from app.api.v1.resources.sim_change import SimChange
from app.api.v2.schema.input_schema import USSDSchema
from app.api.v1.schema.input_schema import VfyPaircodeSchema
from app.api.assets.response import STATUS_CODES, MIME_TYPES
from app.api.assets.error_handlers import custom_text_response
from app.api.v1.resources.rel_all_pairs import ReleaseAllPairs
from app.api.v1.resources.verify_paircode import VerifyPairCode
from app.api.v1.resources.additional_pairs import AdditionalPairs
from app.api.v1.resources.rel_single_pair import ReleaseSinglePair


class DpsUssd(Resource):
    """Flask Resource to access and handle USSD parameters"""

    def get(self):
        kwargs = request.args
        try:
            USSDSchema().load(kwargs)
        except ValidationError as e:
            err = []
            for v in e.messages.values():
                err.append(v[0])

            return custom_text_response(err, status=STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                        mimetype=MIME_TYPES.get('TEXT'))

        ussd_case = kwargs['case']
        text = kwargs['msg_text'].split(',')

        if ussd_case == "first_pair":
            if len(text) > 2:
                pair_code = text[2]
                params = {"pair_code": pair_code, "sender_no": kwargs['sender_no'], "operator": kwargs['operator']}
                try:
                    Validations.validate_paircode(pair_code)
                except ValidationError as e:
                    return custom_text_response(e.messages[0], status=STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                                mimetype=MIME_TYPES.get('TEXT'))
                pp = FirstPair()
                result = pp.first_pair_creation(params)
                return result
            else:
                return "USSD does not contain pair-code"

        elif ussd_case == "additional_pair":
            rslt, params = self.params_validation(text, kwargs)
            if rslt: return rslt
            else:
                ap = AdditionalPairs()
                result = ap.sec_pair_creation(params)
                return result

        elif ussd_case == "del_single_pair":
            rslt, params = self.params_validation(text, kwargs)
            if rslt: return rslt
            else:
                dsp = ReleaseSinglePair()
                result = dsp.del_sngl_pair(params)

                return result

        elif ussd_case == "del_all_pairs":
            params = {"primary_msisdn": kwargs['sender_no']}
            dap = ReleaseAllPairs()
            result = dap.del_all_pairs(params)
            return result

        elif ussd_case == "sim_change":
            params = {"msisdn": kwargs['sender_no'], "operator": kwargs['operator']}
            sc = SimChange()
            result = sc.sim_change_mnp(params)
            return result

        elif ussd_case == "verify_pair":
            if len(text) > 3:
                pair_code, imei = text[2], text[3]
                params = {"pair_code": pair_code, "imei": imei}
                try:
                    VfyPaircodeSchema().load(params)
                except ValidationError as e:
                    err = []
                    if e.messages.get("imei"): err.append(e.messages.get("imei")[0])
                    if e.messages.get("pair_code"): err.append(e.messages.get("pair_code")[0])
                    return custom_text_response(err, status=STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                                mimetype=MIME_TYPES.get('TEXT'))
                vps = VerifyPairCode()
                result = vps.verify_pair_code(params)
                return result
            else:
                return "USSD does not provide all the required information"

        elif ussd_case == "find_pair":
            primary_msisdn = {"primary_msisdn": kwargs['sender_no']}

            fp = FindPairs()
            result = fp.find_pair_details(primary_msisdn)
            return result

        return "Case not found"

    @staticmethod
    def params_validation(text, kwargs):
        """method to validate the parameters send via SMS-Text"""

        if len(text) > 2:
            secondary_msisdn = text[2]
            params = {"primary_msisdn": kwargs['sender_no'], "secondary_msisdn": secondary_msisdn}
            try:
                Validations.validate_msisdn(secondary_msisdn)
            except ValidationError:
                return custom_text_response("Secondary MSISDN format is not correct",
                                            status=STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                            mimetype=MIME_TYPES.get('TEXT')), None
            else:
                return None, params
        else:
            return "USSD does not contain Secondary MSISDN", None
