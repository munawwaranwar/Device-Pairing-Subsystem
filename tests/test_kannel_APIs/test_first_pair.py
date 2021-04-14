"""
Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

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

    payload = {"pair_code": 'OvfT4pGf', "sender_no": "923040519777", "operator": "jazz"}
    rslt = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    print(rslt.data)
    assert rslt.status_code == 200
    return rslt.data


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_validations_wrong_paircodes(flask_app, db):
    """ Verify that first-pair api accepts only valid pair-code """

    pair_codes = ["pqZTDCgE4", "KliX6", "pqZ*DCgE", "Ft#9J$k!"]
    for pair_code in pair_codes:
        payload = {"pair_code": pair_code, "sender_no": "923040519543", "operator": "jazz"}
        result = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload))
        print("Pair-Code =", pair_code, " : ", result.data)
        assert result.status_code == 422
        data = json.loads(result.data.decode('utf-8'))
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['pair_code'][0] == "Pair-Code format is not correct"
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['pair_code'][0] == "El formato del código de par no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['pair_code'][0] == "Format Pair-Code tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_validations_valid_paircode(flask_app, db):
    """ Verify that first-pair api responds corectly when pair-code is valid """

    pair_code = 'pqZ5DCgE'
    payload = {"pair_code": pair_code, "sender_no": "923040519543", "operator": "jazz"}
    rslt = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    data = json.loads(rslt.data.decode('utf-8'))
    print(data)
    if conf['supported_languages']['default_language'] == 'en':
        assert not data == "Pair-Code format is not correct"
    elif conf['supported_languages']['default_language'] == 'es':
        assert not data == "El formato del código de par no es correcto"
    elif conf['supported_languages']['default_language'] == 'id':
        assert not data == "Format Pair-Code tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_validations_wrong_sender_no(flask_app, db):
    """ Verify that first-pair api accepts only valid Sender_no """
    sender_no = ['9230028460937724', '92321417g9C21', '92345@769#564&8', '923004']
    for val in sender_no:
        payload = {"pair_code": "pqZ5DCgE", "sender_no": val, "operator": "jazz"}
        rslt = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload))
        assert rslt.status_code == 422
        data = json.loads(rslt.data.decode('utf-8'))
        print("Sender_No =", val, " : ", data['message']['sender_no'][0])
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['sender_no'][0] == "MSISDN format is not correct"
        if conf['supported_languages']['default_language'] == 'es':
            assert data['message']['sender_no'][0] == "El formato MSISDN no es correcto"
        if conf['supported_languages']['default_language'] == 'id':
            assert data['message']['sender_no'][0] == "Format MSISDN tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_validations_valid_sender_no(flask_app, db, session):
    """ Verify that first-pair api responds corectly when sender_no is valid """

    complete_db_insertion(session, db, 999, '923004107404', 999, 'OnePlus5', 'OnePlus', 'abcdef999', '4G',
                          'CACF0999', 999, '111111111111111')
    sender_no = '923008173629'
    payload = {"pair_code": "CACF0999", "sender_no": sender_no, "operator": "jazz"}
    rslt = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    data = json.loads(rslt.data.decode('utf-8'))
    print(data)
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "PairCode CACF0999 is valid and your pair will be added in next 24 to 48 hours"
        assert not data == "MSISDN format is not correct"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "PairCode CACF0999 es válido y su par se agregará en las próximas 24 a 48 horas"
        assert not data == "El formato MSISDN no es correcto"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "PairCode CACF0999 valid dan pasangan Anda akan ditambahkan dalam 24 hingga 48 jam ke depan"
        assert not data == "Format MSISDN tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_validations_operator_name(flask_app, db):
    """ Verify that first-pair api accepts only valid pair-code """

    mno_1 = 'j@zz'
    mno_2 = 'telenor'
    payload_1 = {"pair_code": "pqZ5DCgE", "sender_no": "923040519543", "operator": mno_1}
    payload_2 = {"pair_code": "pqZ5DCgE", "sender_no": "923040519543", "operator": mno_2}
    result_1 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_1))
    result_2 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))

    assert result_1.status_code == 422
    data = json.loads(result_1.data.decode('utf-8'))
    print(result_2.data)
    print("Operator =", mno_1, " : ", data['message']['operator'][0])
    if conf['supported_languages']['default_language'] == 'en':
        assert data['message']['operator'][0] == "Operator name is not correct"
        assert not result_2.data == b"\"Operator name is not correct\""
    if conf['supported_languages']['default_language'] == 'es':
        assert data['message']['operator'][0] == "El nombre del operador no es correcto."
        assert not result_2.data == b"\"El nombre del operador no es correcto.\""
    if conf['supported_languages']['default_language'] == 'id':
        assert data['message']['operator'][0] == "Nama operator tidak benar"
        assert not result_2.data == b"\"Nama operator tidak benar\""


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_missing_parameters(flask_app, db):
    """ Verify that first-pair api prompts when any parameter is missing """
    payload_1 = {"sender_no": "923040519543", "operator": "jazz"}
    payload_2 = {"pair_code": "pqZ5DCgE", "operator": "jazz"}
    payload_3 = {"pair_code": "pqZ5DCgE", "sender_no": "923040519543"}
    result_1 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_1))
    result_2 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    result_3 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_3))
    data_1 = json.loads(result_1.data.decode('utf-8'))
    data_2 = json.loads(result_2.data.decode('utf-8'))
    data_3 = json.loads(result_3.data.decode('utf-8'))
    assert data_1['message']['pair_code'][0] == "Missing data for required field."
    assert result_1.status_code == 422
    assert data_2['message']['sender_no'][0] == "Missing data for required field."
    assert result_2.status_code == 422
    assert data_3['message']['operator'][0] == "Missing data for required field."
    assert result_3.status_code == 422
    print(result_1.data)
    print(result_2.data)
    print(result_3.data)


# noinspection PyUnusedLocal,PyShadowingNames
def test_first_pair_error_404_wrong_api(flask_app, db):
    """ Verify that first-pair api prompts when Error-404 is occurred """
    tmp_api = 'api/v1/firsttt-pairrrrr'
    payload = {"pair_code": "pqZ5DCgE", "sender_no": "923040519543", "operator": "telenor"}
    result = flask_app.post(tmp_api, headers=HEADERS, data=payload)
    print(result.data)
    assert result.status_code == 404


# noinspection PyUnusedLocal,PyShadowingNames,DuplicatedCode
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


# noinspection PyUnusedLocal,PyShadowingNames,DuplicatedCode
def test_first_pair_functionality_msisdn_already_exist(flask_app, db, session):
    """ verifying the first-pair doesn't allow duplicated primary MSISDN """
    complete_db_insertion(session, db, 2, '923004171565', 2, 'Note-8', 'Samsung', 'a1b2c3d4e5', '4G', 'AxT3pGf9', 2,
                          '310987923089461')
    complete_db_insertion(session, db, 3, '923458209871', 3, 'Note-9', 'Samsung', 'AaBbCcDdEe', '4G', 'GMiQ0D3w', 3,
                          '310987923089462')

    payload_1 = {"pair_code": 'AxT3pGf9', "sender_no": "923137248795", "operator": "zong"}
    res_1 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_1))
    print(res_1.data)
    payload_2 = {"pair_code": 'GMiQ0D3w', "sender_no": "923137248795", "operator": "zong"}
    res_2 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    print(res_2.data)
    if conf['supported_languages']['default_language'] == 'en':
        assert res_2.data == b"\"MSISDN already exists as Primary-Pair\""
    elif conf['supported_languages']['default_language'] == 'es':
        assert res_2.data == b"\"MSISDN ya existe como par primario\""
    elif conf['supported_languages']['default_language'] == 'id':
        assert res_2.data == b"\"MSISDN sudah ada sebagai Pasangan Primer\""


