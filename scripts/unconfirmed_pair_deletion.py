"""
DPS Unconfirmed Pair Deletion package.
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
from datetime import datetime


def uncnfrmd_pair_deletion():
    """ Function to delete unconfirmed pairs after specific time"""
    try:
        con = pg.connect("dbname = 'DPS_Test' user = 'postgres' password = 'Pakistan1' host = 'localhost'")
        #con = pg.connect("dbname = 'dps' user = 'admin' password = 'admin' host = '192.168.100.69'")

        cur = con.cursor()

        fmt = '%Y-%m-%d %H:%M:%S'

        crnt_date = strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""select "creation_date" , "id" from pairing where "add_pair_status" = false """)

        rslt = cur.fetchall()

        for index, i in enumerate(rslt):

            d1 = datetime.strptime(crnt_date, fmt)

            d2 = datetime.strptime(str(rslt[index][0]), fmt)
            time_diff = d1-d2

            seconds = int(time_diff.total_seconds())

            #days = time_diff.days
            #minutes = int(int(time_diff.total_seconds())/60)
            #hours = int((int(time_diff.total_seconds())/60)/60)
            #day_2 = int(((int(time_diff.total_seconds()) / 60) / 60)/24)

            #print("Time difference in Total Secs: ",seconds)
            #print("Time difference in Days: ", days)
            #print("Time difference in Total Minutes: ", minutes)
            #print("Time difference in Total Hours: ", hours)
            #print("Time difference in Total Days: ", day_2)

            if seconds > 86400:

                cur.execute("""delete from pairing where id = {}; """.format(rslt[index][1]))

        con.commit()

        con.close()

        return

    except Exception as e:
        con.close()

    finally:
        con.close()


if __name__ == "__main__":
    uncnfrmd_pair_deletion()
