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
import json
from app import conf
# noinspection PyUnresolvedReferences,PyProtectedMember
from tests._fixtures import *
# noinspection PyProtectedMember
from tests._helpers import *
from sqlalchemy import text


REL_SINGLE_API = 'api/v1/rel-single-pair'
HEADERS = {'Content-Type': "application/json"}


# noinspection PyUnusedLocal,PyShadowingNamesl,PyShadowingNames
def test_rel_single_pair_validations_wrong_primary_msisdn(flask_app, db):
    """ Verify that rel-single api doesn't accept invalid primary Mobile numbers """

    sender_no = ['9230028460937724', '92321417g9C21', '92345@769#564&8', '923004', '']
    for val in sender_no:
        payload_1 = {"primary_msisdn": val, "secondary_msisdn": "923003294857"}
        rslt = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload_1))
        data = json.loads(rslt.data.decode('utf-8'))
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['primary_msisdn'][0] == "MSISDN format is not correct"
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['primary_msisdn'][0] == "El formato MSISDN no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['primary_msisdn'][0] == "Format MSISDN tidak benar"

        print("primary_msisdn :", val, "\n msg : ", data['message']['primary_msisdn'][0])


# noinspection PyUnusedLocal,PyShadowingNamesl,PyShadowingNames
def test_rel_single_pair_validations_wrong_secondary_msisdn(flask_app, db):
    """ Verify that rel-single api doesn't accept invalid Secondary Mobile numbers """

    sender_no = ['9230028460937724', '92321417g9C21', '92345@769#564&8', '923004', '']
    for val in sender_no:
        payload_2 = {"primary_msisdn": "923003294857", "secondary_msisdn": val}
        rslt = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload_2))
        data = json.loads(rslt.data.decode('utf-8'))
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['secondary_msisdn'][0] == "MSISDN format is not correct"
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['secondary_msisdn'][0] == "El formato MSISDN no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['secondary_msisdn'][0] == "Format MSISDN tidak benar"

        print("secondary_msisdn :", val, "\n msg : ", data['message']['secondary_msisdn'][0])


