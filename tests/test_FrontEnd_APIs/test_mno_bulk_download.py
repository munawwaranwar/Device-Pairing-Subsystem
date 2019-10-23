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
# noinspection PyUnresolvedReferences
from sqlalchemy import text
from app import conf


MNO_BULK_DOWNLOAD = 'api/v1/mno-bulk-download'
HEADERS = {'Content-Type': "application/json"}


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_download_functionality_no_records(flask_app, db):
    """ to check the response of bulk-download api when there is no record """
    mno = ['jazz', 'telenor', 'zong', 'ufone', 'warid']
    for val in mno:
        url = "{api}?mno={opr}".format(api=MNO_BULK_DOWNLOAD, opr=val)
        rs = flask_app.get(url)
        assert rs.status_code == 422
        d1 = json.loads(rs.data.decode('utf-8'))
        print(d1, val)
        if conf['supported_languages']['default_language'] == 'en':
            assert d1.get('Error') == "No File found"
        elif conf['supported_languages']['default_language'] == 'es':
            assert d1.get('Error') == "Archivo no encontrado"
        elif conf['supported_languages']['default_language'] == 'id':
            assert d1.get('Error') == "Tidak ada File yang ditemukan"


    # noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_download_happy_case_primary_pairs_only(flask_app, db, session):
    """ Verify that bulk-download api downloads the file successfully having only primary pairs"""
    complete_db_insertion(session, db, 251, '923357891879', 251, 'G4', 'LG', 'shfy8JhZx', '2G,3G',
                          'Z45aWf6l', 251, '112233445566778')
    complete_db_insertion(session, db, 252, '923357891880', 252, 'G5', 'LG', 'JhOp8JhZx', '2G,3G',
                          'S5fRtf6l', 252, '998877665544332')
    first_pair_db_insertion(session, db, 251, '923007112390', 'jazz', 251)
    first_pair_db_insertion(session, db, 252, '923007112391', 'jazz', 252)
    url = "{api}?mno=jazz".format(api=MNO_BULK_DOWNLOAD)
    rs = flask_app.get(url)
    print(rs.data)
    assert rs.status_code == 200


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_download_happy_case_all_pairs(flask_app, db, session):
    """ Verify that bulk-download api downloads the file successfully having primary & secondary pairs both"""
    complete_db_insertion(session, db, 253, '923354441879', 253, 'G6', 'LG', 'shfHHJhZx', '2G,3G',
                          '9i8Pbr5T', 253, '112233445566778')
    complete_db_insertion(session, db, 254, '923358881880', 254, 'G7', 'LG', 'JhOUUJhZx', '2G,3G',
                          'G3eeR7vQ', 254, '998877665544332')
    first_pair_db_insertion(session, db, 253, '923006565747', 'warid', 253)
    add_pair_db_insertion(session, db, 254, 253, '923018112222', 253)
    add_pair_confrm_db_insertion(session, db, '923018112222', 253, 'warid')

    first_pair_db_insertion(session, db, 255, '923007575848', 'warid', 254)
    add_pair_db_insertion(session, db, 256, 255, '923018113333', 254)
    add_pair_confrm_db_insertion(session, db, '923018113333', 255, 'warid')

    url = "{api}?mno=warid".format(api=MNO_BULK_DOWNLOAD)
    rs = flask_app.get(url)
    print(rs.data)
    assert rs.status_code == 200


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_download_validations_operator_names(flask_app, db):
    """Verify that bulk-download api doesn't allow mno names other than mentioned in configuration file"""
    mno = ['jazz', 'telenor', 'zong', 'ufone', 'warid']
    f_mno = ['j@zz', 'Vodafone', 'T-Mobile', 'Orange', 'wariid']
    for val in mno:
        url = "{api}?mno={opr}".format(api=MNO_BULK_DOWNLOAD, opr=val)
        flask_app.get(url)
        print('correct operator name: ', val)
    for v in f_mno:
        url = "{api}?mno={opr}".format(api=MNO_BULK_DOWNLOAD, opr=v)
        rs_1 = flask_app.get(url)
        f_d1 = json.loads(rs_1.data.decode('utf-8'))
        print(f_d1, v)
        if conf['supported_languages']['default_language'] == 'en':
            assert f_d1.get('Error') == "Improper Operator-Name provided"
        elif conf['supported_languages']['default_language'] == 'es':
            assert f_d1.get('Error') == "Nombre de operador incorrecto proporcionado"
        elif conf['supported_languages']['default_language'] == 'id':
            assert f_d1.get('Error') == "Nama Operator yang Tidak Benar disediakan"


    # noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_download_error_404_wrong_api(flask_app, db):
    """ Verify that bulk-download api prompts when Error-404 is occurred """
    tmp_api = 'api/v1/mnooo-bulkkk-downloaddd'
    url = "{api}?mno=telenor".format(api=tmp_api)
    rs = flask_app.get(url)
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert rs.status_code == 404


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_download_error_405_method_not_allowed(flask_app, db):
    """ Verify that bulk-download api prompts when Error-405 is occurred """
    res1 = flask_app.put(MNO_BULK_DOWNLOAD)
    assert res1.status_code == 405
    res2 = flask_app.post(MNO_BULK_DOWNLOAD)
    assert res2.status_code == 405
    res3 = flask_app.delete(MNO_BULK_DOWNLOAD)
    assert res3.status_code == 405
    res4 = flask_app.patch(MNO_BULK_DOWNLOAD)
    assert res4.status_code == 405
