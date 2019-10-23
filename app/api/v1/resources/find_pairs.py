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
from flask_restful import Resource
from flask_apispec import use_kwargs
from ..assets.response import *
from ..models.pairings import Pairing
from ..schema.input_schema import RelAllPairsSchema
from ..assets.error_handlers import custom_text_response


# noinspection PyComparisonWithNone,PyUnusedLocal
class FindPairs(Resource):
    """Flask resource to find secondary-pairs."""

    @staticmethod
    @use_kwargs(RelAllPairsSchema().fields_dict, locations=['querystring'])
    def get(**kwargs):
        """method to find secondary-pairs"""

        try:

            pair_info = []
            status_list = []
            msisdn_list = []

            chk_primary = Pairing.query.filter(Pairing.msisdn == '{}'.format(kwargs['primary_msisdn']),
                                               Pairing.is_primary == True,
                                               Pairing.end_date == None).first()

            # to check if request is made from primary-pair

            if chk_primary:

                chk_sec = Pairing.query.filter(Pairing.primary_id == '{}'.format(chk_primary.id),
                                               Pairing.end_date == None).all()

                for m in chk_sec:

                    msisdn_list.append(m.msisdn)

                    if m.add_pair_status:
                        status_list.append('Confirmed Pair')

                    else:
                        status_list.append('Un-confirmed Pair')

                for r in range(len(msisdn_list)):
                    data = {
                        "MSISDN": msisdn_list[r],
                        "Status": status_list[r]
                    }

                    pair_info.append(data)
            else:
                return custom_text_response(_("%(pm)s is not registered as Primary-Pair", pm=kwargs['primary_msisdn']),
                                            status=STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                            mimetype=MIME_TYPES.get('TEXT'))

            return pair_info

        except Exception as e:
            db.session.rollback()

        finally:
            db.session.close()
