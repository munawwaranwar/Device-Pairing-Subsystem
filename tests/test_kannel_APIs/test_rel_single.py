"""
SPDX-License-Identifier: BSD-4-Clause-Clear

Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following
  disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
  disclaimer in the documentation and/or other materials provided with the distribution.
* All advertising materials mentioning features or use of this software, or any deployment of this software, or
  documentation accompanying any distribution of this software, must display the trademark/logo as per the details
  provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
* Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
  products derived from this software without specific prior written permission.

SPDX-License-Identifier: ZLIB-ACKNOWLEDGEMENT

Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable
for any damages arising from the use of this software.

Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter
it and redistribute it freely, subject to the following restrictions:

* The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If
  you use this software in a product, an acknowledgment is required by displaying the trademark/logo as per the details
  provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
* Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
* This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""


# noinspection PyUnresolvedReferences,PyProtectedMember
from tests._fixtures import *
# noinspection PyProtectedMember
from tests._helpers import *
from sqlalchemy import text


REL_SINGLE_API = 'api/v1/rel-single'
HEADERS = {'Content-Type': "application/json"}


# noinspection PyUnusedLocal,PyShadowingNames
def test_rel_single_pair_validations_wrong_sender_no(flask_app, db):
    """ Verify that rel-single api doesn't accept invalid primary and secondary numbers """
    sender_no = ['924006171951', '9230028460937724', '92321417g9C21', '92345@769#564&8', '923004']
    for val in sender_no:
        payload_1 = {"Sender_No": val, "MSISDN": "923003294857"}
        rslt_1 = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload_1))
        payload_2 = {"Sender_No": "923003294857", "MSISDN": val}
        rslt_2 = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload_2))
        assert rslt_1.data == b"Primary MSISDN format is not correct"
        assert rslt_2.data == b"Secondary MSISDN format is not correct"


