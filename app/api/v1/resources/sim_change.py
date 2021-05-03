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
from flask_restful import Resource
from flask_apispec import use_kwargs
from ..models.pairings import Pairing
from ..schema.input_schema import SimChangeSchema
from app.api.assets.response import STATUS_CODES, MIME_TYPES
from app.api.assets.error_handlers import custom_text_response


# noinspection PyUnusedLocal,PyComparisonWithNone
class SimChange(Resource):
    """Flask resource to delete IMSI for SIM replacement."""

    @use_kwargs(SimChangeSchema().fields_dict, locations=['json'])
    def delete(self, **kwargs):
        """method to initiate SIM-Change/MNP process"""

        rst = self.sim_change_mnp(kwargs)
        return rst

    @staticmethod
    def sim_change_mnp(kwargs):
        """method to delete IMSI for SIM replacement"""

        try:
            chk_all = Pairing.query.filter(Pairing.msisdn == '{}'.format(kwargs['msisdn'])) \
                                   .filter(Pairing.end_date == None) \
                                   .filter(Pairing.imsi != None) \
                                   .filter(Pairing.add_pair_status == True).all()

            # checking conditions for SIM replacement
            if chk_all:

                for q in chk_all:

                    if q.export_status is True:

                        q.old_imsi = q.imsi
                        q.imsi = None
                        q.export_status = None
                        q.change_type = None
                        q.operator_name = '{}'.format(kwargs['operator'])
                        db.session.commit()

                    else:
                        q.imsi = None
                        q.export_status = None
                        q.change_type = None
                        q.operator_name = '{}'.format(kwargs['operator'])
                        db.session.commit()

                return custom_text_response(_("SIM Change request has been registered. The Pair will be active in 24 to 48 hours"),
                                            status=STATUS_CODES.get('OK'),
                                            mimetype=MIME_TYPES.get('TEXT'))
            else:
                return custom_text_response(_("MSISDN %(ms)s is not existed in any pair or SIM-Change request is already in process",
                                              ms=kwargs['msisdn']),
                                            status=STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                            mimetype=MIME_TYPES.get('TEXT'))

        except Exception as e:
            db.session.rollback()       # pragma: no cover

        finally:
            db.session.close()
