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

SIM_CHG_API = 'api/v1/sim-change'
HEADERS = {'Content-Type': "application/json"}


# noinspection PyUnusedLocal,PyShadowingNames
def test_sim_change_validation_wrong_sender_no(flask_app, db):
    """ Verify that sim-chg api doesn't accept invalid primary """
    sender_no = ['9230028460937724', '92321417g9C21', '92345@769#564&8', '923004', '']
    for val in sender_no:
        payload = {"msisdn": val, "operator": "telenor"}
        rslt = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
        print("\nprimary_msisdn :", val, "\n", rslt.data)
        data = json.loads(rslt.data.decode('utf-8'))
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['msisdn'][0] == "MSISDN format is not correct"
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['msisdn'][0] == "El formato MSISDN no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['msisdn'][0] == "Format MSISDN tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_sim_change_validation_valid_sender_no(flask_app, db):
    """ Verify that sim-chg api only accepts valid sender number"""
    sender_no = '923069590281'
    payload = {"msisdn": sender_no, "operator": "jazz"}
    rslt = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
    print(rslt.data)
    data = json.loads(rslt.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert not data == "MSISDN format is not correct"
    elif conf['supported_languages']['default_language'] == 'es':
        assert not data == "El formato MSISDN no es correcto"
    elif conf['supported_languages']['default_language'] == 'es':
        assert not data == "Format MSISDN tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_sim_change_validation_operator_name(flask_app, db):
    """ Verify that sim-chg api accepts only valid operator name """
    mno_1 = 'j@zz'
    mno_2 = 'mobile_operator_name_with_more_than_fifty_characters'
    mno_3 = 'telenor'
    payload_1 = {"msisdn": "923468292404", "operator": mno_1}
    payload_2 = {"msisdn": "923468292404", "operator": mno_2}
    payload_3 = {"msisdn": "923468292404", "operator": mno_3}
    rslt_1 = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload_1))
    rslt_2 = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload_2))
    rslt_3 = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload_3))
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
def test_sim_change_missing_parameters(flask_app, db):
    """ Verify that sim-chg api prompts when any parameter is missing """
    payload = [
        {"operator": "telenor"},
        {"msisdn": "923468292404"}
    ]
    for val in range(0, 2):
        result = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload[val]))
        print(result.data)
        data = json.loads(result.data.decode('utf-8'))
        if val == 0:
            assert data['message']['msisdn'][0] == "Missing data for required field."
        elif val == 1:
            assert data['message']['operator'][0] == "Missing data for required field."


# noinspection PyUnusedLocal,PyShadowingNames
def test_sim_change_error_404_wrong_api(flask_app, db):
    """ Verify that sim-chg api prompts when Error-404 is occurred """
    tmp_api = 'api/v1/simmmm-chgggg'
    payload = {"msisdn": "923458179437", "operator": "telenor"}
    result = flask_app.delete(tmp_api, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.status_code == 404


# noinspection PyUnusedLocal,PyShadowingNames
def test_sim_change_error_405_method_not_allowed(flask_app, db):
    """ Verify that sim-chg api prompts when Error-405 is occurred """
    res1 = flask_app.get(SIM_CHG_API)
    assert res1.status_code == 405
    print("\nHTTP-Method : GET \n msg : ", res1.data)
    res2 = flask_app.post(SIM_CHG_API)
    assert res2.status_code == 405
    print("HTTP-Method : POST \n msg : ", res2.data)
    res3 = flask_app.put(SIM_CHG_API)
    assert res3.status_code == 405
    print("HTTP-Method : PUT \n msg : ", res3.data)
    res4 = flask_app.patch(SIM_CHG_API)
    assert res4.status_code == 405
    print("HTTP-Method : PATCH \n msg : ", res4.data)


# noinspection PyUnusedLocal,PyShadowingNames,SqlDialectInspection
def test_sim_change_happy_case(flask_app, db, session):
    """ Verify that sim-chg api responds correctly when all parameters are valid """
    complete_db_insertion(session, db, 411, '923036830442', 411, 'Find-X', 'OPPO', '5RT1qazbh', '3G,4G',
                          'EiYjagYD', 411, '889270911982467')
    first_pair_db_insertion(session, db, 412, '923460192939', 'telenor', 411)
    session.execute(text("""UPDATE public.pairing SET imsi = '410057689234091' WHERE msisdn = '923460192939';"""))
    payload = {"msisdn": "923460192939", "operator": "jazz"}
    result = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.status_code == 200


# noinspection PyUnusedLocal,PyShadowingNames,SqlDialectInspection,PyPep8Naming
def test_sim_change_functionality_before_export_to_PairList(flask_app, db, session):
    """ Verify the behaviour of sim-chg api when pair is not exported to Pair-List at the time of deletion """

    complete_db_insertion(session, db, 412, '923047930553', 412, 'F-9', 'OPPO', 'Fd9kLqwV', '3G,4G',
                          'gDd7XsL4', 412, '910223945867106')
    first_pair_db_insertion(session, db, 413, '923155406922', 'zong', 412)
    imsi = '410042233445566'

    session.execute(text("""UPDATE public.pairing SET imsi = '{}' WHERE msisdn = '923155406922';""".format(imsi)))
    payload = {"msisdn": "923155406922", "operator": "warid"}
    result = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)

    qry = session.execute(text("""SELECT * FROM pairing WHERE msisdn = '923155406922'; """)).fetchone()
    print("\n-----Pair Status-----\nOld IMSI = {}\nNew IMSI = {}\nchange_type = {}\nexport_status = {}".
          format(qry.old_imsi, qry.imsi, qry.change_type, qry.export_status))

    assert qry.old_imsi is None
    assert qry.imsi is None
    assert qry.change_type is None


