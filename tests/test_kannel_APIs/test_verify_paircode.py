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

VFY_PAIRCODE_API = 'api/v1/vfy-paircode'
HEADERS = {'Content-Type': "application/json"}


# noinspection PyUnusedLocal,PyShadowingNames
def test_vfy_paircode_validation_invalid_paircodes(flask_app, db):
    """ Verify that vfy-paircode api doesn't accept invalid pair-code """
    pair_codes = ['pqZTDCgE4', 'KliX6', 'pqZ*C3gE']
    for val in pair_codes:
        url = '{api}?Pair_Code={pc}&IMEI=111111111111111'.format(api=VFY_PAIRCODE_API, pc=val)
        rslt = flask_app.get(url)
        print(rslt.data, val)
        assert rslt.data == b"Pair-Code format is not correct"


# noinspection PyUnusedLocal,PyShadowingNames
def test_vfy_paircode_validation_invalid_imeis(flask_app, db):
    """ Verify that vfy-paircode api doesn't accept invalid imei """
    imei = ['12345', '123456789098765433', '123456acg789098', '111111@#*111111']
    for val in imei:
        url = '{api}?Pair_Code=pqZ4DCgE&IMEI={imei}'.format(api=VFY_PAIRCODE_API, imei=val)
        rslt = flask_app.get(url)
        print(rslt.data, val)
        assert rslt.data == b"IMEI format is not correct"


# noinspection PyUnusedLocal,PyShadowingNames
def test_vfy_paircode_validation_valid_paircode_and_imei(flask_app, db):
    """ Verify that vfy-paircode api doesn't accept invalid imei """
    url = '{api}?Pair_Code=pqZ4DCgE&IMEI=111111111111111'.format(api=VFY_PAIRCODE_API)
    rslt = flask_app.get(url)
    print(rslt.data)
    assert not rslt.data == b"Pair-Code format is not correct"
    assert not rslt.data == b"IMEI format is not correct"


# noinspection PyUnusedLocal,PyShadowingNames
def test_vfy_paircode_missing_parameters(flask_app, db):
    """ Verify that vfy-paircode api prompts when any parameter is missing """
    url_1 = '{api}?Pair_Code=&IMEI=111111111111111'.format(api=VFY_PAIRCODE_API)
    url_2 = '{api}?Pair_Code=pqZ4DCgE&IMEI='.format(api=VFY_PAIRCODE_API)
    rslt_1 = flask_app.get(url_1)
    rslt_2 = flask_app.get(url_2)
    print(rslt_1.data, rslt_2.data)
    assert rslt_1.data == b"Pair-Code is missing in SMS"
    assert rslt_2.data == b"IMEI is missing in SMS"


# noinspection PyUnusedLocal,PyShadowingNames
def test_vfy_paircode_error_404_wrong_api(flask_app, db):
    """ Verify that vfy-paircode api prompts when Error-404 is occurred """
    tmp_api = 'api/v1/vfy-paircodeeee'
    url = '{api}?Pair_Code=prU4DCgE&IMEI=111111111111111'.format(api=tmp_api)
    rslt = flask_app.get(url)
    print(rslt.data)
    assert rslt.status_code == 404


# noinspection PyUnusedLocal,PyShadowingNames
def test_vfy_paircode_error_405_method_not_allowed(flask_app, db):
    """ Verify that vfy-paircode api prompts when Error-405 is occurred """
    url = '{api}?Pair_Code=pqZ4zCgE&IMEI=111111111111111'.format(api=VFY_PAIRCODE_API)
    res1 = flask_app.post(url)
    assert res1.status_code == 405
    res2 = flask_app.put(url)
    assert res2.status_code == 405
    res3 = flask_app.delete(url)
    assert res3.status_code == 405
    res4 = flask_app.patch(url)
    assert res4.status_code == 405


# noinspection PyUnusedLocal,PyShadowingNames
def test_vfy_paircode_happy_case(flask_app, db, session):
    """ Verify that vfy-paircode api provides correct pair-code status """
    pair_code = 'PuPnag6D'
    imei = '889270911982467'
    complete_db_insertion(session, db, 511, '923036830442', 511, 'Find-X', 'OPPO', '5RT1qazbh', '3G,4G',
                          pair_code, 511, imei)
    url = '{api}?Pair_Code={pc}&IMEI={imei}'.format(api=VFY_PAIRCODE_API, pc=pair_code, imei=imei)
    result = flask_app.get(url)
    print(result.data)
    assert result.data == b"Pair-Code (PuPnag6D) is active & associated with provided IMEI"


# noinspection PyUnusedLocal,PyShadowingNames
def test_vfy_paircode_functionality_wrong_paircode(flask_app, db, session):
    """ Verify that vfy-paircode api detects wrong pair-code """
    pair_code = 'Y9DwX2OM'
    imei = '928019923475048'
    complete_db_insertion(session, db, 512, '923046831111', 512, 'F-3', 'OPPO', 'U7a2eTazbh', '3G,4G',
                          pair_code, 512, imei)
    url = '{api}?Pair_Code=A1B2C3D4&IMEI={imei}'.format(api=VFY_PAIRCODE_API, imei=imei)
    result = flask_app.get(url)
    print(result.data)
    assert result.data == b"Pair-Code (A1B2C3D4) is not valid or not associated with provided IMEI"


# noinspection PyUnusedLocal,PyShadowingNames
def test_vfy_paircode_functionality_wrong_imei(flask_app, db, session):
    """ Verify that vfy-paircode api detects wrong pair-code """
    pair_code = 'L8vP3haD'
    imei = '928019923475048'
    complete_db_insertion(session, db, 513, '923458877665', 513, 'F-4', 'OPPO', 'Hdg47Ty', '3G,4G',
                          pair_code, 513, imei)
    url = '{api}?Pair_Code={pc}&IMEI=111111111111111'.format(api=VFY_PAIRCODE_API, pc=pair_code)
    result = flask_app.get(url)
    print(result.data)
    assert result.data == b"Pair-Code (L8vP3haD) is not valid or not associated with provided IMEI"
