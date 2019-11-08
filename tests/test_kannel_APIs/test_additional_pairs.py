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

ADD_PAIR_API = 'api/v1/secondary-pairs'
HEADERS = {'Content-Type': "application/json"}


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_pair_validations_wrong_primary_msisdn(flask_app, db):
    """ Verify that add-pair api doesn't accept invalid primary number """
    sender_no = ['9230028460937724', '92321417g9C21', '92345@769#564&8', '923004', ""]
    for val in sender_no:
        payload = {"primary_msisdn": val, "secondary_msisdn": "923003294857"}
        rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
        data = json.loads(rslt.data.decode('utf-8'))
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['primary_msisdn'][0] == "MSISDN format is not correct"
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['primary_msisdn'][0] == "El formato MSISDN no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['primary_msisdn'][0] == "Format MSISDN tidak benar"
        print("Primary-MSISDN =", val, " : ", data['message']['primary_msisdn'][0])


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_pair_validations_valid_primary_msisdn(flask_app, db):
    """ Verify that add-pair api only accepts valid primary number """
    sender_no = '923458179437'
    payload = {"primary_msisdn": sender_no, "secondary_msisdn": "923003294857"}
    rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    print(rslt.data)
    data = json.loads(rslt.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert not data == b"MSISDN format is not correct"
    elif conf['supported_languages']['default_language'] == 'es':
        assert not data == "El formato MSISDN no es correcto"
    elif conf['supported_languages']['default_language'] == 'id':
        assert not data == "Format MSISDN tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_pair_validations_wrong_secondary_msisdn(flask_app, db):
    """ Verify that add-pair api doesn't accept invalid primary number """
    msisdn = ['9230028460937724', '923x1417k9C21', '92345@769#564&8', '923004', ""]
    for val in msisdn:
        payload = {"primary_msisdn": "923003294857", "secondary_msisdn": val}
        rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
        data = json.loads(rslt.data.decode('utf-8'))
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['secondary_msisdn'][0] == "MSISDN format is not correct"
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['secondary_msisdn'][0] == "El formato MSISDN no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['secondary_msisdn'][0] == "Format MSISDN tidak benar"
        print("Secondary_MSISDN =", val, " : ", data['message']['secondary_msisdn'][0])


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_pair_validations_valid_secondary_msisdn(flask_app, db):
    """ Verify that add-pair api only accepts valid secondary number """
    sender_no = '923458179437'
    payload = {"primary_msisdn": "923003294857", "secondary_msisdn": sender_no}
    rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    print(rslt.data)
    data = json.loads(rslt.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert not data == b"MSISDN format is not correct"
    elif conf['supported_languages']['default_language'] == 'es':
        assert not data == "El formato MSISDN no es correcto"
    elif conf['supported_languages']['default_language'] == 'id':
        assert not data == "Format MSISDN tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_pair_missing_parameters(flask_app, db):
    """ Verify that add-pair api prompts when any parameter is missing """
    payload_1 = {"secondary_msisdn": "923003294857"}
    payload_2 = {"primary_msisdn": "923003294857"}
    result_1 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_1))
    result_2 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    data_1 = json.loads(result_1.data.decode('utf-8'))
    data_2 = json.loads(result_2.data.decode('utf-8'))
    assert data_1['message']['primary_msisdn'][0] == "Missing data for required field."
    assert data_2['message']['secondary_msisdn'][0] == "Missing data for required field."
    print(data_1, "\n", data_2)


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_pair_error_404_wrong_api(flask_app, db):
    """ Verify that add-pair api prompts when Error-404 is occurred """
    tmp_api = 'api/v1/adddd-pairrr'
    payload = {"primary_msisdn": "923458179437", "secondary_msisdn": "923003294857"}
    result = flask_app.post(tmp_api, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.status_code == 404


# noinspection PyUnusedLocal,PyShadowingNames
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


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_pair_happy_case(flask_app, db, session):
    """ Verify that add-pair api responds correctly when all parameters are valid"""

    complete_db_insertion(session, db, 6, '923004171564', 6, 'Note5', 'Samsung', 'abcdefgh', '3G,4G',
                          'O1G64pGf', 6, '123456789098765')
    first_pair_db_insertion(session, db, 7, '923459146387', 'telenor', 6)
    payload = {"primary_msisdn": "923459146387", "secondary_msisdn": "923117658111"}
    rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    print(rslt.data)
    assert rslt.status_code == 200


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_pair_functionality_wrong_primary_msisdn(flask_app, db, session):
    """ Verify that add-pair api doesn't allow wrong primary MSISDN"""
    payload = {"primary_msisdn": "923348617409", "secondary_msisdn": "923128649052"}
    rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    data = json.loads(rslt.data.decode('utf-8'))
    print(data)
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "Request not made by Primary-Pair or number-to-be-added is Primary number"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "La solicitud no realizada por Par primario o número a agregar es Número primario"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "Permintaan tidak dibuat oleh Pasangan Utama atau nomor yang akan ditambahkan adalah nomor " \
                       "Pratama"


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_pair_functionality_same_primary_and_secondary_msisdn(flask_app, db, session):
    """ Verify that add-pair api api doesn't allow same MSISDN for primary & secondary pairs """
    complete_db_insertion(session, db, 7, '923346181454', 7, 'iphone-max', 'Apple', 'P8go7tdR', '4G',
                          'CuYg4fzD', 7, '987654321012333')
    first_pair_db_insertion(session, db, 9, '923086190554', 'jazz', 7)
    payload = {"primary_msisdn": "923086190554", "secondary_msisdn": "923086190554"}
    rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
    data = json.loads(rslt.data.decode('utf-8'))
    print(data)
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "Request not made by Primary-Pair or number-to-be-added is Primary number"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "La solicitud no realizada por Par primario o número a agregar es Número primario"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "Permintaan tidak dibuat oleh Pasangan Utama atau nomor yang akan ditambahkan adalah nomor " \
                       "Pratama"


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_pair_functionality_already_paired_msisdn(flask_app, db, session):
    """ Verify that add-pair api doesn't allow already paired MSISDN for secondary pair """
    complete_db_insertion(session, db, 8, '923228450691', 8, 'iphone-7', 'Apple', 'ASX0Yh317933', '3G,4G',
                          'ELAI5hqq', 8, '378510893448902')
    first_pair_db_insertion(session, db, 10, '923469988554', 'telenor', 8)
    payload_1 = {"primary_msisdn": "923469988554", "secondary_msisdn": "923086190554"}
    rslt_1 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_1))
    print(rslt_1.data)
    payload_2 = {"primary_msisdn": "923469988554", "secondary_msisdn": "923086190554"}
    rslt_2 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    print(rslt_2.data)
    data = json.loads(rslt_2.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "MSISDN 923086190554 already paired with the device"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "MSISDN 923086190554 ya emparejado con el dispositivo"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "MSISDN 923086190554 sudah dipasangkan dengan perangkat"


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_pair_functionality_pairing_limit(flask_app, db, session):
    """ Verify that add-pair api doesn't allow secondary pairs more than pre-configured limit"""

    complete_db_insertion(session, db, 9, '923238450807', 9, 'REDMI', 'Xiaomi', 'Xr4q9irgTj', '3G,4G',
                          '3Bdzs1sx', 9, '809762846310927')
    first_pair_db_insertion(session, db, 12, '923337788991', 'ufone', 9)

    msisdn = ["923017986111", "923027986222", "923037986333", "923047986444"]
    for val in msisdn:
        payload = {"primary_msisdn": "923337788991", "secondary_msisdn": val}
        rslt = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
        print(rslt.data)
        if conf['supported_languages']['default_language'] == 'en':
            assert not rslt.data == "Pairing limit breached: need to remove any existing pair"
        elif conf['supported_languages']['default_language'] == 'es':
            assert not rslt.data == "Límite de emparejamiento incumplido: elimine primero cualquier par existente"
        elif conf['supported_languages']['default_language'] == 'id':
            assert not rslt.data == "Batas pasangan dilanggar: hilangkan pasangan yang ada terlebih dahulu"

    msisdn_overlimit = '923057986555'
    payload_2 = {"primary_msisdn": "923337788991", "secondary_msisdn": msisdn_overlimit}
    rslt_2 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
    print(rslt_2.data)
    data = json.loads(rslt_2.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "Pairing limit breached: remove any existing pair first"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "Límite de emparejamiento incumplido: elimine primero cualquier par existente"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "Batas pasangan dilanggar: hilangkan pasangan yang ada terlebih dahulu"
    print("msg: ", data)


# noinspection PyUnusedLocal,PyShadowingNames
# def test_add_pair_functionality_single_msisdn_with_many_primary_pairs(flask_app, db, session):
#     """ Verify that add-pair api allows one secondary-MSISDN to pair with many primary-pairs """
#
#     complete_db_insertion(session, db, 80, '923023008790', 80, 'J7prime', 'Samsung', 'Xrt7oPa9u8', '3G,4G',
#                           'F4Rd9iKu', 80, '547190887376107')
#     complete_db_insertion(session, db, 81, '923138301663', 81, 'Nokia8', 'Nokia', 'Qaw34dc7t6y', '4G',
#                           'MIm1auUA', 81, '547190887376108')
#     first_pair_db_insertion(session, db, 88, '923079298687', 'jazz', 80)
#     first_pair_db_insertion(session, db, 89, '923498921445', 'telenor', 81)
#
#     payload = {"primary_msisdn": "923337788991", "secondary_msisdn": "923330005596"}
#     rslt_1 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload))
#     print(rslt_1.data)
#     assert rslt_1.status_code == 200
#
#     data1 = json.loads(rslt_1.data.decode('utf-8'))
#     # print("\nprimary_msisdn: 923049298687", "secondary_msisdn: 923330005596\n msg: ", data1)
#     if conf['supported_languages']['default_language'] == 'en':
#         assert data1 == "Secondary pair is added by 923079298687. Confirmation is awaited from 923330005596"
#     elif conf['supported_languages']['default_language'] == 'es':
#         assert data1 == "El par secundario se agrega por 923079298687. Se espera confirmación de 923330005596"
#     elif conf['supported_languages']['default_language'] == 'id':
#         assert data1 == "Pasangan sekunder ditambahkan oleh 923079298687. Konfirmasi ditunggu dari 923330005596"
#
#     payload_2 = {"primary_msisdn": "923498921445", "secondary_msisdn": "923330005596"}
#     rslt_2 = flask_app.post(ADD_PAIR_API, headers=HEADERS, data=json.dumps(payload_2))
#     assert rslt_2.status_code == 200
#
#     data2 = json.loads(rslt_2.data.decode('utf-8'))
#     print("\nprimary_msisdn: 923468921445", "secondary_msisdn: 923334445556\n msg: ", data2)
#     if conf['supported_languages']['default_language'] == 'en':
#         assert data2 == "Secondary pair is added by 923498921445. Confirmation is awaited from 923330005596"
#     elif conf['supported_languages']['default_language'] == 'es':
#         assert data2 == "El par secundario se agrega por 923498921445. Se espera confirmación de 923330005596"
#     elif conf['supported_languages']['default_language'] == 'id':
#         assert data2 == "Pasangan sekunder ditambahkan oleh 923498921445. Konfirmasi ditunggu dari 923330005596"
