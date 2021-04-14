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
from ..schema.input_schema import DeviceSearchSchema
from app.api.assets.error_handlers import custom_text_response, custom_json_response
from app.api.assets.response import STATUS_CODES, MIME_TYPES


# noinspection SqlDialectInspection,PyUnusedLocal
class DeviceSearch(Resource):
    """Flask resource to search device(s)."""

    @staticmethod
    @use_kwargs(DeviceSearchSchema().fields_dict, locations=['querystring'])
    def get(**kwargs):
        """method to search device(s)"""

        try:

            cases = []
            para_cnt = len(kwargs)
            fst = False

            qry = "select contact, brand, model, serial_no, string_agg(imei,',') as imei, mac, " \
                  "pair_code, is_active from test_view where "

            if para_cnt > 2:

                for p in kwargs:

                    if p == "imei" and not fst:              # building the database query
                        qry = qry + """{} = '{}' """.format(p, (kwargs.get(p)))
                        fst = True
                    elif p == "imei" and fst:
                        qry = qry + """ and {} = '{}' """.format(p, (kwargs.get(p)))
                    elif p == "serial_no" and not fst:
                        qry = qry + """{} = '{}' """.format(p, (kwargs.get(p)))
                        fst = True
                    elif p == "serial_no" and fst:      # pragma: no cover
                        qry = qry + """ and {} = '{}' """.format(p, (kwargs.get(p)))
                    elif p == "mac" and not fst:
                        qry = qry + """{} = '{}' """.format(p, (kwargs.get(p)))
                        fst = True
                    elif p == "mac" and fst:            # pragma: no cover
                        qry = qry + """ and {} = '{}' """.format(p, (kwargs.get(p)))
                    elif p == "contact" and not fst:
                        qry = qry + """{} = '{}' """.format(p, (kwargs.get(p)))
                        fst = True
                    elif p == "contact" and fst:
                        qry = qry + """ and {} = '{}' """.format(p, (kwargs.get(p)))

                tmp_qry = qry + " group by serial_no, mac,contact, brand, model, pair_code, is_active ;"

                chk_rslt = db.engine.execute(tmp_qry)

                qry_count = chk_rslt.fetchall()

                qry = qry + " group by serial_no, mac,contact, brand, model, pair_code," \
                            " is_active Limit {} offset {} ;".format(kwargs['limit'], kwargs['start'])

                rslt = db.session.execute(qry)

                for rows in rslt:
                    cases.append(dict((a, b) for a, b in rows.items()))

                if cases:
                    paginated_data = {'start': kwargs['start'],
                                      'limit': kwargs['limit'],
                                      'count': len(qry_count),
                                      'cases': cases
                                      }

                    return custom_text_response(paginated_data, status=STATUS_CODES.get('OK'),
                                                mimetype=MIME_TYPES.get('JSON'))

                else:
                    data = {
                        "start": kwargs['start'],
                        "cases": cases,
                        "count": 0,
                        "limit": kwargs['limit']
                    }

                    return custom_text_response(data, status=STATUS_CODES.get('OK'),
                                                mimetype=MIME_TYPES.get('JSON'))
            else:
                return custom_json_response(_("Please select any search parameter"),
                                            status=STATUS_CODES.get('NOT_FOUND'),
                                            mimetype=MIME_TYPES.get('JSON'))

        except Exception as e:
            db.session.rollback()           # pragma: no cover

        finally:
            db.session.close()
