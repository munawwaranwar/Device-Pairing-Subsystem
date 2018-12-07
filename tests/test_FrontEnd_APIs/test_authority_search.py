"""
Unit Test Module for Authority-Search API
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
from tests._helpers import *
import json

ATHTY_SEARCH = 'api/v1/authority-search'
HEADERS = {'Content-Type': "application/json"}

def test_athty_search_happy_case(flask_app, db, session):
    """ Verify that athty-serach provides correct search result """
    athty_search_db_insertion(session, db, 701, '923145309696', 701, 'Note5', 'Samsung', '1234GHb4y', '3G,4G',
                          'g8qquEVQ', 701, ['111111111111111'],"20:AB:56:AF:44:AD")
    payload = athty_search_payload(1,5,"111111111111111","20:AB:56:AF:44:AD","1234GHb4y","923145309696")
    rs = flask_app.post(ATHTY_SEARCH, headers=HEADERS, data=json.dumps(payload))
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert rs.status_code == 200


def test_athty_search_functionality_missing_parameters(flask_app, db, session):
    """ Verify that athty-serach supports search by any parameter """
    athty_search_db_insertion(session, db, 702, '923145309696', 702, 'F-6', 'OPPO', '1234GHAAA', '4G',
                          'kyDCAmL1', 702, ['222222222222222'], "20:AB:5C:AF:44:AD")
    for val in range(1,5):
        payload = athty_search_payload(1, 5, "222222222222222", "20:AB:5C:AF:44:AD", "1234GHAAA", "923145309696", val)
        rs = flask_app.post(ATHTY_SEARCH, headers=HEADERS, data=json.dumps(payload))
        d1 = json.loads(rs.data.decode('utf-8'))
        print(d1)
        assert rs.status_code == 200


def test_athty_search_functionality_single_parameter_search(flask_app, db, session):
    """ Verify that athty-serach api supports search by single parameter as well"""
    athty_search_db_insertion(session, db, 703, '923006819263', 703, 'RedMi', 'Xiamo', 'U87Hsr', '3G,4G',
                          'QBADXNGZ', 703, ['333333333333333'], "F0:CB:AD:EF:84:FD")
    for val in range(5, 9):
        payload = athty_search_payload(1, 5, "333333333333333", "F0:CB:AD:EF:84:FD", "U87Hsr", "923006819263", val)
        rs = flask_app.post(ATHTY_SEARCH, headers=HEADERS, data=json.dumps(payload))
        d1 = json.loads(rs.data.decode('utf-8'))
        print(d1)
        assert rs.status_code == 200


def test_athty_search_functionality_no_search_parameter(flask_app,db,session):
    """ to check the response of athty-serach api when no search parameter is provided"""
    athty_search_db_insertion(session, db, 704, '923218965339', 704, 'Nokia-8', 'NOKIA', '0oa36Th7Fe', '3G,4G',
                          'm9p4dViX', 704, ['444444444444444'], "78:C3:AD:54:84:FD")
    payload = athty_search_payload(1, 5, "444444444444444", "78:C3:AD:54:84:FD", "0oa36Th7Fe", "923218965339", 9)
    rs = flask_app.post(ATHTY_SEARCH, headers=HEADERS, data=json.dumps(payload))
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert rs.status_code == 200


def test_athty_search_functionality_wrong_search_parameter(flask_app,db,session):
    """ to check the response of athty-serach api when wrong search parameters are provided"""
    athty_search_db_insertion(session, db, 705, '(23457091287', 705, 'Nokia-2', 'NOKIA', 'Kj8sR56h', '3G,4G',
                          'HP0nCrc9', 705, ['555555555555555'], "AD:C3:99:54:84:88")
    payload = athty_search_payload(1, 5, "545454545454545", "12:C3:34:54:56:78", "a1b2c3d4", "923149988770")
    rs = flask_app.post(ATHTY_SEARCH, headers=HEADERS, data=json.dumps(payload))
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert rs.status_code == 200


def test_athty_search_functionality_grouped_imeis(flask_app,db,session):
    """ Verify that athty-serach api groups IMEIs for single search result"""
    imei = ['555555555555555','666666666666666']
    athty_search_db_insertion(session, db, 706, '923457091247', 706, 'Nokia-2', 'NOKIA', 'G6Tre4kl', '3G,4G',
                          'FrfxlfLk', 706, imei, "AD:C3:99:54:84:88")
    payload = athty_search_payload(1, 5, "555555555555555", "AD:C3:99:54:84:88", "G6Tre4kl", "923457091287",6)
    rs = flask_app.post(ATHTY_SEARCH, headers=HEADERS, data=json.dumps(payload))
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert rs.status_code == 200


def test_athty_search_validations_invalid_mac(flask_app, db):
    """Verify that athty-serach api doesn't allow invalid MAC"""
    mac = ['T~68_F*eP`q', 'K0@2a6!M04$']
    for val in mac:
        payload = athty_search_payload(1, 5, "545454545454545", val, "Kj8sw5ry6h", "923149988990")
        rs = flask_app.post(ATHTY_SEARCH, headers=HEADERS, data=json.dumps(payload))
        assert rs.status_code == 422
        d1 = json.loads(rs.data.decode('utf-8'))
        print(d1,val)
        assert d1.get('Error') == 'MAC format is not correct'


