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
import magic
import tempfile
import pandas as pd
from flask import request
from time import strftime
from shutil import rmtree
from flask_babel import _
from app import conf, app, db
from flask_restful import Resource
from flask_apispec import use_kwargs
from werkzeug.utils import secure_filename
from ..assets.response import *
from ..common.database import connect
from ..schema.input_schema import BulkUploadSchema
from ..assets.error_handlers import custom_json_response, custom_text_response


UPLOAD_FOLDER = app.config['DPS_UPLOADS']
DOWNLOAD_FOLDER = app.config['DPS_DOWNLOADS']


# noinspection PyUnusedLocal,SqlDialectInspection
class BulkImsiUpload(Resource):
    """Flask resource to upload Bulk IMSIs File."""

    @staticmethod
    @use_kwargs(BulkUploadSchema().fields_dict, locations=['form'])
    def post(**kwargs):
        """method to upload bulk IMSIs File"""

        try:
            file = request.files.get('file')
            if file and file_allowed(file.filename):
                tmp_dir = tempfile.mkdtemp()
                filename = secure_filename(file.filename)
                filepath = os.path.join(tmp_dir, filename)
                file.save(filepath)
                try:
                    filetype = magic.from_file(filepath, mime=True)

                    if filename != '' or filetype == 'text/plain':
                        try:
                            with open(filepath, 'r') as newfile:
                                df = pd.read_csv(newfile, usecols=range(2), dtype={"MSISDN": str, "IMSI": str})

                            newfile.close()
                        except Exception as e:
                            if e:
                                newfile.close()
                                return custom_json_response(_("File content is not Correct"),
                                                            STATUS_CODES.get('FORBIDDEN'), MIME_TYPES.get('JSON'))

                        total_rows, total_columns = df.shape

                        if df.columns[0] == 'MSISDN' or df.columns[1] == 'IMSI':

                            df_dup = df[df.duplicated(['IMSI'], keep='first')]

                            if df_dup.empty:

                                df2 = df[df.isnull().any(axis=1)]  # to detect null values in any column
                                df1 = df.dropna()  # to drop rows with one or more null values
                                df3 = df1[~(df1.MSISDN.astype(str).str.match(conf['validation_regex']['msisdn']))]
                                df1 = df1[(df1.MSISDN.astype(str).str.match(conf['validation_regex']['msisdn']))]
                                df4 = df1[~(df1.IMSI.astype(str).str.match(conf['validation_regex']['imsi']))]
                                df1 = df1[(df1.IMSI.astype(str).str.match(conf['validation_regex']['imsi']))]

                                final_rows, final_columns = df1.shape
                                del_rec = (total_rows - final_rows)

                                df1.to_csv(filepath, index=False)

                                lst_df = [df2, df3, df4]
                                dfs = pd.concat(lst_df, ignore_index=False)

                                con = connect()
                                filename1 = os.path.join(tmp_dir, filename)
                                cur = con.cursor()

                                cur.execute(""" CREATE TABLE if not exists test_mno (t_msisdn text, t_imsi text)""")
                                # con.commit()

                                f = open(filename1)
                                cur.copy_from(f, 'test_mno', sep=",")

                                cur.execute(""" update pairing set imsi = test_mno.t_imsi, change_type = 'add',
                                                export_status = false, updated_at = date_trunc('second', NOW())
                                                from test_mno
                                                where pairing.msisdn = test_mno.t_msisdn and pairing.end_date is null
                                                and pairing.add_pair_status = true and pairing.operator_name = 
                                                '{mno}'""".format(mno=kwargs['operator']))

                                cur.execute(""" drop table if exists test_mno;  """)

                                con.commit()
                                cur.close()
                                con.close()
                                f.close()

                                if del_rec != 0:

                                    error_file = "Error-Records_" + kwargs['operator'] + '_' \
                                                 + strftime("%Y-%m-%d_%H-%M-%S") + '.csv'

                                    download_path = os.path.join(DOWNLOAD_FOLDER, error_file)

                                    file.save(download_path)
                                    dfs.to_csv(download_path, index=False)

                                    rtn_msg = {
                                        "msg": _("File loaded successfully"),
                                        "Total_Records": total_rows,
                                        "Successful_Records": final_rows,
                                        "Deleted_Record": del_rec,
                                        "link": download_path
                                    }

                                    return custom_text_response(rtn_msg, STATUS_CODES.get('OK'), MIME_TYPES.get('JSON'))
                                else:
                                    return custom_json_response(_("File uploaded successfully without errors"),
                                                                STATUS_CODES.get('OK'), MIME_TYPES.get('JSON'))
                            else:
                                return custom_json_response(_("File contains duplicated IMSIs"),
                                                            STATUS_CODES.get('FORBIDDEN'), MIME_TYPES.get('JSON'))
                        else:
                            return custom_json_response(_("File headers are incorrect"),
                                                        STATUS_CODES.get('FORBIDDEN'), MIME_TYPES.get('JSON'))
                    else:
                        return custom_json_response(_("System only accepts csv/txt files"),
                                                    STATUS_CODES.get('FORBIDDEN'), MIME_TYPES.get('JSON'))

                finally:
                    rmtree(tmp_dir)
            else:
                return custom_json_response(_("Please select csv/txt file"),
                                            STATUS_CODES.get('UNPROCESSABLE_ENTITY'),
                                            MIME_TYPES.get('JSON'))

        except Exception as e:
            db.session.rollback()

        finally:
            db.session.close()


def file_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in conf['allowed_extensions']