# noinspection PyUnusedLocal,PyShadowingNames
def test_rel_single_pair_validations_valid_sender_no(flask_app, db):
    """ Verify that rel-single api only accepts valid primary & secondary numbers """
    sender_no = '923458179437'
    payload = {"primary_msisdn": sender_no, "secondary_msisdn": sender_no}
    rslt = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    print(rslt.data)
    data = json.loads(rslt.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert not rslt.data == b"Sender MSISDN format is not correct"
        assert not rslt.data == b"Secondary MSISDN format is not correct"
    elif conf['supported_languages']['default_language'] == 'es':
        assert not rslt.data == "El formato MSISDN no es correcto"
        assert not rslt.data == "Format MSISDN tidak benar"


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_missing_parameters(flask_app, db):
    """ Verify that rel-single api prompts when any parameter is missing """
    payload = [
        {"secondary_msisdn": "923458179437"},
        {"primary_msisdn": "923225782404"}
    ]
    for val in range(0, 2):
        result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload[val]))
        print(result.data)
        data = json.loads(result.data.decode('utf-8'))
        if val == 0:
            assert data['message']['primary_msisdn'][0] == "Missing data for required field."
        elif val == 1:
            assert data['message']['secondary_msisdn'][0] == "Missing data for required field."


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_error_404_wrong_api(flask_app, db):
    """ Verify that rel-single api prompts when Error-400 is occurred """
    tmp_api = 'api/v1/rellll-singleeeee'
    payload = {"primary_msisdn": "923225782404", "secondary_msisdn": "923458179437"}
    result = flask_app.delete(tmp_api, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    assert result.status_code == 404


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_error_405_method_not_allowed(flask_app, db):
    """ Verify that add-confirm api prompts when Error-405 occurs """
    res1 = flask_app.get(REL_SINGLE_API)
    assert res1.status_code == 405
    print("\nHTTP-Method : GET \n msg : ", res1.data)
    res2 = flask_app.post(REL_SINGLE_API)
    assert res2.status_code == 405
    print("HTTP-Method : POST \n msg : ", res2.data)
    res3 = flask_app.put(REL_SINGLE_API)
    assert res3.status_code == 405
    print("HTTP-Method : PUT \n msg : ", res3.data)
    res4 = flask_app.patch(REL_SINGLE_API)
    assert res4.status_code == 405
    print("HTTP-Method : PATCH \n msg : ", res4.data)


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_happy_case_unconfirmed_pair(flask_app, db, session):
    """ Verify that rel-single api successfully deletes unconfirmed secondary pair """

    complete_db_insertion(session, db, 211, '923036830442', 211, 'Find-X', 'OPPO', '5RT1qazbh', '3G,4G',
                          'EirnagYD', 211, '889270911982467')
    first_pair_db_insertion(session, db, 212, '923460192939', 'telenor', 211)
    add_pair_db_insertion(session, db, 213, 212, '923115840917', 211)

    payload = {"primary_msisdn": "923460192939", "secondary_msisdn": "923115840917"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    data = json.loads(result.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "Deletion request is successful. Pair will be removed in next 24 to 48 hours"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "La solicitud de eliminación se realizó correctamente. El par se eliminará en las próximas 24 " \
                       "a 48 horas."
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "Permintaan penghapusan berhasil. Pasangan akan dihapus dalam 24 hingga 48 jam ke depan"


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_happy_case_confirmed_pair(flask_app, db, session):
    """ Verify that rel-single api successfully deletes unconfirmed secondary pair """
    complete_db_insertion(session, db, 212, '923047930553', 212, 'F-9', 'OPPO', 'Fd9kLqwV', '3G,4G',
                          'gB8DXsL4', 212, '910223945867106')
    first_pair_db_insertion(session, db, 214, '923145406911', 'zong', 212)
    add_pair_db_insertion(session, db, 215, 214, '923125840917', 212)
    add_pair_confrm_db_insertion(session, db, '923125840917', 214, 'zong')

    payload = {"primary_msisdn": "923145406911", "secondary_msisdn": "923125840917"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    data = json.loads(result.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "Deletion request is successful. Pair will be removed in next 24 to 48 hours"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "La solicitud de eliminación se realizó correctamente. El par se eliminará en las próximas 24 " \
                       "a 48 horas."
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "Permintaan penghapusan berhasil. Pasangan akan dihapus dalam 24 hingga 48 jam ke depan"


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_functionality_wrong_primary_msisdn(flask_app, db, session):
    """ Verify that rel-single api detects wrong primary MSISDN in parameters """
    complete_db_insertion(session, db, 213, '923057930229', 213, 'MI MIX 2S ', 'XIAOMI', 'SN1i9KpW', '3G,4G',
                          '892jXN42', 213, '910223947111222')
    first_pair_db_insertion(session, db, 216, '923158191645', 'zong', 213)
    add_pair_db_insertion(session, db, 217, 216, '923125840917', 213)

    payload = {"primary_msisdn": "923156667777", "secondary_msisdn": "923125840917"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    data = json.loads(result.data.decode('utf-8'))
    print(result.data)
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "Request is not made by Primary-MSISDN or number-to-be-deleted belongs to primary pair"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "El MSISDN primario no realiza la solicitud o el número que se va a eliminar pertenece al " \
                       "par primario"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "Permintaan tidak dibuat oleh Primary-MSISDN atau nomor yang akan dihapus milik pasangan primer"


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_functionality_wrong_secondary_msisdn(flask_app, db, session):
    """ Verify that rel-single api detects wrong secondary MSISDN in parameters """
    complete_db_insertion(session, db, 214, '923057930229', 214, 'PocoPhone ', 'XIAOMI', 'Sb9i9]]KpW', '3G,4G',
                          'QJIceP39', 214, '910223947111444')
    first_pair_db_insertion(session, db, 218, '923338791465', 'ufone', 214)
    add_pair_db_insertion(session, db, 219, 218, '923125840917', 214)

    payload = {"primary_msisdn": "923338791465", "secondary_msisdn": "923137848888"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    data = json.loads(result.data.decode('utf-8'))
    print(result.data)
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "MSISDN 923137848888 is not Paired with the device"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "MSISDN 923137848888 no está emparejado con el dispositivo"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "MSISDN 923137848888 tidak dipasangkan dengan perangkat"


# noinspection PyShadowingNames,PyUnusedLocal
def test_rel_single_pair_functionality_delete_primary_msisdn(flask_app, db, session):
    """ Verify that rel-single api doesn't allow deletion of primary pair """

    complete_db_insertion(session, db, 215, '923089923776', 215, 'Nokia-4 ', 'NOKIA', 'Sbqa7KpW', '2G,3G,4G',
                          'Ox4JTcst', 215, '910223947333344')
    first_pair_db_insertion(session, db, 220, '923216754889', 'warid', 215)
    add_pair_db_insertion(session, db, 221, 220, '923125840917', 215)

    payload = {"primary_msisdn": "923216754889", "secondary_msisdn": "923216754889"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    data = json.loads(result.data.decode('utf-8'))
    print(result.data)
    if conf['supported_languages']['default_language'] == 'en':
        assert data == "Request is not made by Primary-MSISDN or number-to-be-deleted belongs to primary pair"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data == "El MSISDN primario no realiza la solicitud o el número que se va a eliminar pertenece al " \
                       "par primario"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data == "Permintaan tidak dibuat oleh Primary-MSISDN atau nomor yang akan dihapus milik pasangan primer"


# noinspection PyShadowingNames,PyUnusedLocal,PyPep8Naming,SqlDialectInspection
def test_rel_single_pair_deletion_before_export_to_PairList(flask_app, db, session):
    """ Verify the behaviour of rel-single api when secondary pair is not exported to
        Pair-List at the time of deletion """

    complete_db_insertion(session, db, 216, '923098924476', 216, 'LUMIA ', 'NOKIA', 'S2w434a7hW', '2G,3G',
                          '4eUe5NaB', 216, '871022394555554')
    first_pair_db_insertion(session, db, 222, '923145892117', 'zong', 216)
    add_pair_db_insertion(session, db, 223, 222, '923018144773', 216)

    session.execute(text("""UPDATE public.pairing SET imsi = '410015678987223', change_type = 'add', 
                            export_status = false, add_pair_status = true WHERE msisdn = '923018144773';"""))

    payload = {"primary_msisdn": "923145892117", "secondary_msisdn": "923018144773"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)
    q1 = session.execute(text("""SELECT * FROM public.pairing WHERE msisdn = '923018144773'; """)).fetchone()
    print("\n-----Deleted Secondary-Pair-----\nmsisdn = {}\nend_date = {}\nchange_type = {}\nexport_status = {}".
          format(q1.msisdn, q1.end_date, q1.change_type, q1.export_status))
    assert q1.change_type is None
    assert q1.export_status is None
    assert q1.old_imsi is None


# noinspection PyShadowingNames,PyUnusedLocal,PyPep8Naming,SqlDialectInspection
def test_rel_single_pair_deletion_after_export_to_PairList(flask_app, db, session):
    """ Verify the behaviour of rel-single api when secondary pair is already exported to
        Pair-List at the time of deletion """

    complete_db_insertion(session, db, 217, '923098922234', 217, 'Nokia-4', 'NOKIA', 'Aq23rDTn8', '3G,4G',
                          'S4vXXoMp', 217, '361022321334964')
    first_pair_db_insertion(session, db, 224, '923138834564', 'zong', 217)
    add_pair_db_insertion(session, db, 225, 224, '923479091924', 217)

    session.execute(text("""UPDATE public.pairing SET imsi = '410029803775223', change_type = 'add', 
                            export_status = true, add_pair_status = true WHERE msisdn = '923479091924';"""))

    payload = {"primary_msisdn": "923138834564", "secondary_msisdn": "923479091924"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)

    q1 = session.execute(text("""SELECT * FROM public.pairing WHERE msisdn = '923479091924'; """)).fetchone()
    print("\n-----Deleted Secondary-Pair-----\nmsisdn = {}\nend_date = {}\nchange_type = {}\nexport_status = {}".
          format(q1.msisdn, q1.end_date, q1.change_type, q1.export_status))

    assert q1.change_type == 'remove'
    assert not q1.export_status


# noinspection PyUnusedLocal,PyShadowingNames,SqlDialectInspection
def test_rel_single_pair_exported_sim_changed_deleted_before_new_imsi(flask_app, db, session):
    """ Verify the behaviour of rel-single api for special case where secondary pair is exported once and after
        that SIM-Change is requested but before MNO provides new IMSI, Pair is deleted"""

    complete_db_insertion(session, db, 218, '923098922556', 218, 'Nokia-6', 'NOKIA', 'Lk9Y6VVf', '3G,4G',
                          'AxY7PiG8', 218, '451087529940964')
    first_pair_db_insertion(session, db, 226, '923339125125', 'ufone', 218)
    add_pair_db_insertion(session, db, 227, 226, '923337457869', 218)

    session.execute(text("""UPDATE public.pairing SET old_imsi = '410079703451431', change_type = null,
                                    export_status = null, add_pair_status = true WHERE msisdn = '923337457869';"""))

    payload = {"primary_msisdn": "923339125125", "secondary_msisdn": "923337457869"}
    result = flask_app.delete(REL_SINGLE_API, headers=HEADERS, data=json.dumps(payload))
    print(result.data)

    q1 = session.execute(text("""SELECT * FROM public.pairing WHERE msisdn = '923337457869'; """)).fetchone()
    print("\n-----Deleted Secondary-Pair-----\nmsisdn = {}\nend_date = {}\nchange_type = {}\nexport_status = {}".
          format(q1.msisdn, q1.end_date, q1.change_type, q1.export_status))

    assert q1.change_type == 'remove'
    assert not q1.export_status
    assert q1.imsi == '410079703451431'
    assert not q1.old_imsi
