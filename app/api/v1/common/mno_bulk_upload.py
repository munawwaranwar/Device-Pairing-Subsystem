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
import re
from werkzeug.utils import secure_filename
from flask import request
from app import db, conf
import pandas as pd
from time import strftime
import magic
from app.api.v1.common.database import connect
from flask_babel import lazy_gettext as _


ALLOWED_EXTENSIONS = {'csv', 'txt'}
UPLOAD_FOLDER = conf['Upload_Path']
DOWNLOAD_FOLDER = conf['Download_Path']


class BulkUpload:

    # noinspection PyUnboundLocalVariable,PyUnusedLocal
    @staticmethod
    def bulk_imsis():

        try:
            chk_mno = False
            rtn_msg = ""
            mno = request.form.get("mno")

            for key, val in conf.items():  # checking for correct operator's name
                if mno == val:
                    chk_mno = True

            if not chk_mno:
                data = {
                    "Error": _("improper Operator-name provided")
                }
                return data, 422

            else:

                file = request.files.get('file')

                if file and file_allowed(file.filename):

                    filename = secure_filename(file.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(os.path.join(UPLOAD_FOLDER, filename))

                    f = magic.Magic(mime=True)
                    file_type = f.from_file(file_path)
                    if file_type != 'text/plain':
                        data = {
                            "Error": _("File type is not valid")
                        }
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        return data, 422

                    # --------------------------------------------------------------------------------------------------

                    pat1 = re.compile(r'923\d{9}')
                    pat2 = re.compile(r'\d{15}')
                    try:
                        newfile = open(file_path, 'r')
                        df = pd.read_csv(newfile, usecols=range(2), dtype={"MSISDN": str, "IMSI": str})
                        newfile.close()
                    except Exception as e:
                        if e:
                            newfile.close()
                            data = {
                                "Error": _("File content is not Correct")
                            }
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                            return data, 422

                    total_rows, total_columns = df.shape

                    if df.columns[0] != 'MSISDN' or df.columns[1] != 'IMSI':
                        data = {
                            "Error": _("File headers are missing or incorrect")
                        }
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        return data, 422

                    df_dup = df[df.duplicated(['IMSI'], keep='first')]  # To detect duplicated IMSIs in uploaded File

                    if not df_dup.empty:
                        data = {
                            "Error": _("File contains duplicated IMSIs")
                        }
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        return data, 422

                    else:
                        df2 = df[df.isnull().any(axis=1)]
                        df1 = df.dropna()
                        df3 = df1[(df1.IMSI.astype(str).str.len() > 15)]
                        df1 = df1[~(df1.IMSI.astype(str).str.len() > 15)]
                        df4 = df1[(df1.MSISDN.astype(str).str.len() > 12)]
                        df1 = df1[~(df1.MSISDN.astype(str).str.len() > 12)]
                        df5 = df1[~(df1.IMSI.astype(str).str.match(pat2))]
                        df1 = df1[(df1.IMSI.astype(str).str.match(pat2))]
                        df6 = df1[~(df1.MSISDN.astype(str).str.match(pat1))]
                        df1 = df1[(df1.MSISDN.astype(str).str.match(pat1))]

                        final_rows, final_columns = df1.shape
                        del_rec = (total_rows - final_rows)
                        df1.to_csv(file_path, index=False)

                        lst_df = [df2, df3, df4, df5, df6]
                        dfs = pd.concat(lst_df, ignore_index=False)
                        # ----------------------------------------------------------------------------------------------

                        con = connect()
                        filename1 = os.path.join(UPLOAD_FOLDER, filename)
                        cur = con.cursor()

                        cur.execute(""" CREATE TABLE if not exists test_mno (t_msisdn text, t_imsi text)""")
                        con.commit()

                        f = open(filename1)
                        cur.copy_from(f, 'test_mno', sep=",")

                        cur.execute(""" update pairing set imsi = test_mno.t_imsi, change_type = 'add',
                                        export_status = false, updated_at = date_trunc('second', NOW())
                                        from test_mno
                                        where pairing.msisdn = test_mno.t_msisdn and pairing.end_date is null
                                        and pairing.add_pair_status = true and pairing.operator_name = '{mno}'""".format(
                            mno=mno
                        ))
                        con.commit()

                        cur.execute(""" drop table if exists test_mno;  """)

                        con.commit()

                        con.close()
                        f.close()

                        if del_rec > 0:
                            error_file = "Error-Records_" + mno + '_' + strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
                            download_path = os.path.join(DOWNLOAD_FOLDER, error_file)
                            file.save(download_path)
                            dfs.to_csv(download_path, index=False)
                        else:
                            download_path = _("No error file available")

                        rtn_msg = {
                            "msg": _("File successfully loaded"),
                            "Total_Records": total_rows,
                            "Successful_Records": final_rows,
                            "Deleted_Record": del_rec,
                            "link": download_path
                        }
                        return rtn_msg, 200

                else:

                    rtn_msg = {
                        "Error": _("No file or improper file found")
                    }

                    return rtn_msg, 422

        except Exception as e:
            db.session.rollback()

        finally:
            db.session.close()


def file_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
