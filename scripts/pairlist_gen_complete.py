"""
DPS Pair-List Generation package.
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
from time import strftime

LIST_PATH = r'/var/www/html/Device-Pairing-Subsystem/pairing_lists'


def pair_list_complete():
    """ Function to generate pair-list for DIRBS CORE"""

    global con

    try:
        # con = pg.connect("dbname = 'DPS_Test' user = 'postgres' password = 'Pakistan1' host = 'localhost'")
        con = pg.connect("dbname = 'dps' user = 'admin' password = 'admin' host = '192.168.100.69'")

        cur = con.cursor()

        cur.execute(""" select imei_id, imsi, old_imsi from pairing where add_pair_status = true order by imei_id ;""")

        chk_1 = cur.fetchall()

        filename = LIST_PATH + '/Pair_List_Complete' + '_' + strftime("%Y-%m-%d_%H-%M-%S") + '.csv'

        file = open(filename, 'w')
        file.write('imei,' + 'imsi' + '\n')

        if chk_1:

            for qry in chk_1:

                if qry[1] and qry[2] is None:
                    cur.execute(""" select imei from imei where id = {} ;""".format(qry[0]))
                    chk_imei = cur.fetchone()
                    file.write(chk_imei[0] + ',' + qry[1] + '\n')

                elif qry[1] is None and qry[2]:
                    cur.execute(""" select imei from imei where id = {} ;""".format(qry[0]))
                    chk_imei = cur.fetchone()
                    file.write(chk_imei[0] + ',' + qry[2] + '\n')

        file.close()

        con.commit()

        return

    except Exception as e:
        cur.close()
        con.close()
        return

    finally:
        cur.close()
        con.close()


if __name__ == "__main__":
    pair_list_complete()