# noinspection PyUnusedLocal,PyShadowingNames
def test_rel_single_pair_validations_valid_sender_no(flask_app, db):
    """ Verify that rel-single api only accepts valid primary & secondary numbers """
    sender_no = '923458179437'
    payload = {"Sender_No": sender_no, "MSISDN": sender_no}
    rslt = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    assert not rslt.data == b"Sender MSISDN format is not correct"
    assert not rslt.data == b"Secondary MSISDN format is not correct"


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_missing_parameters(flask_app, db):
    """ Verify that rel-single api prompts when any parameter is missing """
    payload = [
        {"Sender_No": "", "MSISDN": "923458179437"},
        {"MSISDN": "923458179437"},
        {"Sender_No": "923225782404", "MSISDN": ""},
        {"Sender_No": "923225782404"}
    ]
    for val in range(0, 4):
        result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload[val]))
        if val == 0:
            assert result.data == b"Sender number is missing in SMS"
        elif val == 1:
            assert result.data == b"Sender number is missing in SMS"
        elif val == 2:
            assert result.data == b"Secondary number is missing in SMS"
        elif val == 3:
            assert result.data == b"Secondary number is missing in SMS"


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_error_400_wrong_api(flask_app, db):
    """ Verify that rel-single api prompts when Error-400 is occurred """
    payload = {"Sender_No": "923225782404", "MSISDN": "923458179437"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=payload)
    print(result.data)
    assert result.status_code == 400


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_error_404_wrong_api(flask_app, db):
    """ Verify that rel-single api prompts when Error-400 is occurred """
    tmp_api = 'api/v1/rellll-singleeeee'
    payload = {"Sender_No": "923225782404", "MSISDN": "923458179437"}
    result = flask_app.delete(tmp_api, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.status_code == 404


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_error_405_method_not_allowed(flask_app, db):
    """ Verify that add-confirm api prompts when Error-405 occurrs """
    res1 = flask_app.get(REL_SINGLE_API)
    assert res1.status_code == 405
    res2 = flask_app.post(REL_SINGLE_API)
    assert res2.status_code == 405
    res3 = flask_app.put(REL_SINGLE_API)
    assert res3.status_code == 405
    res4 = flask_app.patch(REL_SINGLE_API)
    assert res4.status_code == 405


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_happy_case_unconfirmed_pair(flask_app, db, session):
    """ Verify that rel-single api successfully deletes unconfirmed secondary pair """
    complete_db_insertion(session, db, 211, '923036830442', 211, 'Find-X', 'OPPO', '5RT1qazbh', '3G,4G',
                          'EirnagYD', 211, '889270911982467')
    first_pair_db_insertion(session, db, 212, '923460192939', 'telenor', 211)
    add_pair_db_insertion(session, db, 213, 212, '923115840917', 211)

    payload = {"Sender_No": "923460192939", "MSISDN": "923115840917"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.data == b"Deletion request is successfully registered. Pair will be removed in next 24 to 48 hours"


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_happy_case_confirmed_pair(flask_app, db, session):
    """ Verify that rel-single api successfully deletes unconfirmed secondary pair """
    complete_db_insertion(session, db, 212, '923047930553', 212, 'F-9', 'OPPO', 'Fd9kLqwV', '3G,4G',
                          'gB8DXsL4', 212, '910223945867106')
    first_pair_db_insertion(session, db, 214, '923145406911', 'zong', 212)
    add_pair_db_insertion(session, db, 215, 214, '923125840917', 212)
    add_pair_confrm_db_insertion(session, db, '923125840917', 214, 'zong')

    payload = {"Sender_No": "923145406911", "MSISDN": "923125840917"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.data == b"Deletion request is successfully registered. Pair will be removed in next 24 to 48 hours"


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_functionality_wrong_primary_msisdn(flask_app, db, session):
    """ Verify that rel-single api detects wrong primary MSISDN in parameters """
    complete_db_insertion(session, db, 213, '923057930229', 213, 'MI MIX 2S ', 'XIAOMI', 'SN1i9KpW', '3G,4G',
                          '892jXN42', 213, '910223947111222')
    first_pair_db_insertion(session, db, 216, '923158191645', 'zong', 213)
    add_pair_db_insertion(session, db, 217, 216, '923125840917', 213)

    payload = {"Sender_No": "923156667777", "MSISDN": "923125840917"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.data == b"Request is not made by Primary-MSISDN or number-to-be-deleted belongs to primary pair"


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_functionality_wrong_secondary_msisdn(flask_app, db, session):
    """ Verify that rel-single api detects wrong secondary MSISDN in parameters """
    complete_db_insertion(session, db, 214, '923057930229', 214, 'PocoPhone ', 'XIAOMI', 'Sb9i9]]KpW', '3G,4G',
                          'QJIceP39', 214, '910223947111444')
    first_pair_db_insertion(session, db, 218, '923338791465', 'ufone', 214)
    add_pair_db_insertion(session, db, 219, 218, '923125840917', 214)

    payload = {"Sender_No": "923338791465", "MSISDN": "923137848888"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.data == b"MSISDN (923137848888) is not Paired with the device"


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_functionality_delete_primary_msisdn(flask_app, db, session):
    """ Verify that rel-single api doesn't allow deletion of primary pair """

    complete_db_insertion(session, db, 215, '923089923776', 215, 'Nokia-4 ', 'NOKIA', 'Sbqa7KpW', '2G,3G,4G',
                          'Ox4JTcst', 215, '910223947333344')
    first_pair_db_insertion(session, db, 220, '923216754889', 'warid', 215)
    add_pair_db_insertion(session, db, 221, 220, '923125840917', 215)

    payload = {"Sender_No": "923216754889", "MSISDN": "923216754889"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.data == b"Request is not made by Primary-MSISDN or number-to-be-deleted belongs to primary pair"


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_deletion_before_export_to_PairList(flask_app, db, session):
    """ Verify the behaviour of rel-single api when secondary pair is not exported to
        Pair-List at the time of deletion """

    complete_db_insertion(session, db, 216, '923098924476', 216, 'LUMIA ', 'NOKIA', 'S2w434a7hW', '2G,3G',
                          '4eUe5NaB', 216, '871022394555554')
    first_pair_db_insertion(session, db, 222, '923145892117', 'zong', 216)
    add_pair_db_insertion(session, db, 223, 222, '923018144773', 216)

    session.execute(text("""UPDATE public.pairing SET imsi = '410015678987223', change_type = 'add', 
                            export_status = false, add_pair_status = true WHERE msisdn = '923018144773';"""))

    payload = {"Sender_No": "923145892117", "MSISDN": "923018144773"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    q1 = session.execute(text("""SELECT * FROM public.pairing WHERE msisdn = '923018144773'; """)).fetchone()
    print("\n-----Deleted Secondary-Pair-----\nmsisdn = {}\nend_date = {}\nchange_type = {}\nexport_status = {}".
          format(q1.msisdn, q1.end_date, q1.change_type, q1.export_status))
    assert q1.change_type is None
    assert q1.export_status is None
    assert q1.old_imsi is None


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_deletion_after_export_to_PairList(flask_app, db, session):
    """ Verify the behaviour of rel-single api when secondary pair is already exported to
        Pair-List at the time of deletion """

    complete_db_insertion(session, db, 217, '923098922234', 217, 'Nokia-4', 'NOKIA', 'Aq23rDTn8', '3G,4G',
                          'S4vXXoMp', 217, '361022321334964')
    first_pair_db_insertion(session, db, 224, '923138834564', 'zong', 217)
    add_pair_db_insertion(session, db, 225, 224, '923479091924', 217)

    session.execute(text("""UPDATE public.pairing SET imsi = '410029803775223', change_type = 'add', 
                            export_status = true, add_pair_status = true WHERE msisdn = '923479091924';"""))

    payload = {"Sender_No": "923138834564", "MSISDN": "923479091924"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)

    q1 = session.execute(text("""SELECT * FROM public.pairing WHERE msisdn = '923479091924'; """)).fetchone()
    print("\n-----Deleted Secondary-Pair-----\nmsisdn = {}\nend_date = {}\nchange_type = {}\nexport_status = {}".
          format(q1.msisdn, q1.end_date, q1.change_type, q1.export_status))

    assert q1.change_type == 'remove'
    assert not q1.export_status


# noinspection PyUnusedLocal,PyShadowingNames
def test_rel_single_pair_exported_sim_changed_deleted_before_new_imsi(flask_app, db, session):
    """ Verify the behaviour of rel-single api for special case where secondary pair is exported once and after
        that SIM-Change is requested but before MNO provides new IMSI, Pair is deleted"""

    complete_db_insertion(session, db, 218, '923098922556', 218, 'Nokia-6', 'NOKIA', 'Lk9Y6VVf', '3G,4G',
                          'AxY7PiG8', 218, '451087529940964')
    first_pair_db_insertion(session, db, 226, '923339125125', 'ufone', 218)
    add_pair_db_insertion(session, db, 227, 226, '923337457869', 218)

    session.execute(text("""UPDATE public.pairing SET old_imsi = '410079703451431', change_type = null,
                                    export_status = null, add_pair_status = true WHERE msisdn = '923337457869';"""))

    payload = {"Sender_No": "923339125125", "MSISDN": "923337457869"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)

    q1 = session.execute(text("""SELECT * FROM public.pairing WHERE msisdn = '923337457869'; """)).fetchone()
    print("\n-----Deleted Secondary-Pair-----\nmsisdn = {}\nend_date = {}\nchange_type = {}\nexport_status = {}".
          format(q1.msisdn, q1.end_date, q1.change_type, q1.export_status))

    assert q1.change_type == 'remove'
    assert not q1.export_status
    assert q1.imsi == '410079703451431'
    assert not q1.old_imsi
