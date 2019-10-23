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


# noinspection PyUnresolvedReferences,PyProtectedMember
from tests._fixtures import *
# noinspection PyProtectedMember
from tests._helpers import *
import json
from app import conf
from sqlalchemy import text

MNO_IMSI_UPLOAD = 'api/v1/mno-single-upload'
HEADERS = {'Content-Type': "application/json"}


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_single_imsi_happy_case_primary_pair(flask_app, db, session):
    """ Verify that mno-single-imsi api provides IMSI addition for primary pair """

    complete_db_insertion(session, db, 150, '923216778901', 150, 'G3', 'LG', 's5T98JhZx', '2G,3G',
                          'Z4Cghf6l', 150, '112233445566778')
    first_pair_db_insertion(session, db, 150, '923214567456', 'warid', 150)
    payload = mno_imsi_upload('92', '3214567456', 'warid', '410049988776655')
    rs = flask_app.put(MNO_IMSI_UPLOAD, headers=HEADERS, data=json.dumps(payload))
    d1 = json.loads(rs.data.decode('utf-8'))
    assert rs.status_code == 200
    print(d1)
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('msg') == 'IMSI added successfully'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('msg') == "IMSI agregado exitosamente"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('msg') == "IMSI berhasil ditambahkan"


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_single_imsi_happy_case_secondary_pair(flask_app, db, session):
    """ Verify that mno-single-imsi api provides IMSI addition for secondary pair as well"""

    complete_db_insertion(session, db, 151, '923047934553', 151, 'F-9', 'OPPO', 'Fd9kLqwV', '3G,4G',
                          'gB8dXsL4', 151, '910223945867106')
    first_pair_db_insertion(session, db, 152, '923145406911', 'zong', 151)
    add_pair_db_insertion(session, db, 153, 152, '923125840917', 151)
    add_pair_confrm_db_insertion(session, db, '923125840917', 152, 'zong')
    payload = mno_imsi_upload('92', '3125840917', 'zong', '410071122334455')
    rs = flask_app.put(MNO_IMSI_UPLOAD, headers=HEADERS, data=json.dumps(payload))
    d1 = json.loads(rs.data.decode('utf-8'))
    assert rs.status_code == 200
    print(d1)
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('msg') == 'IMSI added successfully'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('msg') == "IMSI agregado exitosamente"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('msg') == "IMSI berhasil ditambahkan"


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_single_imsi_functionality_imsi_duplication(flask_app, db, session):
    """ Verify that mno-single-imsi api doesn't allow IMSI duplication"""

    complete_db_insertion(session, db, 153, '923051930442', 153, 'F2', 'OPPO', 'Gfs6e3K', '3G,4G',
                          'Jh2d54mx', 153, '819283744569024')
    complete_db_insertion(session, db, 154, '923339676123', 154, 'iphone-7', 'Apple', 'Kj8at35F', '2G,3G,4G',
                          'H9solPt5', 154, '723092217845603')
    first_pair_db_insertion(session, db, 154, '923462197056', 'telenor', 153)
    first_pair_db_insertion(session, db, 155, '923003819457', 'jazz', 154)
    pl_1 = mno_imsi_upload('92', '3462197056', 'telenor', '410036667778889')
    pl_2 = mno_imsi_upload('92', '3003819457', 'jazz', '410036667778889')
    rs_1 = flask_app.put(MNO_IMSI_UPLOAD, headers=HEADERS, data=json.dumps(pl_1))
    assert rs_1.status_code == 200
    rs_2 = flask_app.put(MNO_IMSI_UPLOAD, headers=HEADERS, data=json.dumps(pl_2))
    assert rs_2.status_code == 422
    d1 = json.loads(rs_2.data.decode('utf-8'))
    print(d1)
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('Error') == 'IMSI already exists'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('Error') == "IMSI ya existe"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('Error') == "IMSI sudah ada"


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_single_imsi_validations_wrong_mno_and_msisdn(flask_app, db, session):
    """ Verify that mno-single-imsi api doesn't allow IMSI updation for wrong operator name and MSISDN"""

    complete_db_insertion(session, db, 155, '923335888777', 155, 'iphone-8', 'Apple', 'GfT6YhD3', '2G,3G,4G',
                          'Sq3rU2tC', 155, '891264786729436')
    first_pair_db_insertion(session, db, 156, '923348960442', 'ufone', 155)
    pl_1 = mno_imsi_upload('92', '3348960442', 'telenor', '410031111444466')
    rs_1 = flask_app.put(MNO_IMSI_UPLOAD, headers=HEADERS, data=json.dumps(pl_1))
    assert rs_1.status_code == 422
    d1 = json.loads(rs_1.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('msg') == 'IMSI addition Failed'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('msg') == "Falló la adición de IMSI"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('msg') == "Penambahan IMSI Gagal"
    print(d1)

    pl_2 = mno_imsi_upload('92', '3341111111', 'ufone', '410031111444466')  # wrong
    rs_2 = flask_app.put(MNO_IMSI_UPLOAD, headers=HEADERS, data=json.dumps(pl_2))
    assert rs_2.status_code == 422
    d2 = json.loads(rs_2.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert d2.get('msg') == 'IMSI addition Failed'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d2.get('msg') == "Falló la adición de IMSI"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d2.get('msg') == "Penambahan IMSI Gagal"
    print(d2)


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_single_imsi_functionality_unconfirmed_pair(flask_app, db, session):
    """ Verify that mno-single-imsi api doesn't allow IMSI updation for unconfirmed pairs"""

    complete_db_insertion(session, db, 156, '923336646555', 156, 'iphone-8', 'Apple', 'GfT6YhD3', '2G,3G,4G',
                          'g8Cad3kL', 156, '891264786729436')
    first_pair_db_insertion(session, db, 157, '923357788994', 'ufone', 156)
    add_pair_db_insertion(session, db, 158, 157, '923136783456', 156)
    pl = mno_imsi_upload('92', '3136783456', 'zong', '410072334455667')
    rs = flask_app.put(MNO_IMSI_UPLOAD, headers=HEADERS, data=json.dumps(pl))
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('msg') == 'IMSI addition Failed'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('msg') == "Falló la adición de IMSI"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('msg') == "Penambahan IMSI Gagal"


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_single_imsi_functionality_deleted_pair(flask_app, db, session):
    """ Verify that mno-single-imsi api doesn't allow IMSI updation for deleted-pairs"""

    complete_db_insertion(session, db, 157, '923336663444', 157, 'iphone-8', 'Apple', 'GfT6YhD3', '4G',
                          'Gh6Ei9oS', 157, '891264786729436')
    first_pair_db_insertion(session, db, 159, '923226510989', 'warid', 157)
    session.execute(text("""UPDATE public.pairing SET end_date = '2018-11-18' WHERE msisdn = '923226510989';"""))
    pl = mno_imsi_upload('92', '3226510989', 'warid', '410054443332221')
    rs = flask_app.put(MNO_IMSI_UPLOAD, headers=HEADERS, data=json.dumps(pl))
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('msg') == 'IMSI addition Failed'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('msg') == "Falló la adición de IMSI"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('msg') == "Penambahan IMSI Gagal"


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_single_imsi_error_404_wrong_api(flask_app, db):
    """ Verify that mno-single-imsi api prompts when Error-404 is occurred """

    tmp_api = 'api/v1/mnoooo-singleeee-uploadddd'
    pl = mno_imsi_upload('92', '3226510989', 'warid', '410054443332221')
    rs = flask_app.put(tmp_api, headers=HEADERS, data=json.dumps(pl))
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert rs.status_code == 404


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_single_imsi_error_405_method_not_allowed(flask_app, db):
    """ Verify that mno-single-imsi api prompts when Error-405 is occurred """

    res1 = flask_app.get(MNO_IMSI_UPLOAD)
    assert res1.status_code == 405
    res2 = flask_app.post(MNO_IMSI_UPLOAD)
    assert res2.status_code == 405
    res3 = flask_app.delete(MNO_IMSI_UPLOAD)
    assert res3.status_code == 405
    res4 = flask_app.patch(MNO_IMSI_UPLOAD)
    assert res4.status_code == 405


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_single_validations_invalid_counrty_code(flask_app, db):
    """Verify that mno-single-imsi api doesn't allow invalid country-code"""
    country_code = '0971'
    pl = mno_imsi_upload(country_code, '3226510989', 'warid', '410054443332221')
    rs = flask_app.put(MNO_IMSI_UPLOAD, headers=HEADERS, data=json.dumps(pl))
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('Error') == 'MSISDN format is not correct'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('Error') == "El formato MSISDN no es correcto"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('Error') == "Format MSISDN tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_single_validations_invalid_subscriber_no(flask_app, db):
    """Verify that mno-single-imsi api doesn't allow invalid subscriber-number """

    sn = ['30021619047892364', '30a21D19x4', '30@216!904$']
    for val in sn:
        pl = mno_imsi_upload('92', val, 'warid', '410054443332221')
        rs = flask_app.put(MNO_IMSI_UPLOAD, headers=HEADERS, data=json.dumps(pl))
        assert rs.status_code == 422
        d1 = json.loads(rs.data.decode('utf-8'))
        print(d1, val)
        if conf['supported_languages']['default_language'] == 'en':
            assert d1.get('Error') == 'MSISDN format is not correct'
        elif conf['supported_languages']['default_language'] == 'es':
            assert d1.get('Error') == "El formato MSISDN no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert d1.get('Error') == "Format MSISDN tidak benar"


        # noinspection PyUnusedLocal,PyShadowingNames
def test_mno_single_validations_invalid_imsi(flask_app, db):
    """Verify that mno-single-imsi api doesn't allow invalid IMSI """

    imsi = ['4100181', '410048956738902536', '41OO12l6o4z6a9N', '4!00|2l6@4^6#9&']
    for val in imsi:
        pl = mno_imsi_upload('92', '3226510989', 'warid', val)
        rs = flask_app.put(MNO_IMSI_UPLOAD, headers=HEADERS, data=json.dumps(pl))
        assert rs.status_code == 422
        d1 = json.loads(rs.data.decode('utf-8'))
        print(d1, val)
        if conf['supported_languages']['default_language'] == 'en':
            assert d1.get('Error') == 'IMSI format is not correct'
        elif conf['supported_languages']['default_language'] == 'es':
            assert d1.get('Error') == "El formato IMSI no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert d1.get('Error') == "Format IMSI tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_single_validations_operator_names(flask_app, db):
    """Verify that mno-single-imsi api doesn't allow mno names other than mentioned in configuration file"""

    mno = ['jazz', 'telenor', 'zong', 'ufone', 'warid']
    f_mno = ['j@zz', 'Vodafone', 'T-Mobile', 'Orange', 'wariid']

    for val in mno:
        pl = mno_imsi_upload('92', '3226510989', val, '410054443332221')
        rs = flask_app.put(MNO_IMSI_UPLOAD, headers=HEADERS, data=json.dumps(pl))
        d1 = json.loads(rs.data.decode('utf-8'))
        print('correct operator name: ', val)
        if conf['supported_languages']['default_language'] == 'en':
            assert not d1.get('Error') == "Improper Operator-Name provided"
        elif conf['supported_languages']['default_language'] == 'es':
            assert not d1.get('Error') == "Nombre de operador incorrecto proporcionado"
        elif conf['supported_languages']['default_language'] == 'id':
            assert not d1.get('Error') == "Nama Operator yang Tidak Benar disediakan"

    for v in f_mno:
        pl = mno_imsi_upload('92', '3226510989', v, '410054443332221')
        rs_1 = flask_app.put(MNO_IMSI_UPLOAD, headers=HEADERS, data=json.dumps(pl))
        f_d1 = json.loads(rs_1.data.decode('utf-8'))
        print(f_d1, v)
        if conf['supported_languages']['default_language'] == 'en':
            assert f_d1.get('Error') == "Improper Operator-Name provided"
        elif conf['supported_languages']['default_language'] == 'es':
            assert f_d1.get('Error') == "Nombre de operador incorrecto proporcionado"
        elif conf['supported_languages']['default_language'] == 'id':
            assert f_d1.get('Error') == "Nama Operator yang Tidak Benar disediakan"


# noinspection PyUnusedLocal,PyShadowingNames
def test_mno_single_missing_parameters(flask_app, db):
    """ Verify that mno-single-imsi api prompts when any parameter is missing """
    for cond in range(1, 6):
        pl_1 = mno_imsi_upload('92', '3226510989', 'telenor', '410054443332221', cond)
        rs_1 = flask_app.put(MNO_IMSI_UPLOAD, headers=HEADERS, data=json.dumps(pl_1))
        assert rs_1.status_code == 422
        d1 = json.loads(rs_1.data.decode('utf-8'))
        print(d1)
        if conf['supported_languages']['default_language'] == 'en':
            if cond == 1:
                assert d1.get('Error') == 'Country-Code is missing'
            elif cond == 2:
                assert d1.get('Error') == 'Subscriber-Number is missing'
            elif cond == 3:
                assert d1.get('Error') == "operator's name is missing"
            elif cond == 4:
                assert d1.get('Error') == "IMSI is missing"
            elif cond == 5:
                assert d1.get('Error') == "MSISDN is missing"

        elif conf['supported_languages']['default_language'] == 'es':
            if cond == 1:
                assert d1.get('Error') == "Falta el código del país"
            elif cond == 2:
                assert d1.get('Error') == "Falta el número de abonado"
            elif cond == 3:
                assert d1.get('Error') == "Falta el nombre del operador"
            elif cond == 4:
                assert d1.get('Error') == "IMSI falta"
            elif cond == 5:
                assert d1.get('Error') == "Falta MSISDN"

        elif conf['supported_languages']['default_language'] == 'id':
            if cond == 1:
                assert d1.get('Error') == "Kode Negara tidak ada"
            elif cond == 2:
                assert d1.get('Error') == "Nomor Pelanggan tidak ada"
            elif cond == 3:
                assert d1.get('Error') == "nama operator tidak ada"
            elif cond == 4:
                assert d1.get('Error') == "IMSI tidak ada"
            elif cond == 5:
                assert d1.get('Error') == "MSISDN tidak ada"
