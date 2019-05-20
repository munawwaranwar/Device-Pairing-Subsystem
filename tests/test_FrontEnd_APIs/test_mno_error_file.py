"""
Unit Test Module for MNO-Error-File API
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

# noinspection PyUnresolvedReferences
import json
# noinspection PyUnresolvedReferences,PyProtectedMember
from tests._fixtures import *
# noinspection PyUnresolvedReferences
from io import BytesIO, StringIO

MNO_ERROR_FILE = 'api/v1/mno-error-file'


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_error_file_happy_case(flask_app, session):
    """ Verify that error-file api downloads the error-file successfully"""
    link = "/home/munawar/PycharmProjects/Device-Pairing-Subsystem/downloads/Error-Records_jazz_2019-04-15_16-29-16.csv"
    url = '{api}?url={link}'.format(api=MNO_ERROR_FILE, link=link)
    rs = flask_app.get(url)
    print(rs.data)
    assert rs.status_code == 200


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_error_file_not_found(flask_app, session):
    """ Verify that error-file api prompts when error-file is not found"""
    link = "/var/www/html/dirbs-dps-api-1.0.0/Downloads/Error-Records_telenor_0000-00-00_00-00-00.csv"
    url = '{api}?url={link}'.format(api=MNO_ERROR_FILE, link=link)
    rs = flask_app.get(url)
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert rs.status_code == 422
    assert d1.get('Error') == 'File not found'


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_error_file_missing_url(flask_app, session):
    """ Verify that error-file api prompts when error-file is not found"""
    url = '{api}?url='.format(api=MNO_ERROR_FILE)
    rs = flask_app.get(url)
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert rs.status_code == 422
    assert d1.get('Error') == 'URL is missing'


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_error_file_error_404_wrong_api(flask_app, session):
    """ Verify that error-file api prompts when Error-404 is occurred """
    tmp_api = 'api/v1/mnoo-errorrr-fileee'
    link = "/var/www/html/dirbs-dps-api-1.0.0/Downloads/Error-Records_warid_2018-11-20_09-04-53.csv"
    url = '{api}?url={link}'.format(api=tmp_api, link=link)
    rs = flask_app.get(url)
    print(rs.data)
    assert rs.status_code == 404


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_error_file__error_405_method_not_allowed(flask_app, session):
    """ Verify that mno-first-page api prompts when Error-405 is occurred """
    link = "/var/www/html/dirbs-dps-api-1.0.0/Downloads/Error-Records_warid_2018-11-20_09-04-53.csv"
    url = '{api}?url={link}'.format(api=MNO_ERROR_FILE, link=link)
    res1 = flask_app.post(url)
    assert res1.status_code == 405
    res2 = flask_app.put(url)
    assert res2.status_code == 405
    res3 = flask_app.delete(url)
    assert res3.status_code == 405
    res4 = flask_app.patch(url)
    assert res4.status_code == 405
