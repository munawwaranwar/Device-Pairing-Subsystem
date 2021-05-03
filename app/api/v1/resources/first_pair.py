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

from app import db
from flask_babel import _
from time import strftime
from ..models.imeis import Imei
from flask_restful import Resource
from flask_apispec import use_kwargs
from ..models.pairings import Pairing
from ..models.pairing_codes import Pairing_Codes
from ..schema.input_schema import FirstPairSchema
from app.api.assets.response import STATUS_CODES, MIME_TYPES
from app.api.assets.error_handlers import custom_text_response


# noinspection PyComparisonWithNone,PyBroadException,PyUnusedLocal
class FirstPair(Resource):
    """Flask resource for creation of First-Pair."""

    @use_kwargs(FirstPairSchema().fields_dict, locations=['json'])
    def post(self, **kwargs):
        """method to call static-method to create primary-pairs"""

        rst = self.first_pair_creation(kwargs)
        return rst

    @staticmethod
    def first_pair_creation(kwargs):
        """method to create primary/first pair"""

        try:
            chk_pc = Pairing_Codes.query.filter(Pairing_Codes.pair_code == '{}'.format(kwargs['pair_code']),
                                                Pairing_Codes.is_active == True).first()

            if chk_pc:

                chk_primary = Pairing.query.filter(Pairing.msisdn == '{}'.format(kwargs['sender_no'])) \
                                           .filter(Pairing.is_primary == True) \
                                           .filter(Pairing.end_date == None).first()

                if not chk_primary:
                    chk_imei = Imei.query.filter(Imei.device_id == '{}'.format(chk_pc.device_id)).all()

                    for q in chk_imei:

                        first_add = Pairing(primary_id=0,           # Inserting Primary-Pair in pairing table
                                            msisdn=kwargs['sender_no'],
                                            is_primary=True,
                                            creation_date=strftime("%Y-%m-%d %H:%M:%S"),
                                            operator_name=kwargs['operator'],
                                            add_pair_status=True,
                                            imei_id=q.id)

                        db.session.add(first_add)
                        db.session.flush()

                    chk_pc.is_active = False  # de-activating pair-code in PairCodes Table
                    db.session.flush()
                    db.session.commit()

                    return custom_text_response(_("PairCode %(v1)s is valid and your pair will be added in next 24 to "
                                                  "48 hours", v1=kwargs['pair_code']),
                                                status=STATUS_CODES.get('OK'),
                                                mimetype=MIME_TYPES.get('TEXT'))
                else:
                    return custom_text_response(_("MSISDN already exists as Primary-Pair"),
                                                status=STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                                mimetype=MIME_TYPES.get('TEXT'))
            else:
                return custom_text_response(_("Pair Code %(pc)s is not Valid", pc=kwargs['pair_code']),
                                            status=STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                            mimetype=MIME_TYPES.get('TEXT'))

        except Exception as e:
            db.session.rollback()        # pragma: no cover

        finally:
            db.session.close()
