"""
Unit Test Module for Additional-Pair-Confirmation API
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
from tests._fixtures import *
import json
from tests._helpers import *

add_confirm_api = 'api/v1/add-cnfrm'
HEADERS = {'Content-Type': "application/json"}


def test_add_confirm_validations_wrong_sender_no(flask_app, db):
    """ Verify that add-confirm api doesn't accept invalid primary and secondary numbers """
    sender_no = ['924006171951', '9230028460937724', '92321417g9C21', '92345@769#564&8', '923004']
    for val in sender_no:
        payload_1 = {"Sender_No": val, "Operator": "jazz", "Primary_No": "923003294857", "Confirm": "Yes"}
        rslt_1 = flask_app.put(add_confirm_api, headers=HEADERS, data=json.dumps(payload_1))
        payload_2 = {"Sender_No": "923003294857", "Operator": "jazz", "Primary_No": val, "Confirm": "Yes"}
        rslt_2 = flask_app.put(add_confirm_api, headers=HEADERS, data=json.dumps(payload_2))
        assert rslt_1.data == b"Sender MSISDN format is not correct"
        assert rslt_2.data == b"Primary MSISDN format is not correct"


def test_add_confirm_validations_valid_sender_no(flask_app, db):
    """ Verify that add-confirm api only accepts valid primary & secondary numbers """
    sender_no = '923458179437'
    payload = {"Sender_No": sender_no, "Operator": "jazz", "Primary_No": sender_no, "Confirm": "Yes"}
    rslt = flask_app.put(add_confirm_api, headers=HEADERS, data=json.dumps(payload))
    assert not rslt.data == b"Sender MSISDN format is not correct"
    assert not rslt.data == b"Primary MSISDN format is not correct"


def test_add_confirm_validations_operator_name(flask_app, db):
    """ Verify that add-confirm api accepts only valid operator name """
    mno_1 = 'j@zz'
    mno_2 = 'operator_name_with_more_than_20_characters'
    mno_3 = 'telenor'
    payload_1 = {"Sender_No": "923468292404", "Operator": mno_1, "Primary_No": "923003294857", "Confirm": "Yes"}
    payload_2 = {"Sender_No": "923468292404", "Operator": mno_2, "Primary_No": "923003294857", "Confirm": "Yes"}
    payload_3 = {"Sender_No": "923468292404", "Operator": mno_3, "Primary_No": "923003294857", "Confirm": "Yes"}
    rslt_1 = flask_app.put(add_confirm_api, headers=HEADERS, data=json.dumps(payload_1))
    rslt_2 = flask_app.put(add_confirm_api, headers=HEADERS, data=json.dumps(payload_2))
    rslt_3 = flask_app.put(add_confirm_api, headers=HEADERS, data=json.dumps(payload_3))
    assert rslt_1.data == b"Operator name is not correct"
    assert rslt_2.data == b"Operator name is not correct"
    assert not rslt_3.data == b"Operator name is not correct"


def test_add_confirm_validations_yes_no(flask_app, db):
    """ Verify that add-confirm api accepts only valid formats of confirmation """
    yes = ['yes', 'Yes', 'YES', 'yEs']
    no = ['no', 'No', 'NO', 'nO']
    for cnfrm in range(0, 4):
        payload_1 = {"Sender_No": "923458179437", "Operator": "telenor",
                     "Primary_No": "923003294857", "Confirm": yes[cnfrm]}
        rslt_1 = flask_app.put(add_confirm_api, headers=HEADERS, data=json.dumps(payload_1))
        if yes[cnfrm] == 'yEs':
            assert rslt_1.data == b"Confirmation is not proprely done"
        else:
            assert not rslt_1.data == b"Confirmation is not proprely done"
        payload_2 = {"Sender_No": "923458179437", "Operator": "telenor",
                     "Primary_No": "923003294857", "Confirm": no[cnfrm]}
        rslt_2 = flask_app.put(add_confirm_api, headers=HEADERS, data=json.dumps(payload_2))
        if no[cnfrm] == 'nO':
            assert rslt_2.data == b"Confirmation is not proprely done"
        else:
            assert not rslt_2.data == b"Confirmation is not proprely done"


def test_add_confirm_missing_parameters(flask_app, db):
    """ Verify that add-confirm api prompts when any parameter is missing """
    payload = [
        {"Sender_No": "", "Operator": "telenor", "Primary_No": "923003294857", "Confirm": "yes"},
        {"Operator": "telenor", "Primary_No": "923003294857", "Confirm": "yes"},
        {"Sender_No": "923458179437", "Operator": "", "Primary_No": "923003294857", "Confirm": "yes"},
        {"Sender_No": "923458179437",  "Primary_No": "923003294857", "Confirm": "yes"},
        {"Sender_No": "923458179437", "Operator": "telenor", "Primary_No": "", "Confirm": "yes"},
        {"Sender_No": "923458179437", "Operator": "telenor", "Confirm": "yes"},
        {"Sender_No": "923458179437", "Operator": "telenor", "Primary_No": "923003294857", "Confirm": ""},
        {"Sender_No": "923458179437", "Operator": "telenor", "Primary_No": "923003294857"}
    ]
    for val in range(0, 8):
        result = flask_app.put(add_confirm_api, headers=HEADERS, data=json.dumps(payload[val]))
        if val == 0 or val == 1:
            assert result.data == b"Sender number is missing in SMS"
        elif val == 2 or val == 3:
            assert result.data == b"Operator name is missing in SMS"
        elif val == 4 or val == 5:
            assert result.data == b"Primary number is missing in SMS"
        elif val == 6 or val == 7:
            assert result.data == b"Confirmation is missing in SMS"


