"""
Unit Test Module for MNO-First-Page API
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


MNO_FIRST_PAGE = 'api/v1/mno-first-page'
HEADERS = {'Content-Type': "application/json"}


def test_mno_first_page_happy_case_multiple_record(flask_app,session,db):
    """ Verify that mno-first-page api provides correct results """
    owner = ['923001111111','923002222222','923003333333','923004444444']
    pair_code = ['xGnTrInE','z3fQp3X7','3Bdzs1sx','JM7Bt9QX']
    primary = ['923458888111','923458888222','923458888333','923458888444']
    secondary = ['923479999111','923479999222','923479999333','923479999444']
    dev_id = 2000
    pair_id = 2000
    cnt = 0
    for pri in primary:
        complete_db_insertion(session, db, dev_id, owner[cnt], dev_id, 'Nokia-4 ', 'NOKIA', 'Sbqa7KpW', '2G,3G,4G',
                              pair_code[cnt], dev_id, '810223947333344')
        first_pair_db_insertion(session, db, pair_id, pri, 'telenor', dev_id)
        cnt += 1
        dev_id += 1
        sec_id = pair_id + 1
        for sec in secondary:
            add_pair_db_insertion(session, db, sec_id, pair_id, sec, dev_id-1)
            add_pair_confrm_db_insertion(session, db, sec, pair_id, 'telenor')
            sec_id += 1
        pair_id = sec_id

    url_1 = '{api}?mno=telenor&start=1&limit=20'.format(api=MNO_FIRST_PAGE)
    rs1 = flask_app.get(url_1)
    print(rs1.data)
    assert rs1.status_code == 200
    url_2 = '{api}?mno=telenor&start=2&limit=2'.format(api=MNO_FIRST_PAGE)
    rs2 = flask_app.get(url_2)
    print(rs2.data)
    assert rs2.status_code == 200
    url_3 = '{api}?mno=telenor&start=3&limit=2'.format(api=MNO_FIRST_PAGE)
    rs3 = flask_app.get(url_3)
    print(rs3.data)
    assert rs3.status_code == 200


def test_mno_first_page_happy_case_single_record(flask_app,session,db):
    """ Verify that mno-first-page api provides correct results """
    complete_db_insertion(session, db, 2005, '923089923776', 2005, 'Nokia-8 ', 'NOKIA', 'Sbqa7KpW', '2G,3G,4G',
                          'Ox4KWcst', 2005, '810223947333344')
    first_pair_db_insertion(session, db, 2021, '923216754889', 'warid', 2005)
    add_pair_db_insertion(session, db, 2022, 2021, '923227648092', 2005)
    add_pair_confrm_db_insertion(session, db, '923227648092', 2021, 'warid')

    url = '{api}?mno=warid&start=1&limit=2'.format(api=MNO_FIRST_PAGE)
    rs = flask_app.get(url)
    print(rs.data)
    assert rs.status_code == 200


def test_mno_first_page_missing_parameters(flask_app, session):
    """ Verify that mno-first-page api prompts when any parameter is missing """
    url_1 = '{api}?mno=warid&start=1&limit='.format(api=MNO_FIRST_PAGE)
    url_2 = '{api}?mno=warid&start=&limit=10'.format(api=MNO_FIRST_PAGE)
    url_3 = '{api}?mno=&start=1&limit=10'.format(api=MNO_FIRST_PAGE)
    rs1 = flask_app.get(url_1)
    rs2 = flask_app.get(url_2)
    rs3 = flask_app.get(url_3)
    d1 = json.loads(rs1.data.decode('utf-8'))
    d2 = json.loads(rs2.data.decode('utf-8'))
    d3 = json.loads(rs3.data.decode('utf-8'))
    assert rs1.status_code == 422
    assert rs2.status_code == 422
    assert rs3.status_code == 422
    print(d1,d2,d3)
    assert d1.get('Error') == 'limit is missing'
    assert d2.get('Error') == 'start is missing'
    assert d3.get('Error') == 'operator name is missing'


def test_mno_first_page_validations_start_and_limit(flask_app, session):
    """Verify that mno-first-page api doesn't allow invalid start & limit values"""
    url_1 = '{api}?mno=warid&start=1&limit=a'.format(api=MNO_FIRST_PAGE)
    url_2 = '{api}?mno=warid&start=@&limit=10'.format(api=MNO_FIRST_PAGE)
    rs1 = flask_app.get(url_1)
    rs2 = flask_app.get(url_2)
    d1 = json.loads(rs1.data.decode('utf-8'))
    d2 = json.loads(rs2.data.decode('utf-8'))
    assert rs1.status_code == 422
    assert rs2.status_code == 422
    print(d1, d2)
    assert d1.get('Error') == 'Start or limit is not correct'
    assert d2.get('Error') == 'Start or limit is not correct'


def test_mno_first_page_validations_operator_name(flask_app,session):
    """Verify that mno-first-page api doesn't allow mno names other than mentioned in configuration file"""
    mno = ['jazz', 'telenor', 'zong', 'ufone', 'warid']
    f_mno = ['j@zz','Vodafone','T-Mobile','Orange','wariid']
    for val in mno:
        url = '{api}?mno={operator}&start=1&limit=10'.format(api=MNO_FIRST_PAGE,operator=val)
        rs = flask_app.get(url)
        d1 = json.loads(rs.data.decode('utf-8'))
        print('correct operator name: ' ,val)
        assert not d1.get('Error') == "improper Operator's name provided"
    for v in f_mno:
        f_url = '{api}?mno={operator}&start=1&limit=10'.format(api=MNO_FIRST_PAGE, operator=v)
        f_rs = flask_app.get(f_url)
        f_d1 = json.loads(f_rs.data.decode('utf-8'))
        print(f_d1, v)
        assert f_d1.get('Error') == "improper Operator's name provided"


def test_mno_first_page_functionality_no_records(flask_app,session):
    """Verify that mno-first-page api provides correct response when no operator record found """
    url = '{api}?mno=ufone&start=1&limit=10'.format(api=MNO_FIRST_PAGE)
    rs = flask_app.get(url)
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert d1.get('msg') == "no record found"


def test_mno_first_page_error_404_wrong_api(flask_app, session):
    """ Verify that mno-first-page api prompts when Error-404 is occurred """
    tmp_API = 'api/v1/mnooo-firstttt-pageeee'
    url = '{api}?mno=jazz&start=1&limit=10'.format(api=tmp_API)
    rs = flask_app.get(url)
    print(rs.data)
    assert rs.status_code == 404


def test_mno_first_page_error_405_method_not_allowed(flask_app, session):
    """ Verify that mno-first-page api prompts when Error-405 is occurred """
    url = '{api}?mno=jazz&start=1&limit=10'.format(api=MNO_FIRST_PAGE)
    res1 = flask_app.post(url)
    assert res1.status_code == 405
    res2 = flask_app.put(url)
    assert res2.status_code == 405
    res3 = flask_app.delete(url)
    assert res3.status_code == 405
    res4 = flask_app.patch(url)
    assert res4.status_code == 405