def test_athty_search_validations_invalid_serial_no(flask_app, db):
    """Verify that athty-serach api doesn't allow invalid serial number"""
    serial = ['$erI@||n<>?b#', 'G&!@6!T04$']
    for val in serial:
        payload = athty_search_payload(1, 5, "545454545454545", "FE:C3:AD:54:BC:88", val, "923149988990")
        rs = flask_app.post(ATHTY_SEARCH, headers=HEADERS, data=json.dumps(payload))
        assert rs.status_code == 422
        d1 = json.loads(rs.data.decode('utf-8'))
        print(d1,val)
        assert d1.get('Error') == 'Serial-Number format is not correct'


def test_athty_search_validations_invalid_contact_no(flask_app, db):
    """Verify that athty-serach api doesn't allow invalid contact number"""
    contact = ['30a21D19x4', '30@216!904$']
    for val in contact:
        payload = athty_search_payload(1, 5, "545454545454545", "FE:C3:AD:54:BC:88", "Zxd465ty9", val)
        rs = flask_app.post(ATHTY_SEARCH, headers=HEADERS, data=json.dumps(payload))
        assert rs.status_code == 422
        d1 = json.loads(rs.data.decode('utf-8'))
        print(d1,val)
        assert d1.get('Error') == 'Contact-MSISDN format is not correct'


def test_athty_search_validations_invalid_imei(flask_app, db):
    """Verify that athty-serach api doesn't allow invalid contact number"""
    imei = ["313789$", "31!937A6%81478C5", "31678@8&909*1#6", "7~b9{f1a7,d|9?c8)3/e"]
    for val in imei:
        payload = athty_search_payload(1, 5, val, "FE:C3:AD:54:BC:88", "Zxd465ty9", "923006763650")
        rs = flask_app.post(ATHTY_SEARCH, headers=HEADERS, data=json.dumps(payload))
        assert rs.status_code == 422
        d1 = json.loads(rs.data.decode('utf-8'))
        print(d1,val)
        assert d1.get('Error') == 'IMEI format is not correct'


def test_athty_search_validations_invalid_start_limit(flask_app, db):
    """Verify that athty-serach api doesn't allow invalid contact number"""
    payload = athty_search_payload('F', '$', "123456789098765", "FE:C3:AD:54:BC:88", "Zxd465ty9", "923006763650")
    rs = flask_app.post(ATHTY_SEARCH, headers=HEADERS, data=json.dumps(payload))
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert d1.get('Error') == 'Start or Limit is not integer'


def test_athty_search_validations_invalid_search_arguments(flask_app, db):
    """Verify that athty-serach api doesn't allow invalid Search Arguments"""
    payload = athty_search_payload(1, 5, "123456789098765", "FE:C3:AD:54:BC:88", "Zxd465ty9", "923006763650", 10)
    rs = flask_app.post(ATHTY_SEARCH, headers=HEADERS, data=json.dumps(payload))
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert d1.get('Error') == "Search Arguments is not correct"

def test_athty_search_error__404_wrong_api(flask_app, db):
    """ Verify that athty-serach api prompts when Error-400 is occurred """
    tmp_API = 'api/v1/authorityyyy-searchhhh'
    payload = athty_search_payload(1, 5, "111111111111111", "20:AB:56:AF:44:AD", "1234GHb4y", "923145309696")
    rs = flask_app.post(tmp_API, headers=HEADERS, data=json.dumps(payload))
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert rs.status_code == 404


def test_athty_search_error_405_method_not_allowed(flask_app, db):
    """ Verify that athty-serach api prompts when Error-405 is occurred """
    res1 = flask_app.get(ATHTY_SEARCH)
    assert res1.status_code == 405
    res2 = flask_app.put(ATHTY_SEARCH)
    assert res2.status_code == 405
    res3 = flask_app.delete(ATHTY_SEARCH)
    assert res3.status_code == 405
    res4 = flask_app.patch(ATHTY_SEARCH)
    assert res4.status_code == 405
