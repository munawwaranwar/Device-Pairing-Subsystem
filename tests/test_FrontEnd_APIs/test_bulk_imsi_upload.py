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

# noinspection PyUnresolvedReferences
import json
# noinspection PyUnresolvedReferences,PyProtectedMember
from tests._fixtures import *
from io import BytesIO
from app import conf


MNO_BULK_UPLOAD = 'api/v1/bulk-imsi-upload'
FILE_PATH = conf['test_doc_path']


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_upload_happy_case_proper_file(flask_app, session):
    """ Verify that bulk-upload api uploads the file successfully"""

    file_name = FILE_PATH + 'sample_proper_file.csv'
    with open(file_name, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'operator': 'warid',
        'file': (BytesIO(file_content), 'sample_proper_file.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 200
    d1 = json.loads(rs.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('message') == 'File uploaded successfully without errors'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('message') == "Archivo cargado exitosamente sin errores"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('message') == "File berhasil diunggah tanpa kesalahan"


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_upload_file_duplicated_imsis(flask_app, session):
    """ Verify that bulk-upload api detects duplicated IMSIs in the file"""

    file_name = FILE_PATH + 'sample_duplicate_imsi.csv'
    with open(file_name, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'operator': 'jazz',
        'file': (BytesIO(file_content), 'sample_duplicate_imsi.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 403
    d1 = json.loads(rs.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('message') == 'File contains duplicated IMSIs'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('message') == "El archivo contiene IMSI duplicados"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('message') == "File berisi duplikasi IMSI"


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_upload_file_incorrect_content(flask_app, session):
    """ Verify that bulk-upload api detects file with invalid/incorrect content"""

    file_name = FILE_PATH + 'sample_content_incorrect.csv'
    with open(file_name, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'operator': 'jazz',
        'file': (BytesIO(file_content), 'sample_content_incorrect.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 403
    d1 = json.loads(rs.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('message') == 'File content is not Correct'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('message') == "El contenido del archivo no es correcto"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('message') == "Konten file tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_upload_file_with_errors(flask_app, session):
    """ Verify that bulk-upload api uploads file but with errors"""

    file_name = FILE_PATH + 'sample_with_errors.csv'
    with open(file_name, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'operator': 'jazz',
        'file': (BytesIO(file_content), 'sample_with_errors.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 200
    d1 = json.loads(rs.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('msg') == 'File loaded successfully'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('msg') == "Archivo cargado correctamente"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('msg') == "File berhasil dimuat"
    assert not d1.get('link') == ''


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_upload_file_headers_incorrect(flask_app, session):
    """ Verify that bulk-upload api detects file with invalid/incorrect headers"""

    file_name = FILE_PATH + 'sample_without_headers.csv'
    with open(file_name, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'operator': 'telenor',
        'file': (BytesIO(file_content), 'sample_without_headers.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 403
    d1 = json.loads(rs.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('message') == 'File headers are incorrect'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('message') == "Los encabezados de archivo son incorrectos"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('message') == "Los encabezados de archivo son incorrectos"


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_upload_file_type_invalid(flask_app, session):
    """ Verify that bulk-upload api detects invalid/incorrect file type"""

    file_name = FILE_PATH + 'sample_pdf_csv.pdf.csv'
    with open(file_name, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'operator': 'jazz',
        'file': (BytesIO(file_content), 'sample_pdf_csv.pdf.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 403
    d1 = json.loads(rs.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('message') == 'File content is not Correct'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('message') == "El contenido del archivo no es correcto"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('message') == "Konten file tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_upload_no_file_or_incorrect(flask_app, session):
    """ Verify that bulk-upload api detects no file or invalid/incorrect file"""

    file_name = FILE_PATH + 'sample_proper_file.csv'
    with open(file_name, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'operator': 'jazz',
        'file': (BytesIO(file_content), '')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('message') == 'Please select csv/txt file'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('message') == "Por favor seleccione el archivo csv/txt"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('message') == "Silakan pilih file csv/txt"


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_upload_validation_invalid_mno(flask_app, session):
    """ Verify that bulk-upload api detects invalid/incorrect operator name"""

    file_name = FILE_PATH + 'sample_proper_file.csv'
    with open(file_name, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'operator': 'j@zz',
        'file': (BytesIO(file_content), 'sample_proper_file.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert d1['message']['operator'][0] == 'Operator name is not correct'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1['message']['operator'][0] == "El nombre del operador no es correcto."
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1['message']['operator'][0] == "Nama operator tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_upload_validation_txt_file(flask_app, session):
    """ Verify that bulk-upload api can accept .txt files"""

    file_name = FILE_PATH + 'sample_text_file.txt'
    with open(file_name, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'operator': 'telenor',
        'file': (BytesIO(file_content), 'sample_text_file.txt')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    assert rs.status_code == 200
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('msg') == 'File loaded successfully'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('msg') == "Archivo cargado correctamente"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('msg') == "File berhasil dimuat"


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_upload_validation_wrong_extention_file(flask_app, session):
    """ Verify that bulk-upload api can detect files with wrong extensions"""

    file_name = FILE_PATH + 'sample_pdf.pdf'
    with open(file_name, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'operator': 'ufone',
        'file': (BytesIO(file_content), 'sample_pdf.pdf')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('message') == 'Please select csv/txt file'
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('message') == "Por favor seleccione el archivo csv/txt"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('message') == "Silakan pilih file csv/txt"


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_upload_error__404_wrong_api(flask_app, db):
    """ Verify that bulk-upload api prompts when Error-404 is occurred """
    tmp_api = 'api/v1/mnooo-bulkkk-uploaddd'
    data = {
        'operator': 'zong',
        'file': (BytesIO(b'test'), 'sample_proper_file.csv')
    }
    rs = flask_app.post(tmp_api, buffered=True, content_type='multipart/form-data', data=data)
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert rs.status_code == 404


# noinspection PyUnusedLocal,PyShadowingNames
def test_bulk_upload_error__405_method_not_allowed(flask_app, db):
    """ Verify that bulk-upload api prompts when Error-405 is occurred """
    res1 = flask_app.get(MNO_BULK_UPLOAD)
    assert res1.status_code == 405
    res2 = flask_app.put(MNO_BULK_UPLOAD)
    assert res2.status_code == 405
    res3 = flask_app.delete(MNO_BULK_UPLOAD)
    assert res3.status_code == 405
    res4 = flask_app.patch(MNO_BULK_UPLOAD)
    assert res4.status_code == 405
