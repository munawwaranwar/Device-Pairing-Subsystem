"""
Unit Test Module for Release-All API
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

import json
from tests._fixtures import *
from tests._helpers import *
from app import conf

REL_ALL_API = 'api/v1/rel-all'
HEADERS = {'Content-Type': "application/json"}

def test_rel_all_pairs_validation_wrong_Sender_No(flask_app, db):
    """ Verify that rel-all api doesn't accept invalid primary """
    sender_no = ['924006171951', '9230028460937724', '92321417g9C21', '92345@769#564&8', '923004']
    for val in sender_no:
        payload = {"Sender_No": val}
        rslt = flask_app.delete(REL_ALL_API, headers=HEADERS, data=json.dumps(payload))
        assert rslt.data == b"Primary MSISDN format is not correct"


def test_rel_all_pairs_validations_valid_Sender_No(flask_app, db):
    """ Verify that rel-all api only accepts valid primary & secondary numbers """
    payload = {"Sender_No": "923458179437"}
    rslt = flask_app.delete(REL_ALL_API, headers=HEADERS, data=json.dumps(payload))
    assert not rslt.data == b"Primary MSISDN format is not correct"


def test_rel_all_pairs_missing_parameters(flask_app, db):
    """ Verify that rel-all api prompts when any parameter is missing """
    payload_1 = {"Sender_No": ""}
    payload_2 = {}
    rslt_1 = flask_app.delete(REL_ALL_API, headers=HEADERS, data=json.dumps(payload_1))
    rslt_2 = flask_app.delete(REL_ALL_API, headers=HEADERS, data=json.dumps(payload_2))
    assert rslt_1.data == b"Sender number is missing in SMS"
    assert rslt_2.data == b"Sender number is missing in SMS"


def test_rel_all_pairs_error_400_bad_request(flask_app, db):
    """ Verify that rel-all api prompts when Error-400 is occurred """
    payload = {"Sender_No": "923225782404"}
    result = flask_app.delete(REL_ALL_API, headers=HEADERS, data=payload)
    print(result.data)
    assert result.status_code == 400


