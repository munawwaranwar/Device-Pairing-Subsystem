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


import psycopg2 as pg
from time import strftime

LIST_PATH = r'/var/www/html/Device-Pairing-Subsystem/pairing_lists'


def pair_list_creation():
    """ Function to generate pair-list for DIRBS CORE"""

    global con

    try:
        # con = pg.connect("dbname = 'DPS_Test' user = 'postgres' password = 'Pakistan1' host = 'localhost'")
        con = pg.connect("dbname = 'dps' user = 'admin' password = 'admin' host = '192.168.100.69'")

        cur = con.cursor()

        cur.execute(""" select imei_id, imsi, old_imsi, change_type from pairing where imsi is not null
                        and change_type is not null and export_status = false order by imei_id ;""")

        chk_1 = cur.fetchall()

        filename_add = LIST_PATH + '/ADD_Pair_List' + '_' + strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
        filename_remove = LIST_PATH + '/REMOVE_Pair_List' + '_' + strftime("%Y-%m-%d_%H-%M-%S") + '.csv'

        add_file = open(filename_add, 'w')
        add_file.write('imei,' + 'imsi,' + 'change_type' + '\n')

        remove_file = open(filename_remove, 'w')
        remove_file.write('imei,' + 'imsi,' + 'change_type' + '\n')

        if chk_1:

            for qry in chk_1:

                if qry[2]:

                    cur.execute(""" select imei from imei where id = {} ;""".format(qry[0]))
                    chk_imei = cur.fetchone()
                    remove_file.write(chk_imei[0] + ',' + qry[2] + ',remove\n')
                    add_file.write(chk_imei[0] + ',' + qry[1] + ',add\n')

                elif qry[3] == 'remove':

                    cur.execute(""" select imei from imei where id = {} ;""".format(qry[0]))
                    chk_imei = cur.fetchone()
                    remove_file.write(chk_imei[0] + ',' + qry[1] + ',remove\n')

                elif qry[3] == 'add' and qry[2] is None:

                    cur.execute(""" select imei from imei where id = {} """.format(qry[0]))
                    chk_imei = cur.fetchone()
                    add_file.write(chk_imei[0] + ',' + qry[1] + ',add\n')

            cur.execute(""" update pairing set export_status = true , old_imsi = null
                            where imsi is not null and change_type is not null and export_status = false """)

            # uniqe_pairs = set(open(filename).readlines())
            # file2 = open(filename, 'w')
            #
            # for row in uniqe_pairs:
            #     file2.write(row)
            #
            # file2.close()

        add_file.close()
        remove_file.close()

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
    pair_list_creation()
