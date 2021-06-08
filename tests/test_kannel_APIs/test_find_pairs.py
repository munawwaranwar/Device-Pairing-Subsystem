"""
Copyright (c) 2018-2021 Qualcomm Technologies, Inc.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written permission.
* The origin of this software must not be misrepresented; you must not claim that you wrote the original software.
If you use this software in a product, an acknowledgment is required by displaying the trademark/log as per the details
provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
* Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
* This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.
"""

from app import conf
# noinspection PyUnresolvedReferences,PyProtectedMember
from tests._fixtures import *
# noinspection PyProtectedMember
from tests._helpers import *

FIND_PAIRS_API = 'api/v1/find-pairs'
HEADERS = {'Content-Type': "application/json"}


# noinspection PyUnusedLocal,PyShadowingNames
def test_find_pairs_validation_invalid_sender_no(flask_app, db):
    """ Verify that find-pairs api doesn't accept invalid sender number """
    sender_no = ['9230028460937724', '92321417g9C21', '92345@769#564&8', '923004', '']
    for val in sender_no:
        url = '{api}?primary_msisdn={msisdn}'.format(api=FIND_PAIRS_API, msisdn=val)
        rslt = flask_app.get(url)
        data = json.loads(rslt.data.decode('utf-8'))
        print("\nPrimary_MSISDN :", val, "\n", rslt.data)
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['primary_msisdn'][0] == "MSISDN format is not correct"
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['primary_msisdn'][0] == "El formato MSISDN no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['primary_msisdn'][0] == "Format MSISDN tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_find_pairs_validation_valid_sender_no(flask_app, db):
    """ Verify that find-pairs api only accept valid sender number """
    sender_no = '923002131415'
    url = '{api}?primary_msisdn={msisdn}'.format(api=FIND_PAIRS_API, msisdn=sender_no)
    rslt = flask_app.get(url)
    data = json.loads(rslt.data.decode('utf-8'))
    print(rslt.data)
    if conf['supported_languages']['default_language'] == 'en':
        assert not data == "MSISDN format is not correct"
    elif conf['supported_languages']['default_language'] == 'es':
        assert not data == "El formato MSISDN no es correcto"
    elif conf['supported_languages']['default_language'] == 'id':
        assert not data == "Format MSISDN tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_find_pairs_missing_parameter(flask_app, db):
    """ Verify that find-pairs api prompts when any parameter is missing """
    url = '{api}'.format(api=FIND_PAIRS_API)
    rslt = flask_app.get(url)
    print(rslt.data)
    data = json.loads(rslt.data.decode('utf-8'))
    print("\n", rslt.data)
    assert data['message']['primary_msisdn'][0] == "Missing data for required field."


# noinspection PyUnusedLocal,PyShadowingNames
def test_find_pairs_error_404_wrong_api(flask_app, db):
    """ Verify that find-pairs api prompts when Error-404 is occurred """
    tmp_api = 'api/v1/finddd-pairssss'
    url = '{api}?primary_msisdn=923367790512'.format(api=tmp_api)
    rslt = flask_app.get(url)
    print(rslt.data)
    assert rslt.status_code == 404


# noinspection PyUnusedLocal,PyShadowingNames
def test_find_pairs_error_405_method_not_allowed(flask_app, db):
    """ Verify that find-pairs api prompts when Error-405 is occurred """
    url = '{api}?primary_msisdn=923367790512'.format(api=FIND_PAIRS_API)
    res1 = flask_app.post(url)
    assert res1.status_code == 405
    print("HTTP-Method : POST \n msg : ", res1.data)
    res2 = flask_app.put(url)
    assert res2.status_code == 405
    print("HTTP-Method : PUT \n msg : ", res2.data)
    res3 = flask_app.delete(url)
    assert res3.status_code == 405
    print("HTTP-Method : DELETE \n msg : ", res3.data)
    res4 = flask_app.patch(url)
    assert res4.status_code == 405
    print("HTTP-Method : PATCH \n msg : ", res4.data)


# noinspection PyUnusedLocal,PyShadowingNames
def test_find_pairs_happy_case(flask_app, db, session):
    """ Verify that find-pairs api provides correct details of secondary pairs """
    primary = '923478190264'
    complete_db_insertion(session, db, 611, '923004171631', 611, 'Mate-7', 'Huawei', 'ah8de2g1ah', '3G,4G',
                          'NRlf6OrV', 611, '122134435665788')
    first_pair_db_insertion(session, db, 612, primary, 'telenor', 611)
    add_pair_db_insertion(session, db, 613, 612, '923115840917', 611)
    add_pair_db_insertion(session, db, 614, 612, '923339701290', 611)
    add_pair_confrm_db_insertion(session, db, '923339701290', 612, 'ufone')
    url = '{api}?primary_msisdn={msisdn}'.format(api=FIND_PAIRS_API, msisdn=primary)
    rslt = flask_app.get(url)
    print(rslt.data)
    assert b"MSISDN" in rslt.data
    assert b"Status" in rslt.data


# noinspection PyUnusedLocal,PyShadowingNames
def test_find_pairs_functionality_wrong_primary_no(flask_app, db, session):
    """ Verify that find-pairs api provides detects wrong primary MSISDN in parameters """
    wrong_primary = '923008171615'
    complete_db_insertion(session, db, 612, '923047930553', 612, 'F-9', 'OPPO', 'Fd9kLqwV', '3G,4G',
                          'gB8DGsL4', 612, '910223945867106')
    first_pair_db_insertion(session, db, 615, '923145406911', 'zong', 612)
    add_pair_db_insertion(session, db, 616, 615, '923125840917', 612)
    url = '{api}?primary_msisdn={msisdn}'.format(api=FIND_PAIRS_API, msisdn=wrong_primary)
    rslt = flask_app.get(url)
    print(rslt.data)
    data = json.loads(rslt.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "923008171615 is not registered as Primary-Pair"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "923008171615 no está registrado como par primario"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "923008171615 tidak terdaftar sebagai Pasangan Primer"


# noinspection PyUnusedLocal,PyShadowingNames
def test_find_pairs_functionality_primary_with_no_sec_pairs(flask_app, db, session):
    """ Verify that find-pairs api provides valid response when primary pair has no secndary pairs """
    complete_db_insertion(session, db, 613, '923057930229', 613, 'MI MIX 2S ', 'XIAOMI', 'SN1i9KpW', '3G,4G',
                          '89tjXN42', 613, '910223947111222')
    first_pair_db_insertion(session, db, 617, '923158191645', 'zong', 613)
    url = '{api}?primary_msisdn=923158191645'.format(api=FIND_PAIRS_API)
    rslt = flask_app.get(url)
    print(rslt.data)
    data = json.loads(rslt.data.decode('utf-8'))
    assert data == "No Pair is associated with 923158191645"