def test_add_confirm_error_400_wrong_api(flask_app, db):
    """ Verify that add-confirm api prompts when Error-400 is occurred """
    payload = {"Sender_No": "923458179437", "Operator": "telenor", "Primary_No": "923003294857", "Confirm": "yes"}
    result = flask_app.put(add_confirm_api, headers=HEADERS, data=payload)
    print(result.data)
    assert result.status_code == 400


def test_add_confirm_error_404_bad_request(flask_app, db):
    """ Verify that add-confirm api prompts when Error-404 occurrs """
    tmp_api = 'api/v1/adddd-cnfrmmmm'
    payload = {"Sender_No": "923458179437", "Operator": "telenor", "Primary_No": "923003294857", "Confirm": "yes"}
    result = flask_app.put(tmp_api, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.status_code == 404


def test_add_confirm_error_405_method_not_allowed(flask_app, db):
    """ Verify that add-confirm api prompts when Error-405 occurrs """
    res1 = flask_app.get(add_confirm_api)
    assert res1.status_code == 405
    res2 = flask_app.post(add_confirm_api)
    assert res2.status_code == 405
    res3 = flask_app.delete(add_confirm_api)
    assert res3.status_code == 405
    res4 = flask_app.patch(add_confirm_api)
    assert res4.status_code == 405


def test_add_confirm_happy_case_yes(flask_app, db, session):
    """ Verify that add-confirm api responds correctly when there is a positive confirmation via secondary pair"""
    complete_db_insertion(session, db, 112, '923004171631', 112, 'Mate-7', 'Huawei', 'ah8de2g1ah', '3G,4G',
                          'NRlhKOrV', 112, '122134435665788')
    first_pair_db_insertion(session, db, 113, '923478190264', 'telenor', 112)
    add_pair_db_insertion(session, db, 114, 113, '923115840917', 112)

    payload = {"Sender_No": "923115840917", "Operator": "zong", "Primary_No": "923478190264", "Confirm": "yes"}
    result = flask_app.put(add_confirm_api, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.status_code == 200


def test_add_confirm_happy_case_no(flask_app, db, session):
    """ Verify that add-confirm api responds correctly when there is a negative confirmation via secondary pair"""
    complete_db_insertion(session, db, 113, '923004171632', 113, 'Mate-X', 'Huawei', 'ah8wwwu1ah', '3G,4G',
                          'VEu0Rar0', 113, '814091435665788')
    first_pair_db_insertion(session, db, 115, '923483190333', 'ufone', 113)
    add_pair_db_insertion(session, db, 116, 115, '923125840817', 113)

    payload = {"Sender_No": "923125840817", "Operator": "zong", "Primary_No": "923483190333", "Confirm": "no"}
    result = flask_app.put(add_confirm_api, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.status_code == 200


def test_add_confirm_functionality_confirmation_via_invalid_msisdn(flask_app, db, session):
    """ Verify that add-confirm api responds correctly when all parameters are valid"""
    complete_db_insertion(session, db, 114, '923218471632', 114, 'Mate-8', 'Huawei', 'AzYTsjwpqah', '3G,4G',
                          'H7Y3UxgQ', 114, '814091435665788')
    first_pair_db_insertion(session, db, 117, '923136467879', 'zong', 114)
    add_pair_db_insertion(session, db, 118, 117, '923125840817', 114)

    payload = {"Sender_No": "923157777777", "Operator": "zong", "Primary_No": "923483190333", "Confirm": "no"}
    result = flask_app.put(add_confirm_api, headers=HEADERS, data=json.dumps(payload))
    assert result.data == b"Confirmation of additional pair request is not done by valid MSISDN"
    payload = {"Sender_No": "923157777777", "Operator": "zong", "Primary_No": "923483190333", "Confirm": "yes"}
    result = flask_app.put(add_confirm_api, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.data == b"Confirmation of additional pair request is not done by valid MSISDN"


def test_add_confirm_functionality_wrong_primary_msisdn(flask_app, db, session):
    """ Verify that add-confirm api responds correctly when all parameters are valid"""
    complete_db_insertion(session, db, 115, '923218471632', 115, 'S7-Galaxy', 'Samsung', 'Y8ArtG61P', '2G,3G,4G',
                          '8nVTYBdm', 115, '318970237766498')
    first_pair_db_insertion(session, db, 119, '923352491076', 'ufone', 115)
    add_pair_db_insertion(session, db, 120, 119, '923016349057', 115)

    payload = {"Sender_No": "923016349057", "Operator": "zong", "Primary_No": "923458333333", "Confirm": "yes"}
    result = flask_app.put(add_confirm_api, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.data == b"Wrong Primary number mentioned in SMS"
