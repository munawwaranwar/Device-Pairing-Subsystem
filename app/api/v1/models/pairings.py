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
from time import strftime


class Pairing(db.Model):
    """ Class to create Db Table pairing """

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    primary_id = db.Column(db.BigInteger)
    msisdn = db.Column(db.String(20))
    imsi = db.Column(db.String(20))
    is_primary = db.Column(db.Boolean)
    creation_date = db.Column(db.DateTime, default=strftime("%Y-%m-%d %H:%M:%S"))
    end_date = db.Column(db.Date)
    updated_at = db.Column(db.DateTime)
    operator_name = db.Column(db.String(20))
    add_pair_status = db.Column(db.Boolean)
    change_type = db.Column(db.String(20))
    export_status = db.Column(db.Boolean)
    old_imsi = db.Column(db.String(20))

    imei_id = db.Column(db.BigInteger, db.ForeignKey('imei.id'))

    def __repr__(self):     # pragma: no cover
        return "<Pairing ({} ,{}, {})>".format(self.id, self.msisdn, self.imsi)

    @classmethod
    def create_index(cls, engine):
        """ Method to create Indexes for pairing table. """

        devices_msisdn = db.Index('devices_msisdn_index', cls.msisdn, postgresql_concurrently=False)
        devices_msisdn.create(bind=engine)

        devices_imsi = db.Index('devices_imsi_index', cls.imsi, postgresql_concurrently=False)
        devices_imsi.create(bind=engine)

        devices_creation_date = db.Index('devices_creation_date_index', cls.creation_date, postgresql_concurrently=False)
        devices_creation_date.create(bind=engine)

        devices_end_date = db.Index('devices_end_date_index', cls.end_date, postgresql_concurrently=False)
        devices_end_date.create(bind=engine)

        devices_operator_name = db.Index('devices_operator_index', cls.operator_name, postgresql_concurrently=False)
        devices_operator_name.create(bind=engine)
