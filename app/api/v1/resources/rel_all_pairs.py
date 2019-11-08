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
from ..assets.response import *
from ..models.imeis import Imei
from ..models.pairings import Pairing
from ..models.pairing_codes import Pairing_Codes
from ..common.generate_paircode import gen_paircode
from ..schema.input_schema import RelAllPairsSchema
from ..assets.error_handlers import custom_text_response


# noinspection PyUnboundLocalVariable,PyUnusedLocal
class ReleaseAllPairs(Resource):
    """Flask resource to delete All-Pairs."""

    @staticmethod
    @use_kwargs(RelAllPairsSchema().fields_dict, locations=['json'])
    def delete(**kwargs):
        """method to delete/release All-Pairs"""

        try:
            rtn_msg = ""
            rel_all_cond = 3
            chk_primary = Pairing.query.filter(db.and_(Pairing.msisdn == '{}'.format(kwargs['primary_msisdn']),
                                                       Pairing.is_primary == True)).all()
            # checking if request is originated from primary-pair

            if chk_primary:

                for q1 in chk_primary:

                    if q1.end_date is None:
                        rel_all_cond = 1
                        q1.end_date = '{}'.format(strftime("%Y-%m-%d"))

                        if q1.imsi is not None and q1.add_pair_status and q1.change_type == 'add' \
                                and q1.export_status is True:

                            # Condition checks only those pairs be exported as "removed" in pair-list
                            # which are added and already exported to DIRBS-CORE before removing

                            q1.export_status = False
                            q1.change_type = 'remove'

                        elif q1.export_status is False and (q1.change_type is None or q1.change_type == 'add'):

                            # Condition to avoid exporting this pair to DIRBS-CORE

                            q1.export_status = None  # pragma: no cover
                            q1.change_type = None  # pragma: no cover
                            q1.old_imsi = None  # pragma: no cover

                        elif q1.imsi is None and q1.export_status is None \
                                and q1.change_type is None and q1.old_imsi is not None:

                            # Condition for case where pair(s) is exported once and after that SIM-Change is requested
                            # but before MNO provides new IMSI, Pair is deleted.

                            q1.export_status = False
                            q1.change_type = "remove"
                            q1.imsi = q1.old_imsi
                            q1.old_imsi = None

                        db.session.commit()

                        chk_sec_pairs = Pairing.query.filter(Pairing.primary_id == q1.id).all()
                        # checking if secondary pairs exist under primary

                        if chk_sec_pairs:

                            for q2 in chk_sec_pairs:

                                if q2.imsi is not None and q2.add_pair_status and q2.change_type == 'add' \
                                        and q2.export_status and q2.end_date is None:

                                    # Condition checks only those pairs be exported as "removed" in pair-list
                                    # which are added and already exported to DIRBS-CORE before removing

                                    q2.export_status = False
                                    q2.change_type = 'remove'

                                elif q2.export_status is False and (q2.change_type is None or q2.change_type == 'add'):

                                    # Condition to avoid exporting this pair to DIRBS-CORE

                                    q2.export_status = None  # pragma: no cover
                                    q2.change_type = None  # pragma: no cover
                                    q2.old_imsi = None  # pragma: no cover

                                elif q2.imsi is None and q2.export_status is None \
                                        and q2.change_type is None and q2.old_imsi is not None:

                                    # Condition for case where pair(s) is exported once and after that SIM-Change is
                                    # requested but before MNO provides new IMSI, Pair is deleted.

                                    q2.export_status = False
                                    q2.change_type = "remove"
                                    q2.imsi = q2.old_imsi
                                    q2.old_imsi = None

                                q2.end_date = '{}'.format(strftime("%Y-%m-%d"))

                                db.session.commit()

                    else:

                        rel_all_cond = 2

            else:

                rel_all_cond = 3

            if rel_all_cond == 1:

                paircode = gen_paircode()  # generating new pair-code & assigning it to the particular mobile device

                chk_dev_id = Imei.query.filter(Imei.id == q1.imei_id).first()

                add_pc = Pairing_Codes(pair_code=paircode,
                                       is_active=True,
                                       device_id=chk_dev_id.device_id)

                db.session.add(add_pc)
                db.session.commit()

                rtn_msg = _("Release All-Pairs request is registered. New Pair Code is %(pc)s", pc=paircode)

            elif rel_all_cond == 2:

                chk_dev_id = Imei.query.filter(Imei.id == q1.imei_id).first()

                chk_paircode = Pairing_Codes.query.filter(Pairing_Codes.device_id == chk_dev_id.device_id,
                                                          Pairing_Codes.is_active == True).first()

                rtn_msg = _("Your new Pair-Code is %(pc)s. Release-All request is already registered and will be implemented within 24-48 hours",
                            pc=chk_paircode.pair_code)

            elif rel_all_cond == 3:

                rtn_msg = _("Release-All request not made by Primary-MSISDN")

            return custom_text_response(rtn_msg, status=STATUS_CODES.get('OK'), mimetype=MIME_TYPES.get('TEXT'))

        except Exception as e:
            db.session.rollback()           # pragma: no cover

        finally:
            db.session.close()
