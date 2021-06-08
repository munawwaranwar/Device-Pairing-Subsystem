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


# noinspection PyUnresolvedReferences,PyProtectedMember
from tests._fixtures import *
import json
from app import conf
# noinspection PyProtectedMember
from tests._helpers import *

add_confirm_api = 'api/v1/secondary-confirm'
HEADERS = {'Content-Type': "application/json"}


# noinspection PyUnusedLocal,PyShadowingNames,DuplicatedCode
def test_add_confirm_validations_wrong_secondary_msisdn(flask_app, db):
    """ Verify that secondary-confirm api only accepts valid secondary MSISDNs """

    sender_no = ['9230028460937724', '92321417g9C21', '92345@769#564&8', '923004', '']
    for val in sender_no:
        payload_1 = {"secondary_msisdn": val, "operator": "jazz", "primary_msisdn": "923003294857", "confirm": "Yes"}
        rslt = flask_app.post(add_confirm_api, headers=HEADERS, data=json.dumps(payload_1))
        data = json.loads(rslt.data.decode('utf-8'))

        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['secondary_msisdn'][0] == "MSISDN format is not correct"
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['secondary_msisdn'][0] == "El formato MSISDN no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['secondary_msisdn'][0] == "Format MSISDN tidak benar"

        print("Secondary_MSISDN =", val, " : ", data['message']['secondary_msisdn'][0])


