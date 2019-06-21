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


# noinspection PyUnresolvedReferences
import json
# noinspection PyUnresolvedReferences,PyProtectedMember
from tests._fixtures import *
# noinspection PyUnresolvedReferences
from io import BytesIO, StringIO
from app import conf

MNO_ERROR_FILE = 'api/v1/mno-error-file'
FILE_PATH = conf['Download_Path']

# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_error_file_happy_case(flask_app, session):
    """ Verify that error-file api downloads the error-file successfully"""
    link = FILE_PATH + "/Error-Records_jazz_2019-06-13_16-36-37.csv"
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
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('Error') == 'File not found'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('Error') == "Archivo no encontrado"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('Error') == "Berkas tidak ditemukan"


    # noinspection PyUnusedLocal,PyShadowingNames
def test_mno_error_file_missing_url(flask_app, session):
    """ Verify that error-file api prompts when error-file is not found"""
    url = '{api}?url='.format(api=MNO_ERROR_FILE)
    rs = flask_app.get(url)
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert rs.status_code == 422
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('Error') == 'URL is missing'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('Error') == "Falta la URL"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('Error') == "URL tidak ada"


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
