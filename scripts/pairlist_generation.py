"""
DPS notification resource package.
Copyright (c) 2018 Qualcomm Technologies, Inc.
 All rights reserved.
 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
 limitations in the disclaimer below) provided that the following conditions are met:
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
 disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
 disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
 products derived from this software without specific prior written permission.
 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
 THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
 TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.
"""

import psycopg2 as pg
import os
from time import strftime

LIST_PATH = r'D:\dirbs_intl_dps\Pairing_Lists'

def pair_list_creation():
    """ Function to generate pair-list for DIRBS CORE"""

    global con
    try:
        pairs = []
        con = pg.connect("dbname = 'DPS_Test' user = 'postgres' password = 'Pakistan1' host = 'localhost'")
        # con = pg.connect("dbname = 'dps' user = 'admin' password = 'admin' host = '192.168.100.69'")

        cur = con.cursor()

        cur.execute(""" select imei_id, imsi, change_type, export_status, old_imsi from pairing where imsi is not null
                        and change_type is not null and export_status = false order by imei_id ;""")

        chk_1 = cur.fetchall()

        if chk_1:

            filename = LIST_PATH + '/Pair_List' + '_' + strftime("%Y-%m-%d_%H-%M-%S") + '.csv'

            file = open(filename, 'w')

            for qry in chk_1:

                if qry[4]:
                    cur.execute(""" select imei from imei where id = {} ;""".format(qry[0]))
                    chk_imei = cur.fetchone()
                    file.write(chk_imei[0] + ',' + qry[4] + ',REMOVE\n')
                    file.write(chk_imei[0] + ',' + qry[1] + ',ADD\n')

                else:
                    cur.execute(""" select imei from imei where id = {} """.format(qry[0]))
                    chk_imei = cur.fetchone()
                    file.write(chk_imei[0] + ',' + qry[1] + ',ADD\n')

            file.close()

            cur.execute(""" update pairing set export_status = true , old_imsi = null
                            where imsi is not null and change_type is not null and export_status = false """)

            uniqe_pairs = set(open(filename).readlines())
            file2 = open(filename, 'w')

            for row in uniqe_pairs:
                file2.write(row)

            file2.close()

        else:
            path = os.path.dirname(os.path.dirname(__file__)) + r'\app' + '\Pair_Lists'
            filename = LIST_PATH + '\PairList_ERROR_' + strftime("%Y-%m-%d_%H-%M-%S") + '.csv'

            file = open(filename, 'w')

            file.write("No Record found / no new pair created.....")
            file.close()

        con.commit()

        con.close()

        return

    except Exception as e:
        print(e)
        con.close()
        return

    finally:
        con.close()


if __name__ == "__main__":
    pair_list_creation()
