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

import string
from app import db
from random import choice
from flask_babel import _
from flask_restful import Resource
from flask_apispec import use_kwargs
from ..assets.response import *
from ..models.pairings import Pairing
from ..schema.input_schema import MnoHomePageSchema
from ..assets.error_handlers import custom_text_response, custom_json_response


# noinspection PyComparisonWithNone,PyUnusedLocal
class MnoHomePage(Resource):
    """Flask resource to populate Operators home page with MSISDNs."""

    @staticmethod
    @use_kwargs(MnoHomePageSchema().fields_dict, locations=['querystring'])
    def get(**kwargs):
        """method to populate Operators home page with MSISDNs"""

        try:

            mno_info = []
            msisdn_list = []

            chk_count = Pairing.query.filter(Pairing.operator_name == '{}'.format(kwargs['operator']),
                                             Pairing.imsi == None,
                                             Pairing.add_pair_status == True,
                                             Pairing.end_date == None).distinct(Pairing.msisdn).count()

            chk_imsi = Pairing.query.filter(Pairing.operator_name == '{}'.format(kwargs['operator']),
                                            Pairing.imsi == None,
                                            Pairing.add_pair_status == True,
                                            Pairing.end_date == None).distinct(Pairing.msisdn). \
                                            offset(kwargs['start']).limit(kwargs['limit']).all()

            if chk_imsi:

                for c in chk_imsi:
                    msisdn_list.append(c.msisdn)

                for r in msisdn_list:
                    a = gen_req_id()
                    data = {
                        "Req_id": a,
                        "MSISDN": r
                    }
                    mno_info.append(data)

                if mno_info:
                    paginated_data = {'start': kwargs['start'],
                                      'limit': kwargs['limit'],
                                      'count': chk_count,
                                      'cases': mno_info
                                      }
                    return custom_text_response(paginated_data, status=STATUS_CODES.get('OK'),
                                                mimetype=MIME_TYPES.get('JSON'))
            else:

                return custom_json_response(_("no record found"),
                                            status=STATUS_CODES.get('NOT_FOUND'),
                                            mimetype=MIME_TYPES.get('JSON'))

        except Exception as e:          # pragma: no cover
            db.session.rollback()

        finally:
            db.session.close()


# noinspection PyUnusedLocal
def gen_req_id():
    all_char = string.ascii_letters + string.digits
    req_id = "".join(choice(all_char) for x in range(8))
    return req_id
