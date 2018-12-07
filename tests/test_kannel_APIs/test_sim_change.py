"""
Unit Test Module for SIM-Change API
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

SIM_CHG_API = 'api/v1/sim-chg'
HEADERS = {'Content-Type': "application/json"}

def test_sim_change_validation_wrong_Sender_No(flask_app, db):
    """ Verify that sim-chg api doesn't accept invalid primary """
    sender_no = ['924006171951', '9230028460937724', '92321417g9C21', '92345@769#564&8', '923004']
    for val in sender_no:
        payload = {"Sender_No": val, "Operator" : "telenor"}
        rslt = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
        assert rslt.data == b"Sender MSISDN format is not correct"


def test_sim_change_validation_valid_Sender_No(flask_app, db):
    """ Verify that sim-chg api only accepts valid sender number"""
    sender_no = '923069590281'
    payload = {"Sender_No": sender_no, "Operator": "jazz"}
    rslt = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
    assert not rslt.data == b"Sender MSISDN format is not correct"


def test_sim_change_validation_operator_name(flask_app, db):
    """ Verify that sim-chg api accepts only valid operator name """
    mno_1 = 'j@zz'
    mno_2 = 'operator_name_with_more_than_20_characters'
    mno_3 = 'telenor'
    payload_1 = {"Sender_No": "923468292404", "Operator": mno_1}
    payload_2 = {"Sender_No": "923468292404", "Operator": mno_2}
    payload_3 = {"Sender_No": "923468292404", "Operator": mno_3}
    rslt_1 = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload_1))
    rslt_2 = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload_2))
    rslt_3 = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload_3))
    assert rslt_1.data == b"operator's name is not correct"
    assert rslt_2.data == b"operator's name is not correct"
    assert not rslt_3.data == b"operator's name is not correct"


def test_sim_change_missing_parameters(flask_app, db):
    """ Verify that sim-chg api prompts when any parameter is missing """
    payload = [
        {"Sender_No": "", "Operator": "telenor"},
        {"Operator": "telenor"},
        {"Sender_No": "923468292404", "Operator": ""},
        {"Sender_No": "923468292404"}

    ]
    for val in range(0,4):
        result = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload[val]))
        if val == 0 or val == 1:
            assert result.data == b"Sender number is missing in SMS"
        elif val == 2 or val == 3:
            assert result.data == b"Operator's name is missing in SMS"


def test_sim_change_error_400_bad_request(flask_app, db):
    """ Verify that sim-chg api prompts when Error-400 is occurred """
    payload = {"Sender_No": "923458179437", "Operator": "telenor"}
    result = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=payload)
    print(result.data)
    assert result.status_code == 400


def test_sim_change_error_404_wrong_api(flask_app, db):
    """ Verify that sim-chg api prompts when Error-404 is occurred """
    tmp_API = 'api/v1/simmmm-chgggg'
    payload = {"Sender_No": "923458179437", "Operator": "telenor"}
    result = flask_app.delete(tmp_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.status_code == 404


def test_sim_change_error_405_method_not_allowed(flask_app, db):
    """ Verify that sim-chg api prompts when Error-405 is occurred """
    res1 = flask_app.get(SIM_CHG_API)
    assert res1.status_code == 405
    res2 = flask_app.post(SIM_CHG_API)
    assert res2.status_code == 405
    res3 = flask_app.put(SIM_CHG_API)
    assert res3.status_code == 405
    res4 = flask_app.patch(SIM_CHG_API)
    assert res4.status_code == 405


def test_sim_change_happy_case(flask_app, db, session):
    """ Verify that sim-chg api responds correctly when all parameters are valid """
    complete_db_insertion(session, db, 411, '923036830442', 411, 'Find-X', 'OPPO', '5RT1qazbh', '3G,4G',
                          'EiYjagYD', 411, '889270911982467')
    first_pair_db_insertion(session, db, 412, '923460192939', 'telenor', 411)
    session.execute(text("""UPDATE public.pairing SET imsi = '410057689234091' WHERE msisdn = '923460192939';"""))
    payload = {"Sender_No": "923460192939", "Operator": "jazz"}
    result = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert  result.data == b"SIM Change request has been registered. The Pair will be active in 24 to 48 hours"


def test_sim_change_functionality_chk_old_and_new_imsis(flask_app, db, session):
    """ Verify that sim-chg api handles old & new IMSIs correctly """
    complete_db_insertion(session, db, 412, '923047930553', 412, 'F-9', 'OPPO', 'Fd9kLqwV', '3G,4G',
                          'gDd7XsL4', 412, '910223945867106')
    first_pair_db_insertion(session, db, 413, '923155406922', 'zong', 412)
    imsi = '410042233445566'
    session.execute(text("""UPDATE public.pairing SET imsi = '{}' WHERE msisdn = '923155406922';""".format(imsi)))
    payload = {"Sender_No": "923155406922", "Operator": "warid"}
    result = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert  result.data == b"SIM Change request has been registered. The Pair will be active in 24 to 48 hours"
    qry = session.execute(text("""SELECT * FROM pairing WHERE msisdn = '923155406922'; """)).fetchone()
    print("old imsi = ",qry.old_imsi)
    print("new imsi = ", qry.imsi)
    assert qry.old_imsi == imsi
    assert qry.imsi == None


def test_sim_change_functionality_wrong_sender_no(flask_app,db,session):
    """ Verify that sim-chg api detects wrong Sender MSISDN """
    complete_db_insertion(session, db, 413, '923057930229', 413, 'MI MIX 2S ', 'XIAOMI', 'SN1i9KpW', '3G,4G',
                          '892jeM42', 413, '910223947111222')
    first_pair_db_insertion(session, db, 414, '923138191645', 'zong', 413)
    payload = {"Sender_No": "923113306922", "Operator": "ufone"}
    result = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.data == b"MSISDN (923113306922) is not existed in any pair"


def test_sim_change_functionality_request_from_unconfirmed_sec_pair(flask_app,db,session):
    """ Verify that sim-chg api can cater request from confirmed secondary pair as well """
    complete_db_insertion(session, db, 414, '923057930229', 414, 'PocoPhone ', 'XIAOMI', 'Sb9i9]]KpW', '3G,4G',
                          'QFIceP39', 414, '910223947111444')
    first_pair_db_insertion(session, db, 415, '923338791465', 'ufone', 414)
    add_pair_db_insertion(session, db, 417, 416, '923125840917', 414)
    payload = {"Sender_No": "923125840917", "Operator": "zong"}
    result = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.data == b"MSISDN (923125840917) is not existed in any pair"


def test_sim_change_functionality_request_from_confirmed_sec_pair(flask_app,db,session):
    """ Verify that sim-chg api can cater request from confirmed secondary pair as well """
    complete_db_insertion(session, db, 415, '923089923776', 415, 'Nokia-4 ', 'NOKIA', 'Sbqa7KpW', '2G,3G,4G',
                          'Ox4sTcst', 415, '910223947333344')
    first_pair_db_insertion(session, db, 418, '923216754889', 'warid', 415)
    add_pair_db_insertion(session, db, 419, 418, '923125840917', 415)
    add_pair_confrm_db_insertion(session, db, '923125840917', 418, 'zong')
    payload = {"Sender_No": "923125840917", "Operator": "zong"}
    result = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.data == b"SIM Change request has been registered. The Pair will be active in 24 to 48 hours"
