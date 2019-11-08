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

import os
from app import db, app
from time import strftime
from flask_babel import _
from flask import make_response, send_file
from flask_restful import Resource
from flask_apispec import use_kwargs
from ..assets.response import *
from ..schema.input_schema import BulkDownloadSchema
from ..assets.error_handlers import custom_json_response
from ..models.pairings import Pairing


# noinspection PyComparisonWithNone,PyUnusedLocal,DuplicatedCode
class BulkMsisdnDownload(Resource):
    """Flask resource to download bulk MSISDN File."""

    @staticmethod
    @use_kwargs(BulkDownloadSchema().fields_dict, locations=['querystring'])
    def get(**kwargs):
        """method to download Bulk MSISDN File"""

        try:
            msisdn_list = []
            DOWNLOAD_FOLDER = app.config['DPS_DOWNLOADS']

            chk_imsi = Pairing.query.filter(Pairing.operator_name == '{}'.format(kwargs['operator'])) \
                                            .filter(Pairing.imsi == None) \
                                            .filter(Pairing.add_pair_status == True) \
                                            .filter(Pairing.end_date == None).all()
            # to check which MSISDNs require IMSI from MNO

            if chk_imsi:

                filename = "MSISDNs-List_" + kwargs['operator'] + '_' + strftime("%Y-%m-%d_%H-%M-%S") + '.csv'

                download_path = os.path.join(DOWNLOAD_FOLDER, filename)

                for c in chk_imsi:
                    msisdn_list.append(c.msisdn)

                msisdn_list = set(msisdn_list)
                msisdn_list = list(msisdn_list)

                with open(download_path, 'w') as file:

                    file.write('MSISDN,IMSI\n')
                    file.write(",\n".join(msisdn_list))

                file.close()

                response = make_response(send_file(download_path, as_attachment=True))
                response.headers['Cache-Control'] = 'no-store'
                return response

            else:
                return custom_json_response(_("No File found"),
                                            status=STATUS_CODES.get('NOT_FOUND'),
                                            mimetype=MIME_TYPES.get('JSON'))

        except Exception as e:
            db.session.rollback()       # pragma: no cover

        finally:
            db.session.close()