# noinspection PyUnusedLocal,PyShadowingNames,DuplicatedCode
def test_add_confirm_validations_wrong_primary_msisdn(flask_app, db):
    """ Verify that secondary-confirm api doesn't accept invalid primary MSISDNs """

    primary_no = ['9230028460937724', '92321417g9C21', '92345@769#564&8', '923004', '']
    for val in primary_no:
        payload_2 = {"secondary_msisdn": "923003294857", "operator": "jazz", "primary_msisdn": val, "confirm": "Yes"}
        rslt = flask_app.post(add_confirm_api, headers=HEADERS, data=json.dumps(payload_2))
        data = json.loads(rslt.data.decode('utf-8'))

        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['primary_msisdn'][0] == "MSISDN format is not correct"
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['primary_msisdn'][0] == "El formato MSISDN no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['primary_msisdn'][0] == "Format MSISDN tidak benar"

        print("Primary_MSISDN =", val, " : ", data['message']['primary_msisdn'][0])


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_confirm_validations_valid_sender_no(flask_app, db):
    """ Verify that add-confirm api only accepts valid primary & secondary numbers """
    sender_no = '923458179437'
    payload = {"secondary_msisdn": sender_no, "operator": "jazz", "primary_msisdn": sender_no, "confirm": "Yes"}
    rslt = flask_app.post(add_confirm_api, headers=HEADERS, data=json.dumps(payload))
    print(rslt.data)
    data = json.loads(rslt.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert not data == "MSISDN format is not correct"
    elif conf['supported_languages']['default_language'] == 'es':
        assert not data == "El formato MSISDN no es correcto"
    elif conf['supported_languages']['default_language'] == 'id':
        assert not data == "Format MSISDN tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_confirm_validations_operator_name(flask_app, db):
    """ Verify that add-confirm api accepts only valid operator name """
    mno_1 = 'j@zz'
    mno_2 = 'mobile_operator_name_with_more_than_fifty_characters'
    mno_3 = 'telenor'
    payload_1 = {"secondary_msisdn": "923468292404", "operator": mno_1, "primary_msisdn": "923003294857",
                 "confirm": "Yes"}
    payload_2 = {"secondary_msisdn": "923468292404", "operator": mno_2, "primary_msisdn": "923003294857",
                 "confirm": "Yes"}
    payload_3 = {"secondary_msisdn": "923468292404", "operator": mno_3, "primary_msisdn": "923003294857",
                 "confirm": "Yes"}
    rslt_1 = flask_app.post(add_confirm_api, headers=HEADERS, data=json.dumps(payload_1))
    rslt_2 = flask_app.post(add_confirm_api, headers=HEADERS, data=json.dumps(payload_2))
    rslt_3 = flask_app.post(add_confirm_api, headers=HEADERS, data=json.dumps(payload_3))
    data_1 = json.loads(rslt_1.data.decode('utf-8'))
    data_2 = json.loads(rslt_2.data.decode('utf-8'))
    data_3 = json.loads(rslt_3.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert data_1['message']['operator'][0] == "Operator name is not correct"
        assert data_2['message']['operator'][0] == "Operator name is not correct"
        assert not data_3 == "Operator name is not correct"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data_1['message']['operator'][0] == "El nombre del operador no es correcto."
        assert data_2['message']['operator'][0] == "El nombre del operador no es correcto."
        assert not data_3 == "El nombre del operador no es correcto."
    elif conf['supported_languages']['default_language'] == 'id':
        assert data_1['message']['operator'][0] == "Nama operator tidak benar"
        assert data_2['message']['operator'][0] == "Nama operator tidak benar"
        assert not data_3 == "Nama operator tidak benar"

    print("\n", rslt_1.data, "\n", rslt_2.data, "\n", rslt_3.data)


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_confirm_validations_yes_no(flask_app, db):
    """ Verify that add-confirm api accepts only valid formats of confirmation """

    yes = ['yes', 'Yes', 'YES', 'yEs', '']
    no = ['no', 'No', 'NO', 'nO', '']
    msg = ""

    if conf['supported_languages']['default_language'] == 'en':
        msg = "Confirmation String is not correct"
    elif conf['supported_languages']['default_language'] == 'es':
        msg = "La cadena de confirmación no es correcta"
    elif conf['supported_languages']['default_language'] == 'id':
        msg = "String Konfirmasi tidak benar"

    for cnfrm in range(0, 5):
        payload_1 = {"secondary_msisdn": "923458179437", "operator": "telenor",
                     "primary_msisdn": "923003294857", "confirm": yes[cnfrm]}
        rslt_1 = flask_app.post(add_confirm_api, headers=HEADERS, data=json.dumps(payload_1))
        data_1 = json.loads(rslt_1.data.decode('utf-8'))

        if yes[cnfrm] == 'yEs':
            assert data_1['message']['confirm'][0] == msg
        else:
            assert not data_1 == msg
        print("\nConfirmation-String : ", yes[cnfrm], "\nmsg :", data_1)

        payload_2 = {"secondary_msisdn": "923458179437", "operator": "telenor",
                     "primary_msisdn": "923003294857", "confirm": no[cnfrm]}
        rslt_2 = flask_app.post(add_confirm_api, headers=HEADERS, data=json.dumps(payload_2))
        data_2 = json.loads(rslt_1.data.decode('utf-8'))

        if no[cnfrm] == 'nO':
            assert data_2['message']['confirm'][0] == msg
        else:
            assert not rslt_2.data == msg
        print("\nConfirmation-String : ", no[cnfrm], "\nmsg : ", data_2)


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_confirm_missing_parameters(flask_app, db):
    """ Verify that add-confirm api prompts when any parameter is missing """

    payload = [
        {"secondary_msisdn": "923003294857", "operator": "telenor", "confirm": "yes"},
        {"operator": "telenor", "primary_msisdn": "923003294857", "confirm": "yes"},
        {"secondary_msisdn": "923458179437",  "primary_msisdn": "923003294857", "confirm": "yes"},
        {"secondary_msisdn": "923458179437", "operator": "telenor", "primary_msisdn": "923003294857"}
    ]
    for val in range(0, 4):
        result = flask_app.post(add_confirm_api, headers=HEADERS, data=json.dumps(payload[val]))
        print(result.data)
        data = json.loads(result.data.decode('utf-8'))
        if val == 0:
            assert data['message']['primary_msisdn'][0] == "Missing data for required field."
        elif val == 1:
            assert data['message']['secondary_msisdn'][0] == "Missing data for required field."
        elif val == 2:
            assert data['message']['operator'][0] == "Missing data for required field."
        elif val == 3:
            assert data['message']['confirm'][0] == "Missing data for required field."


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_confirm_error_405_method_not_allowed(flask_app, db):
    """ Verify that add-confirm api prompts when Error-405 occurs """

    res1 = flask_app.get(add_confirm_api)
    print("\nHTTP-Method : GET \n msg : ", res1.data)
    assert res1.status_code == 405
    res2 = flask_app.put(add_confirm_api)
    print("HTTP-Method : PUT \n msg : ", res2.data)
    assert res2.status_code == 405
    res3 = flask_app.delete(add_confirm_api)
    print("HTTP-Method : DELETE \n msg : ", res3.data)
    assert res3.status_code == 405
    res4 = flask_app.patch(add_confirm_api)
    print("HTTP-Method : PATCH \n msg : ", res4.data)
    assert res4.status_code == 405


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_confirm_error_404_bad_request(flask_app, db):
    """ Verify that add-confirm api prompts when Error-404 occurs """

    tmp_api = 'api/v1/adddd-cnfrmmmm'
    payload = {"secondary_msisdn": "923458179437", "operator": "telenor", "primary_msisdn": "923003294857",
               "confirm": "yes"}
    result = flask_app.post(tmp_api, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.status_code == 404


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_confirm_happy_case_yes(flask_app, db, session):
    """ Verify that add-confirm api responds correctly when there is a positive confirmation via secondary pair"""

    complete_db_insertion(session, db, 112, '923004171631', 112, 'Mate-7', 'Huawei', 'ah8de2g1ah', '3G,4G',
                          'NRlhKOrV', 112, '122134435665788')
    first_pair_db_insertion(session, db, 113, '923478190264', 'telenor', 112)
    add_pair_db_insertion(session, db, 114, 113, '923115840917', 112)

    payload = {"secondary_msisdn": "923115840917", "operator": "zong", "primary_msisdn": "923478190264",
               "confirm": "yes"}
    result = flask_app.post(add_confirm_api, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.status_code == 200


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_confirm_happy_case_no(flask_app, db, session):
    """ Verify that add-confirm api responds correctly when there is a negative confirmation via secondary pair"""

    complete_db_insertion(session, db, 113, '923004171632', 113, 'Mate-X', 'Huawei', 'ah8wwwu1ah', '3G,4G',
                          'VEu0Rar0', 113, '814091435665788')
    first_pair_db_insertion(session, db, 115, '923483190333', 'ufone', 113)
    add_pair_db_insertion(session, db, 116, 115, '923125840817', 113)

    payload = {"secondary_msisdn": "923125840817", "operator": "zong", "primary_msisdn": "923483190333",
               "confirm": "no"}
    result = flask_app.post(add_confirm_api, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.status_code == 200


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_confirm_functionality_confirmation_via_invalid_msisdn_no(flask_app, db, session):
    """ Verify that add-confirm api responds correctly when confirmation is done by invalid secondary pair with
        Confirmation string "NO"
    """

    complete_db_insertion(session, db, 114, '923218471632', 114, 'Mate-8', 'Huawei', 'AzYTsjwpqah', '3G,4G',
                          'H7Y3UxgQ', 114, '814091435665788')
    first_pair_db_insertion(session, db, 117, '923136467879', 'zong', 114)
    add_pair_db_insertion(session, db, 118, 117, '923125840817', 114)

    payload = {"secondary_msisdn": "923157777777", "operator": "zong", "primary_msisdn": "923136467879",
               "confirm": "no"}
    res1 = flask_app.post(add_confirm_api, headers=HEADERS, data=json.dumps(payload))
    data_1 = json.loads(res1.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert data_1 == "Confirmation of additional pair request is not done by valid MSISDN"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data_1 == "El MSISDN válido no confirma la solicitud de par adicional"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data_1 == "Konfirmasi permintaan pasangan tambahan tidak dilakukan oleh MSISDN yang valid"
    print("\nConfirmation-String : NO , msg : ", res1.data)


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_confirm_functionality_confirmation_via_invalid_msisdn_yes(flask_app, db, session):
    """ Verify that add-confirm api responds correctly when confirmation is done by invalid secondary pair with
        Confirmation string "YES"
    """

    complete_db_insertion(session, db, 116, '923218471632', 116, 'Mate-8', 'Huawei', 'Y7Tffrjw0012h', '3G,4G',
                          'G6dws9m4', 116, '814091435665788')
    first_pair_db_insertion(session, db, 122, '923136467879', 'zong', 116)
    add_pair_db_insertion(session, db, 123, 122, '923125840817', 116)

    payload = {"secondary_msisdn": "923157777777", "operator": "zong", "primary_msisdn": "923136467879",
               "confirm": "yes"}
    res2 = flask_app.post(add_confirm_api, headers=HEADERS, data=json.dumps(payload))
    data_2 = json.loads(res2.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert data_2 == "Confirmation of additional pair request is not done by valid MSISDN"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data_2 == "El MSISDN válido no confirma la solicitud de par adicional"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data_2 == "Konfirmasi permintaan pasangan tambahan tidak dilakukan oleh MSISDN yang valid"
    print("\nConfirmation-String : YES , msg : ", res2.data)


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_confirm_functionality_wrong_primary_msisdn(flask_app, db, session):
    """ Verify that add-confirm api responds correctly when all parameters are valid"""

    complete_db_insertion(session, db, 115, '923218471632', 115, 'S7-Galaxy', 'Samsung', 'Y8ArtG61P', '2G,3G,4G',
                          '8nVTYBdm', 115, '318970237766498')
    first_pair_db_insertion(session, db, 119, '923352491076', 'ufone', 115)
    add_pair_db_insertion(session, db, 120, 119, '923016349057', 115)

    payload = {"secondary_msisdn": "923016349057", "operator": "zong", "primary_msisdn": "923458333333",
               "confirm": "yes"}
    result = flask_app.post(add_confirm_api, headers=HEADERS, data=json.dumps(payload))
    data = json.loads(result.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "Wrong Primary number mentioned in SMS"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "Número primario incorrecto mencionado en SMS"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "Salah nomor Primer yang disebutkan dalam SMS"

    print("\nPrimary_MSISDN : 923458333333 , msg : ", result.data)
