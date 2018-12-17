"""
Unit Test Module for Additional-Pairs API
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

ADD_PAIR_API = 'api/v1/add-pair'
HEADERS = {'Content-Type': "application/json"}


def test_add_pair_validations_wrong_sender_no(flask_app, db):
    """ Verify that add-pair api doesn't accept invalid primary number """
    sender_no = ['924006171951', '9230028460937724', '92321417g9C21', '92345@769#564&8', '923004']
    for val in sender_no:
        payload = {"Sender_No": val, "MSISDN": "923003294857"}
        rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
        assert rslt.data == b"Primary MSISDN format is not correct"


def test_add_pair_validations_valid_sender_no(flask_app, db):
    """ Verify that add-pair api only accepts valid primary number """
    sender_no = '923458179437'
    payload = {"Sender_No": sender_no, "MSISDN": "923003294857"}
    rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    assert not rslt.data == b"Primary MSISDN format is not correct"


def test_add_pair_validations_wrong_msisdn(flask_app, db):
    """ Verify that add-pair api doesn't accept invalid primary number """
    msisdn = ['924006171951', '9230028460937724', '92321417g9C21', '92345@769#564&8', '923004']
    for val in msisdn:
        payload = {"Sender_No": "923003294857", "MSISDN": val}
        rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
        assert rslt.data == b"Secondary MSISDN format is not correct"


def test_add_pair_validations_valid_msisdn(flask_app, db):
    """ Verify that add-pair api only accepts valid secondary number """
    sender_no = '923458179437'
    payload = {"Sender_No": "923003294857", "MSISDN": sender_no}
    rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    assert not rslt.data == b"Primary MSISDN format is not correct"


def test_add_pair_missing_parameters(flask_app, db):
    """ Verify that add-pair api prompts when any parameter is missing """
    payload_1 = {"Sender_No": "", "MSISDN": "923003294857"}
    payload_2 = {"MSISDN": "923003294857"}
    payload_3 = {"Sender_No": "923003294857", "MSISDN": ""}
    payload_4 = {"Sender_No": "923003294857"}
    result_1 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_1))
    result_2 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    result_3 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_3))
    result_4 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_4))
    assert result_1.data == b"primary number is missing in SMS"
    assert result_2.data == b"primary number is missing in SMS"
    assert result_3.data == b"secondary number is missing in SMS"
    assert result_4.data == b"secondary number is missing in SMS"


def test_add_pair_error_400_bad_request(flask_app, db):
    """ Verify that add-pair api prompts when Error-400 is occurred """
    payload = {"Sender_No": "923458179437", "MSISDN": "923003294857"}
    result = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=payload)
    print(result.data)
    assert result.status_code == 400


