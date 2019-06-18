"""
Unit Test Module DB-Models and Indices test
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

# noinspection PyUnresolvedReferences,PyProtectedMember
from tests._fixtures import *
from app.api.v1.models.pairings import Pairing
from app.api.v1.models.pairing_codes import Pairing_Codes
from app.api.v1.models.imeis import Imei
from app.api.v1.models.owner import Owner
from app.api.v1.models.devices import Devices
from sqlalchemy import text


device_index, pc_index, imei_index, owner_index, dev_index = False, False, False, False, False


# noinspection PyUnusedLocal,PyShadowingNames
def test_owner_index(db, session):
    """Verify that the Owner model works correctly."""

    with db.engine.connect() as conn:
        Owner.create_index(conn)

    qry = session.execute(text(""" select * from pg_stat_user_indexes; """)).fetchall()
    for o in qry:
        if o.indexrelname == 'owner_contact_index':
            owner_index = True
            print(o.indexrelname)
    # noinspection PyUnboundLocalVariable
    assert owner_index


# noinspection PyUnusedLocal,PyShadowingNames
def test_device_indexes(db, session):
    """Verify that the Devices model works correctly."""

    with db.engine.connect() as conn:
        Devices.create_index(conn)

    qry = session.execute(text(""" select * from pg_stat_user_indexes; """)).fetchall()
    for d in qry:
        if d.indexrelname == 'devices_serialno_index':
            dev_index = True
        elif d.indexrelname == 'devices_mac_index':
            dev_index = True
        elif d.indexrelname == 'devices_model_index':
            dev_index = True
        elif d.indexrelname == 'devices_brand_index':
            dev_index = True
        print(d.indexrelname)
    # noinspection PyUnboundLocalVariable
    assert dev_index


# noinspection PyUnusedLocal,PyShadowingNames
def test_pairing_codes_index(db, session):
    """Verify that the Pairing_Codes model works correctly."""

    with db.engine.connect() as conn:
        Pairing_Codes.create_index(conn)

    qry = session.execute(text(""" select * from pg_stat_user_indexes; """)).fetchall()
    for c in qry:
        if c.indexrelname == 'devices_paircodes_index':
            pc_index = True
            print(c.indexrelname)
    # noinspection PyUnboundLocalVariable
    assert pc_index


# noinspection PyUnusedLocal,PyShadowingNames
def test_imei_index(db, session):
    """Verify that the IMEI model works correctly."""

    with db.engine.connect() as conn:
        Imei.create_index(conn)

    qry = session.execute(text(""" select * from pg_stat_user_indexes; """)).fetchall()
    for i in qry:
        if i.indexrelname == 'devices_imei_index':
            imei_index = True
            print(i.indexrelname)
    # noinspection PyUnboundLocalVariable
    assert imei_index


# noinspection PyUnusedLocal,PyShadowingNames
def test_pairing_indexes(db, session):
    """Verify that the Pairing model works correctly."""

    with db.engine.connect() as conn:
        Pairing.create_index(conn)

    qry = session.execute(text(""" select * from pg_stat_user_indexes; """)).fetchall()
    for p in qry:
        if p.indexrelname == 'devices_msisdn_index':
            device_index = True
        elif p.indexrelname == 'devices_imsi_index':
            device_index = True
        elif p.indexrelname == 'devices_creation_date_index':
            device_index = True
        elif p.indexrelname == 'devices_end_date_index':
            device_index = True
        elif p.indexrelname == 'devices_operator_index':
            device_index = True
        print(p.indexrelname)
    # noinspection PyUnboundLocalVariable
    assert device_index
