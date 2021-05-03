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


from app import db, conf
from time import strftime
from flask_babel import _
from flask_restful import Resource
from flask_apispec import use_kwargs
from ..models.pairings import Pairing
from app.api.common.jasmin_apis import JasminAPIs
from ..schema.input_schema import AddPairConfirmSchema
from app.api.assets.response import STATUS_CODES, MIME_TYPES
from app.api.assets.error_handlers import custom_text_response


# noinspection PyComparisonWithNone,PyUnusedLocal
class AdditionalPairsConfirmation(Resource):
    """Flask resource for creation of Secondary-Pairs."""

    @staticmethod
    @use_kwargs(AddPairConfirmSchema().fields_dict, locations=['json'])
    def post(**kwargs):
        """method to create Secondary/Additional pairs confirmation"""

        try:
            rtn_msg = ""
            cnfm_sms = False

            chk_primary = Pairing.query.filter(Pairing.msisdn == '{}'.format(kwargs['primary_msisdn'])) \
                                       .filter(Pairing.is_primary == True) \
                                       .filter(Pairing.end_date == None).all()

            if chk_primary:

                for q in chk_primary:

                    if kwargs['confirm'] in ["NO", "no", "No"]:

                        othr_chks = Pairing.query.filter(Pairing.msisdn == '{}'.format(kwargs['secondary_msisdn']),
                                                         Pairing.is_primary == False,
                                                         Pairing.primary_id == '{}'.format(q.id),
                                                         Pairing.end_date == None,
                                                         Pairing.add_pair_status == False).first()

                        if othr_chks:

                            db.session.delete(othr_chks)
                            db.session.commit()
                            rtn_msg = _("Request of additional pair is rejected by %(sec)s",
                                        sec=kwargs['secondary_msisdn'])

                            cnfm_sms = True

                        else:

                            rtn_msg = _("Confirmation of additional pair request is not done by valid MSISDN")

                    elif kwargs['confirm'] in ["YES", "Yes", "yes"]:

                        othr_chks = Pairing.query.filter(db.and_(Pairing.msisdn == '{}'.
                                                                 format(kwargs['secondary_msisdn']),
                                                                 Pairing.is_primary == False,
                                                                 Pairing.primary_id == '{}'.format(q.id),
                                                                 Pairing.end_date == None,
                                                                 Pairing.add_pair_status == False)).first()

                        if othr_chks:

                            othr_chks.add_pair_status = True
                            othr_chks.operator_name = kwargs['operator']
                            othr_chks.updated_at = '{}'.format(strftime("%Y-%m-%d %H:%M:%S"))
                            db.session.commit()

                            rtn_msg = _("Request of additional pair from %(prim)s is accepted by %(sec)s",
                                        prim=kwargs['primary_msisdn'], sec=kwargs['secondary_msisdn'])

                            cnfm_sms = True

                        else:

                            rtn_msg = _("Confirmation of additional pair request is not done by valid MSISDN")

            else:
                rtn_msg = _("Wrong Primary number mentioned in SMS")

            if cnfm_sms:

                """ ****************** Kannel-Block replaced with Jasmin ******************
                chg_msisdn = '0' + kwargs['primary_msisdn'][2:]

                payload = {'username': conf['kannel_username'], 'password': conf['kannel_password'],
                           'smsc': conf['kannel_smsc'], 'from': conf['kannel_shortcode'], 'to': chg_msisdn,
                           'text': rtn_msg}

                requests.get(conf['kannel_sms'], params=payload)
                """

                response = JasminAPIs.jasmin_sms(kwargs['secondary_msisdn'], conf['kannel_shortcode'],
                                                 rtn_msg, kwargs['operator'])

                cnfm_sms = False

            return custom_text_response(rtn_msg, status=STATUS_CODES.get('OK'), mimetype=MIME_TYPES.get('TEXT'))

        except Exception as e:
            db.session.rollback()       # pragma: no cover

        finally:
            db.session.close()