# noinspection PyUnusedLocal,PyShadowingNames,PyPep8Naming,SqlDialectInspection
def test_sim_change_functionality_after_export_to_PairList(flask_app, db, session):
    """ Verify the behaviour of sim-chg api when pair is already exported to Pair-List at the time of deletion """

    complete_db_insertion(session, db, 416, '923047930887', 416, 'F4', 'OPPO', 'Fd9k567wV', '3G,4G',
                          'Df5tNkL0', 416, '910296775432106')
    first_pair_db_insertion(session, db, 420, '923128845768', 'zong', 416)
    imsi = '410049007345128'

    session.execute(text("""UPDATE public.pairing SET imsi = '{}', export_status = true 
                            WHERE msisdn = '923128845768';""".format(imsi)))
    payload = {"msisdn": "923128845768", "operator": "warid"}
    result = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    # assert result.data == b"SIM Change request has been registered. The Pair will be active in 24 to 48 hours"

    qry = session.execute(text("""SELECT * FROM pairing WHERE msisdn = '923128845768'; """)).fetchone()
    print("\n-----Pair Status-----\nOld IMSI = {}\nNew IMSI = {}\nchange_type = {}\nexport_status = {}".
          format(qry.old_imsi, qry.imsi, qry.change_type, qry.export_status))

    assert qry.old_imsi == '410049007345128'
    assert qry.imsi is None
    assert qry.change_type is None
    assert qry.export_status is None


# noinspection PyUnusedLocal,PyShadowingNames
def test_sim_change_functionality_wrong_sender_no(flask_app, db, session):
    """ Verify that sim-chg api detects wrong Sender MSISDN """
    complete_db_insertion(session, db, 413, '923057930229', 413, 'MI MIX 2S ', 'XIAOMI', 'SN1i9KpW', '3G,4G',
                          '892jeM42', 413, '910223947111222')
    first_pair_db_insertion(session, db, 414, '923138191645', 'zong', 413)
    payload = {"msisdn": "923113306922", "operator": "ufone"}
    result = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
    data = json.loads(result.data.decode('utf-8'))
    print(result.data)
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "MSISDN 923113306922 is not existed in any pair or SIM-Change request is already in process"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "MSISDN 923113306922 no existe en ningún par o la solicitud de cambio de SIM ya está en proceso"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "MSISDN 923113306922 tidak ada dalam pasangan apa pun atau permintaan SIM-Change sedang dalam proses"


# noinspection PyUnusedLocal,PyShadowingNames
def test_sim_change_functionality_request_from_unconfirmed_sec_pair(flask_app, db, session):
    """ Verify that sim-chg api can cater request from confirmed secondary pair as well """
    complete_db_insertion(session, db, 414, '923057930229', 414, 'PocoPhone ', 'XIAOMI', 'Sb9i9]]KpW', '3G,4G',
                          'QFIceP39', 414, '910223947111444')
    first_pair_db_insertion(session, db, 415, '923338791465', 'ufone', 414)
    add_pair_db_insertion(session, db, 417, 416, '923125840917', 414)
    payload = {"msisdn": "923125840917", "operator": "zong"}
    result = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
    data = json.loads(result.data.decode('utf-8'))
    print(result.data)
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "MSISDN 923125840917 is not existed in any pair or SIM-Change request is already in process"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "MSISDN 923125840917 no existe en ningún par o la solicitud de cambio de SIM ya está en proceso"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "MSISDN 923125840917 tidak ada dalam pasangan apa pun atau permintaan SIM-Change sedang " \
                       "dalam proses"


# noinspection PyUnusedLocal,PyShadowingNames,SqlDialectInspection
def test_sim_change_functionality_request_from_confirmed_sec_pair(flask_app, db, session):
    """ Verify that sim-chg api can cater request from confirmed secondary pair as well """
    complete_db_insertion(session, db, 415, '923089923776', 415, 'Nokia-4', 'NOKIA', 'Sbqa7KpW', '2G,3G,4G',
                          'Ox4sTcst', 415, '910223947333344')
    first_pair_db_insertion(session, db, 418, '923216754889', 'warid', 415)
    add_pair_db_insertion(session, db, 419, 418, '923125840917', 415)
    add_pair_confrm_db_insertion(session, db, '923125840917', 418, 'zong')

    imsi = '410065544332211'
    session.execute(text("""UPDATE public.pairing SET imsi = '{}' WHERE msisdn = '923125840917';""".format(imsi)))
    payload = {"msisdn": "923125840917", "operator": "zong"}
    result = flask_app.delete(SIM_CHG_API, headers=HEADERS, data=json.dumps(payload))
    data = json.loads(result.data.decode('utf-8'))
    print(result.data)
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "SIM Change request has been registered. The Pair will be active in 24 to 48 hours"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "La solicitud de cambio de SIM ha sido registrada. El par estará activo en 24 a 48 horas."
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "Permintaan Perubahan SIM telah terdaftar. Pasangan ini akan aktif dalam 24 hingga 48 jam"
