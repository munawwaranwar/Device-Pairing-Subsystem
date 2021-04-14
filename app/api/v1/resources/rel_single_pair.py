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
from flask_babel import _
from time import strftime
from flask_restful import Resource
from flask_apispec import use_kwargs
from ..models.pairings import Pairing
from ..schema.input_schema import AdditionalPairSchema
from app.api.assets.error_handlers import custom_text_response
from app.api.assets.response import STATUS_CODES, MIME_TYPES


# noinspection PyComparisonWithNone,PyUnusedLocal,DuplicatedCode
class ReleaseSinglePair(Resource):
    """Flask resource to delete Single-Pair."""

    @use_kwargs(AdditionalPairSchema().fields_dict, locations=['json'])
    def delete(self, **kwargs):
        """method to call static-method to delete/release a single pair"""

        rst = self.del_sngl_pair(kwargs)
        return rst

    @staticmethod
    def del_sngl_pair(kwargs):
        """method to delete/release a single pair"""

        try:
            rtn_msg = ""
            chk_primary = Pairing.query.filter(Pairing.msisdn == '{}'.format(kwargs['primary_msisdn']),
                                               Pairing.is_primary == True, Pairing.end_date == None,
                                               Pairing.msisdn != kwargs['secondary_msisdn']).all()

                    # checking primary and checking deletion request is not for Primary-Pair

            if chk_primary:

                for p in chk_primary:

                    num_exist = Pairing.query.filter(Pairing.msisdn == '{}'.format(kwargs['secondary_msisdn']),
                                                     Pairing.end_date == None,
                                                     Pairing.primary_id == p.id).first()

                    # checking whether, to-be-deleted MSISDN is paired with Primary, or not"

                    if num_exist:

                        num_exist.end_date = strftime("%Y-%m-%d")

                        if num_exist.imsi is not None and num_exist.add_pair_status \
                                and num_exist.change_type == 'add' and num_exist.export_status == True:

                            # Condition checks only those pairs be exported as "removed" in pair-list
                            # which are added and already exported to DIRBS-CORE before removing

                            num_exist.export_status = False
                            num_exist.change_type = 'remove'

                        elif num_exist.export_status is False and \
                                (num_exist.change_type is None or num_exist.change_type == 'add'):

                            # Condition to avoid exporting this pair to DIRBS-CORE

                            num_exist.export_status = None
                            num_exist.change_type = None
                            num_exist.old_imsi = None

                        elif num_exist.imsi is None and num_exist.export_status is None \
                                and num_exist.change_type is None and num_exist.old_imsi is not None:

                            # Condition for case where pair(s) is exported once and after that SIM-Change is requested
                            # but before MNO provides new IMSI, Pair is deleted.

                            num_exist.export_status = False
                            num_exist.change_type = "remove"
                            num_exist.imsi = num_exist.old_imsi
                            num_exist.old_imsi = None

                        db.session.commit()

                        rtn_msg = (_("Deletion request is successful. Pair will be removed in next 24 to 48 hours"))
                    else:

                        rtn_msg = _("MSISDN %(sec)s is not Paired with the device", sec=kwargs['secondary_msisdn'])
            else:
                rtn_msg = _("Request is not made by Primary-MSISDN or number-to-be-deleted belongs to primary pair")

            return custom_text_response(rtn_msg, status=STATUS_CODES.get('OK'), mimetype=MIME_TYPES.get('TEXT'))

        except Exception as e:
            db.session.rollback()      # pragma: no cover

        finally:
            db.session.close()
