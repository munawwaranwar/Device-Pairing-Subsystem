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
import json

import requests
from flask_babel import _
from time import strftime
from app import db, conf
from flask_restful import Resource
from flask_apispec import use_kwargs
from ..models.pairings import Pairing
from ..schema.input_schema import AdditionalPairSchema
from app.api.assets.error_handlers import custom_text_response
from app.api.assets.response import STATUS_CODES, MIME_TYPES
from app.api.common.jasmin_apis import JasminAPIs

# noinspection PyComparisonWithNone,PyUnboundLocalVariable,DuplicatedCode,PyUnusedLocal,PyUnresolvedReferences,PyTypeChecker
class AdditionalPairs(Resource):
    """Flask resource for creation of Secondary-Pairs."""

    @use_kwargs(AdditionalPairSchema().fields_dict, locations=['json'])
    def post(self, **kwargs):
        """method to call static-method to create secondary-pairs"""

        rst = self.sec_pair_creation(kwargs)
        return rst

    @staticmethod
    def sec_pair_creation(kwargs):
        """method to create additional/Secondary pair"""

        try:
            chk_primary = Pairing.query.filter(db.and_(Pairing.msisdn == '{}'.format(kwargs['primary_msisdn']),
                                                       Pairing.is_primary == True,
                                                       Pairing.end_date == None,
                                                       Pairing.msisdn != kwargs['secondary_msisdn'])).all()

            if chk_primary:
                chk_1 = True
                for q in chk_primary:

                    chk_sec = Pairing.query.filter(Pairing.primary_id == '{}'.format(q.id)) \
                        .filter(Pairing.end_date == None).all()

                    if chk_sec:

                        for r in chk_sec:

                            if r.msisdn != kwargs['secondary_msisdn']:     # checking if MSISDN is already paired or not
                                chk_2 = True

                                if len(chk_sec) < conf['pair_limit']:      # checking if pair-limit is exceeded or not
                                    chk_3 = True

                                else:
                                    chk_3 = False
                                    return custom_text_response(_("Pairing limit breached: remove any existing pair first"),
                                                                status=STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                                                mimetype=MIME_TYPES.get('TEXT'))

                            else:
                                chk_2 = False
                                return custom_text_response(_("MSISDN %(msisdn)s already paired with the device",
                                                            msisdn=kwargs['secondary_msisdn']),
                                                            status=STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                                            mimetype=MIME_TYPES.get('TEXT'))

                        if chk_1 and chk_2 and chk_3:

                            adding1 = Pairing(primary_id=q.id,
                                              msisdn=kwargs['secondary_msisdn'],
                                              is_primary=False,
                                              creation_date=strftime("%Y-%m-%d %H:%M:%S"),
                                              add_pair_status=False,
                                              imei_id=q.imei_id)

                            # adding secondary pair in case one or more secondary pairs already exists

                            db.session.add(adding1)
                            db.session.flush()
                            db.session.commit()

                            cnfm_sms = True

                            rtn_msg = _("Secondary pair is added by %(primary)s. Confirmation is awaited from %(sec)s",
                                        primary=kwargs['primary_msisdn'], sec=kwargs['secondary_msisdn'])

                    else:
                        adding2 = Pairing(primary_id=q.id,
                                          msisdn=kwargs['secondary_msisdn'],
                                          is_primary=False,
                                          creation_date=strftime("%Y-%m-%d %H:%M:%S"),
                                          add_pair_status=False,
                                          imei_id=q.imei_id)    # adding secondary pair for first time

                        db.session.add(adding2)
                        db.session.flush()
                        db.session.commit()

                        cnfm_sms = True

                        rtn_msg = _("Secondary pair is added by %(primary)s. Confirmation is awaited from %(sec)s",
                                    primary=kwargs['primary_msisdn'], sec=kwargs['secondary_msisdn'])

            else:

                chk_1 = False

                return custom_text_response(_("Request not made by Primary-Pair or number-to-be-added is Primary number"),
                                            status=STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                            mimetype=MIME_TYPES.get('TEXT'))

            if cnfm_sms:

                """ ****************** Kannel-Block replaced with Jasmin ******************
                chg_msisdn = '0' + kwargs['secondary_msisdn'][2:]

                message = "CONFIRM [{}]\nPlease reply with Yes/No space {}".format(kwargs['primary_msisdn'],
                                                                                   kwargs['primary_msisdn'])

                payload = {'username': conf['kannel_username'], 'password': conf['kannel_password'],
                           'smsc': conf['kannel_smsc'], 'from': conf['kannel_shortcode'], 'to': chg_msisdn,
                           'text': message}

                # requests.get(conf['kannel_sms'], params=payload)
                """

                message = "CONFIRM [{}]\nPlease reply with Yes/No space {}".format(kwargs['primary_msisdn'],
                                                                                   kwargs['primary_msisdn'])
                response = JasminAPIs.jasmin_sms(kwargs['secondary_msisdn'], conf['kannel_shortcode'], message)

                cnfm_sms = False        # pragma: no cover

            return custom_text_response(rtn_msg, status=STATUS_CODES.get('OK'),
                                        mimetype=MIME_TYPES.get('TEXT'))

        except Exception as e:
            db.session.rollback()            # pragma: no cover

        finally:
            db.session.close()