def test_rel_all_pairs_error_404_wrong_api(flask_app, db):
    """ Verify that rel-all api prompts when Error-404 is occurred """
    tmp_API = 'api/v1/relll-@llll'
    payload = {"Sender_No": "923225782404"}
    result = flask_app.delete(tmp_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.status_code == 404


def test_rel_all_pairs_error_405_method_not_allowed(flask_app, db):
    """ Verify that rel-all api prompts when Error-405 is occurred """
    res1 = flask_app.get(REL_ALL_API)
    assert res1.status_code == 405
    res2 = flask_app.post(REL_ALL_API)
    assert res2.status_code == 405
    res3 = flask_app.put(REL_ALL_API)
    assert res3.status_code == 405
    res4 = flask_app.patch(REL_ALL_API)
    assert res4.status_code == 405


def test_rel_all_pairs_happy_case_without_sec_pairs(flask_app,db, session):
    """ Verify that rel-all api deletes primary-pair incase no secondary pair exists """
    complete_db_insertion(session, db, 311, '923036830442', 311, 'Find-X', 'OPPO', '5RT1qazbh', '3G,4G',
                          'EiBuagYD', 311, '889270911982467')
    first_pair_db_insertion(session, db, 312, '923460192939', 'telenor', 311)

    payload = {"Sender_No": "923460192939"}
    result = flask_app.delete(REL_ALL_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert b"Release All-Pairs request is registered. New Pair Code is" in  result.data


def test_rel_all_pairs_happy_case_with_unconfirmed_sec_pair(flask_app,db, session):
    """ Verify that rel-all api deletes primary-pair as well as unconfirmed secondary-pair  """
    complete_db_insertion(session, db, 312, '923047930553', 312, 'F-9', 'OPPO', 'Fd9kLqwV', '3G,4G',
                          'gc8nXsL4', 312, '910223945867106')
    first_pair_db_insertion(session, db, 313, '923145406911', 'zong', 312)
    add_pair_db_insertion(session, db, 314, 313, '923125840917', 312)

    payload = {"Sender_No": "923145406911"}
    result = flask_app.delete(REL_ALL_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert b"Release All-Pairs request is registered. New Pair Code is" in  result.data


def test_rel_all_pairs_happy_case_with_confirmed_sec_pair(flask_app,db, session):
    """ Verify that rel-all api deletes primary-pair as well as confirmed secondary-pair  """
    complete_db_insertion(session, db, 313, '923057930229', 313, 'MI MIX 2S ', 'XIAOMI', 'SN1i9KpW', '3G,4G',
                          'X92jXN42', 313, '910223947111222')
    first_pair_db_insertion(session, db, 315, '923158191645', 'zong', 313)
    add_pair_db_insertion(session, db, 316, 315, '923125840917', 313)
    add_pair_confrm_db_insertion(session, db, '923125840917', 315, 'zong')

    payload = {"Sender_No": "923158191645"}
    result = flask_app.delete(REL_ALL_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert b"Release All-Pairs request is registered. New Pair Code is" in result.data


def test_rel_all_pairs_happy_case_with_maximum_sec_pairs(flask_app,db, session):
    """ Verify that rel-all api deletes all pairs including primary-pair   """
    complete_db_insertion(session, db, 314, '923057930229', 314, 'PocoPhone ', 'XIAOMI', 'Sb9i9]]KpW', '3G,4G',
                          'QKxc9P39', 314, '910223947111444')
    first_pair_db_insertion(session, db, 317, '923338791465', 'ufone', 314)
    sec_pairs = ['923115798111', '923125798222', '923135798333', '923145798444']
    sec_id = 318
    for msisdn in range(0,conf['pair_limit']):
        add_pair_db_insertion(session, db, sec_id, 317, sec_pairs[msisdn], 314)
        sec_id += 1

    payload = {"Sender_No": "923338791465"}
    result = flask_app.delete(REL_ALL_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert b"Release All-Pairs request is registered. New Pair Code is" in result.data


def test_rel_all_pairs_functionality_wrong_primary_msisdn(flask_app,db, session):
    """ Verify that rel-all api detects wrong primary-pair """
    complete_db_insertion(session, db, 315, '923089923776', 315, 'Nokia-4 ', 'NOKIA', 'Sbqa7KpW', '2G,3G,4G',
                          'BiaJTc5t', 315, '910223947333344')
    first_pair_db_insertion(session, db, 330, '923216754889', 'warid', 315)
    add_pair_db_insertion(session, db, 331, 330, '923125840917', 315)

    payload = {"Sender_No": "923216744444"}
    result = flask_app.delete(REL_ALL_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.data == b"Release-All request not made by Primary-MSISDN"


def test_rel_all_pairs_functionality_repetitive_requests(flask_app,db, session):
    """ Verify that rel-all api detects wrong primary-pair """
    complete_db_insertion(session, db, 316, '923079924476', 316, 'LUMIA ', 'NOKIA', 'S2w434a7hW', '2G,3G',
                          '4eue5SaB', 316, '871022394555554')

    first_pair_db_insertion(session, db, 332, '923145892007', 'zong', 316)
    session.execute(text("""UPDATE public.pairing_codes SET is_active = false WHERE pair_code = '4eue5NaB';"""))

    add_pair_db_insertion(session, db, 333, 332, '923008162773', 316)

    payload = {"Sender_No": "923145892007"}
    result = flask_app.delete(REL_ALL_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert b"Release All-Pairs request is registered. New Pair Code is" in result.data

    for i in range(0,3):
        result = flask_app.delete(REL_ALL_API, headers=HEADERS, data=json.dumps(payload))
        print(result.data)
        assert b"Release-All request is already registered" in result.data


def test_rel_all_pairs_functionality_chk_db_insertion_without_sec_pair(flask_app,db,session):
    """ Verify that rel-single api inserts correct values of change_type & export_status """
    complete_db_insertion(session, db, 317, '923099924433', 317, 'G5 ', 'LG', 'sDx5ue73M', '2G,3G',
                          'X4fwY8ia', 317, '871024444488794')
    first_pair_db_insertion(session, db, 335, '923155432109', 'zong', 317)

    session.execute(text("""UPDATE public.pairing SET imsi = '410079201640338' WHERE msisdn = '923155432109';"""))
    payload = {"Sender_No": "923155432109"}
    result = flask_app.delete(REL_ALL_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)

    qry = session.execute(text("""SELECT * FROM pairing WHERE msisdn = '923155432109'; """)).fetchone()
    print(qry.change_type, qry.export_status)
    assert qry.change_type == 'REMOVE'
    assert qry.export_status == False


def test_rel_all_pairs_functionality_chk_db_insertion_with_sec_pair(flask_app, db, session):
    """ Verify that rel-single api inserts correct values of change_type & export_status """
    complete_db_insertion(session, db, 318, '923219925555', 318, 'Z4', 'QMobile', 'Hj7w3p9U', '3G,4G',
                          'Lq6YHxG9', 318, '673394444483333')
    first_pair_db_insertion(session, db, 336, '923457819043', 'telenor', 318)
    add_pair_db_insertion(session, db, 337, 336, '923028432506', 318)

    session.execute(text("""UPDATE public.pairing SET imsi = '410019876543210', add_pair_status = true WHERE msisdn = '923028432506';"""))
    payload = {"Sender_No": "923457819043"}
    result = flask_app.delete(REL_ALL_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)

    qry = session.execute(text("""SELECT * FROM pairing WHERE msisdn = '923028432506'; """)).fetchone()
    print(qry.change_type, qry.export_status)
    assert qry.change_type == 'REMOVE'
    assert qry.export_status == False