# noinspection PyUnusedLocal,PyShadowingNames,DuplicatedCode
def test_first_pair_functionality_invalid_paircode(flask_app, db, session):
    """ verifying the first-pair doesn't allow invalid pair-code or paircode not found in DB """
    complete_db_insertion(session, db, 4, '923004171565', 4, 'S-8', 'Samsung', 'a1b2c3d4uu', '3G,4G', 'A1b2C3d4', 4,
                          '310987923083344')
    complete_db_insertion(session, db, 5, '923458209871', 5, 'S-9', 'Samsung', 'AaBbCcDdvv', '3G,4G', 'GMiCTD3w', 5,
                          '310987923086789')

    payload_1 = {"pair_code": 'A1b2C3d4', "sender_no": "923146398444", "operator": "zong"}
    res_1 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_1))
    print(res_1.data)

    payload_2 = {"pair_code": 'A1b2C3d4', "sender_no": "923218450713", "operator": "warid"}
    res_2 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    data_2 = json.loads(res_2.data.decode('utf-8'))
    print(data_2)
    if conf['supported_languages']['default_language'] == 'en':
        assert data_2 == "Pair Code A1b2C3d4 is not Valid"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data_2 == "El código de par A1b2C3d4 no es válido"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data_2 == "Kode Pair A1b2C3d4 Tidak Valid"

    payload_3 = {"pair_code": 'AaBbCcDd', "sender_no": "923339014785", "operator": "warid"}
    res_3 = flask_app.post(FIRST_PAIR_API, headers=HEADERS, data=json.dumps(payload_3))
    data_3 = json.loads(res_3.data.decode('utf-8'))
    print(res_3.data)
    if conf['supported_languages']['default_language'] == 'en':
        assert data_3 == "Pair Code AaBbCcDd is not Valid"   # pair-code not in database
    elif conf['supported_languages']['default_language'] == 'es':
        assert data_3 == "El código de par AaBbCcDd no es válido"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data_3 == "Kode Pair AaBbCcDd Tidak Valid"
