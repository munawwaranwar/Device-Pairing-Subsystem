"""
Unit Test Module for First-Pair API
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
# noinspection PyProtectedMember
from tests._helpers import *

FIRST_PAIR_API = 'api/v1/first-pair'
HEADERS = {'Content-Type': "application/json"}


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_happy_case(flask_app, db, session):
    """ Verify that first-pair api responds correctly when all parameters are valid"""
    from tests._helpers import complete_db_insertion
    # url = 'api/v1/first-pair'
    # HEADERS = {'Content-Type': "application/json"}
    complete_db_insertion(session, db, 1, '923004171564', 1, 'Note5', 'Samsung', 'abcdefgh', '4G',
                          'OvfT4pGf', 1, '123456789098765')

    payload = {"Pair_Code": 'OvfT4pGf', "Sender_No": "923040519777", "Operator": "jazz"}
    rslt = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    print(rslt.data)
    assert rslt.status_code == 200
    return rslt.data


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_validations_wrong_paircodes(flask_app, db):
    """ Verify that first-pair api accepts only valid pair-code """
    pair_code_1 = 'pqZTDCgE4'
    pair_code_2 = 'KliX6'
    pair_code_3 = 'pqZ*DCgE'
    payload_1 = {"Pair_Code": pair_code_1, "Sender_No": "923040519543", "Operator": "jazz"}
    payload_2 = {"Pair_Code": pair_code_2, "Sender_No": "923040519543", "Operator": "jazz"}
    payload_3 = {"Pair_Code": pair_code_3, "Sender_No": "923040519543", "Operator": "jazz"}
    result_1 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_1))
    result_2 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    result_3 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_3))
    assert result_1.status_code == 422
    assert result_2.data == b"\"Pair-Code format is not correct\""
    assert result_3.data == b"\"Pair-Code format is not correct\""


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_validations_valid_paircode(flask_app, db):
    """ Verify that first-pair api responds corectly when pair-code is valid """
    pair_code = 'pqZ5DCgE'
    payload = {"Pair_Code": pair_code, "Sender_No": "923040519543", "Operator": "jazz"}
    rslt = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    print(rslt.data)
    assert not rslt.data == b"\"Pair-Code format is not correct\""


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_validations_wrong_sender_no(flask_app, db):
    """ Verify that first-pair api accepts only valid Sender_no """
    sender_no = ['924006171951', '9230028460937724', '92321417g9C21', '92345@769#564&8', '923004']
    for val in sender_no:
        payload = {"Pair_Code": "pqZ5DCgE", "Sender_No": val, "Operator": "jazz"}
        rslt = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload))
        assert rslt.data == b"\"Sender MSISDN format is not correct\""


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_validations_valid_sender_no(flask_app, db):
    """ Verify that first-pair api responds corectly when pair-code is valid """
    sender_no = '923008173629'
    payload = {"Pair_Code": "pqZ5DCgE", "Sender_No": sender_no, "Operator": "jazz"}
    rslt = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    print(rslt.data)
    assert not rslt.data == b"\"Sender MSISDN format is not correct\""


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_validations_operator_name(flask_app, db):
    """ Verify that first-pair api accepts only valid pair-code """
    mno_1 = 'j@zz'
    mno_2 = 'telenor'
    payload_1 = {"Pair_Code": "pqZ5DCgE", "Sender_No": "923040519543", "Operator": mno_1}
    payload_2 = {"Pair_Code": "pqZ5DCgE", "Sender_No": "923040519543", "Operator": mno_2}
    result_1 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_1))
    result_2 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    print(result_1.data)
    print(result_2.data)
    assert result_1.data == b"\"MNO's name is not in correct format\""
    assert not result_2.data == b"\"MNO's name is not in correct format\""


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_missing_parameters(flask_app, db):
    """ Verify that first-pair api prompts when any parameter is missing """
    payload_1 = {"Sender_No": "923040519543", "Operator": "jazz"}
    payload_2 = {"Pair_Code": "pqZ5DCgE", "Operator": "jazz"}
    payload_3 = {"Pair_Code": "pqZ5DCgE", "Sender_No": "923040519543"}
    result_1 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_1))
    result_2 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    result_3 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_3))
    assert result_1.data == b"Pair-Code is missing in SMS"
    assert result_2.data == b"sender number is missing in SMS"
    assert result_3.data == b"operator name is missing in SMS"


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_error_400_bad_request(flask_app, db):
    """ Verify that first-pair api prompts when Error-400 is occurred """
    payload = {"Pair_Co": "pqZ5DCgE", "Sender_No": "923040519543", "Operator": "ufone"}
    result = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=payload)
    print(result.data)
    assert result.status_code == 400


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_error_404_wrong_api(flask_app, db):
    """ Verify that first-pair api prompts when Error-404 is occurred """
    tmp_api = 'api/v1/firsttt-pairrrrr'
    payload = {"Pair_Co": "pqZ5DCgE", "Sender_No": "923040519543", "Operator": "telenor"}
    result = flask_app.post(tmp_api, headers=HEADERS, data=payload)
    print(result.data)
    assert result.status_code == 404


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_error_405_method_not_allowed(flask_app, db):
    """ Verify that first-pair api prompts when Error-405 is occurred """
    res1 = flask_app.get(FIRST_PAIR_API)
    assert res1.status_code == 405
    res2 = flask_app.put(FIRST_PAIR_API)
    assert res2.status_code == 405
    res3 = flask_app.delete(FIRST_PAIR_API)
    assert res3.status_code == 405
    res4 = flask_app.patch(FIRST_PAIR_API)
    assert res4.status_code == 405


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_functionality_msisdn_already_exist(flask_app, db, session):
    """ verifying the first-pair doesn't allow duplicated primary MSISDN """
    complete_db_insertion(session, db, 2, '923004171565', 2, 'Note-8', 'Samsung', 'a1b2c3d4e5', '4G', 'AxT3pGf9', 2,
                          '310987923089461')
    complete_db_insertion(session, db, 3, '923458209871', 3, 'Note-9', 'Samsung', 'AaBbCcDdEe', '4G', 'GMiQ0D3w', 3,
                          '310987923089462')

    payload_1 = {"Pair_Code": 'AxT3pGf9', "Sender_No": "923137248795", "Operator": "zong"}
    res_1 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_1))
    print(res_1.data)
    payload_2 = {"Pair_Code": 'GMiQ0D3w', "Sender_No": "923137248795", "Operator": "zong"}
    res_2 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    print(res_2.data)
    assert res_2.data == b"\"MSISDN already exists as Primary-Pair\""


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_functionality_invalid_paircode(flask_app, db, session):
    """ verifying the first-pair doesn't allow duplicated pair-code or paircode not found in DB """
    complete_db_insertion(session, db, 4, '923004171565', 4, 'S-8', 'Samsung', 'a1b2c3d4uu', '3G,4G', 'A1b2C3d4', 4,
                          '310987923083344')
    complete_db_insertion(session, db, 5, '923458209871', 5, 'S-9', 'Samsung', 'AaBbCcDdvv', '3G,4G', 'GMiCTD3w', 5,
                          '310987923086789')

    payload_1 = {"Pair_Code": 'A1b2C3d4', "Sender_No": "923146398444", "Operator": "zong"}
    res_1 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_1))
    print(res_1.data)
    payload_2 = {"Pair_Code": 'A1b2C3d4', "Sender_No": "923218450713", "Operator": "warid"}
    res_2 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    print(res_2.data)
    assert res_2.data == b"\"Pair Code (A1b2C3d4) is not Valid\""
    payload_3 = {"Pair_Code": 'AaBbCcDd', "Sender_No": "923339014785", "Operator": "warid"}
    res_3 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_3))
    print(res_3.data)
    assert res_3.data == b"\"Pair Code (AaBbCcDd) is not Valid\""  # pair-code not in database