def test_add_pair_error_404_wrong_api(flask_app, db):
    """ Verify that add-pair api prompts when Error-404 is occurred """
    tmp_api = 'api/v1/adddd-pairrr'
    payload = {"Sender_No": "923458179437", "MSISDN": "923003294857"}
    result = flask_app.post(tmp_api, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.status_code == 404


def test_add_pair_error_405_method_not_allowed(flask_app, db):
    """ Verify that add-pair api prompts when Error-405 is occurred """
    res1 = flask_app.get(ADD_PAIR_API)
    assert res1.status_code == 405
    res2 = flask_app.put(ADD_PAIR_API)
    assert res2.status_code == 405
    res3 = flask_app.delete(ADD_PAIR_API)
    assert res3.status_code == 405
    res4 = flask_app.patch(ADD_PAIR_API)
    assert res4.status_code == 405


def test_add_pair_happy_case(flask_app, db, session):
    """ Verify that add-pair api responds correctly when all parameters are valid"""
    complete_db_insertion(session, db, 6, '923004171564', 6, 'Note5', 'Samsung', 'abcdefgh', '3G,4G',
                          'O1G64pGf', 6, '123456789098765')
    first_pair_db_insertion(session, db, 7, '923459146387', 'telenor', 6)

    payload = {"Sender_No": "923459146387", "MSISDN": "923117658111"}
    rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    print(rslt.data)
    assert rslt.status_code == 200


def test_add_pair_functionality_wrong_primary_msisdn(flask_app, db, session):
    """ Verify that add-pair api doesn't allow wrong primary MSISDN"""
    payload = {"Sender_No": "923348617409", "MSISDN": "923128649052"}
    rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    print(rslt.data)
    assert rslt.data == b"Request not made by Primary-Pair or number-to-be-added is Primary number"


def test_add_pair_functionality_same_primary_and_secondary_msisdn(flask_app, db, session):
    """ Verify that add-pair api api doesn't allow same MSISDN for primary & secondary pairs """
    complete_db_insertion(session, db, 7, '923346181454', 7, 'iphone-max', 'Apple', 'P8go7tdR', '4G',
                          'CuYg4fzD', 7, '987654321012333')
    first_pair_db_insertion(session, db, 9, '923086190554', 'jazz', 7)
    # here 3 is pairing-id because 2 is already used for secondary pair in happy case
    payload = {"Sender_No": "923086190554", "MSISDN": "923086190554"}
    rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    print(rslt.data)
    assert rslt.data == b"Request not made by Primary-Pair or number-to-be-added is Primary number"


def test_add_pair_functionality_already_paired_msisdn(flask_app, db, session):
    """ Verify that add-pair api doesn't allow already paired MSISDN for secondary pair """
    complete_db_insertion(session, db, 8, '923228450691', 8, 'iphone-7', 'Apple', 'ASX0Yh317933', '3G,4G',
                          'ELAI5hqq', 8, '378510893448902')
    first_pair_db_insertion(session, db, 10, '923469988554', 'telenor', 8)
    payload_1 = {"Sender_No": "923469988554", "MSISDN": "923086190554"}
    rslt_1 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_1))
    print(rslt_1.data)
    payload_2 = {"Sender_No": "923469988554", "MSISDN": "923086190554"}
    rslt_2 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    print(rslt_2.data)
    assert rslt_2.data == b"MSISDN (923086190554)already paired with the device"


def test_add_pair_functionality_pairing_limit(flask_app, db, session):
    """ Verify that add-pair api doesn't allow secondary pairs more than pre-configured limit"""
    complete_db_insertion(session, db, 9, '923238450807', 9, 'REDMI', 'Xiaomi', 'Xr4q9irgTj', '2G,3G,4G',
                          '3Bdzs1sx', 9, '809762846310927')
    first_pair_db_insertion(session, db, 12, '923337788991', 'ufone', 9)

    msisdn = ["923017986111", "923027986222", "923037986333", "923047986444"]
    for val in msisdn:
        payload = {"Sender_No": "923337788991", "MSISDN": val}
        rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
        print(rslt.data)
        assert not rslt.data == b"Pairing limit breached: need to remove any existing pair"

    msisdn_overlimit = '923057986555'
    payload_2 = {"Sender_No": "923337788991", "MSISDN": msisdn_overlimit}
    rslt_2 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    print(rslt_2.data)
    assert rslt_2.data == b"Pairing limit breached: need to remove any existing pair"


def test_add_pair_functionality_single_secondary_msisdn_many_primary_pairs(flask_app, db, session):
    """ Verify that add-pair api allows one secondary-MSISDN to pair with many primary-pairs """
    complete_db_insertion(session, db, 10, '923024455667', 10, 'J7-prime', 'Samsung', 'Xrt7oPa9', '3G,4G',
                          'DvY5wPZb', 10, '547190887376107')
    complete_db_insertion(session, db, 11, '923033981065', 11, 'Nokia-8', 'Nokia', 'Qaw34dc6y', '2G,3G,4G',
                          'MIm1auUA', 11, '547190887376107')
    first_pair_db_insertion(session, db, 26, '923049298687', 'jazz', 10)
    first_pair_db_insertion(session, db, 28, '923468921445', 'telenor', 11)

    payload_1 = {"Sender_No": "923049298687", "MSISDN": "923334445556"}
    rslt_1 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_1))
    print(rslt_1.data)
    assert rslt_1.data == b"Secondary pair is added by (923049298687). Confirmation is awaited from (923334445556)"

    payload_2 = {"Sender_No": "923468921445", "MSISDN": "923334445556"}
    rslt_2 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    print(rslt_2.data)
    assert rslt_2.data == b"Secondary pair is added by (923468921445). Confirmation is awaited from (923334445556)"
