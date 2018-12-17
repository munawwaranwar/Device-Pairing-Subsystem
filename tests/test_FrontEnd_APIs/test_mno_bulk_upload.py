"""
Unit Test Module for MNO-Bulk-Upload API
Copyright (c) 2018 Qualcomm Technologies, Inc.
 All rights reserved.
 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
 limitations in the disclaimer below) provided that the following conditions are met:
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
 disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
 disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
 products derived from this software without specific prior written permission.
 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
 THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
 TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.
"""

import json
from tests._fixtures import *
from io import BytesIO, StringIO


MNO_BULK_UPLOAD = 'api/v1/mno-bulk-upload'


def test_bulk_upload_happy_case_proper_file(flask_app, session):
    """ Verify that bulk-upload api uploads the file successfully"""
    file_path = '/var/www/html/dirbs-dps-api-1.0.0/tests/unittest_data/sample_files/sample_proper_file.csv'
    with open(file_path, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'mno': 'warid',
        'file': (BytesIO(file_content), 'sample_proper_file.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 200
    d1 = json.loads(rs.data.decode('utf-8'))
    assert d1.get('msg') == 'File successfully loaded'


def test_bulk_upload_file_duplicated_imsis(flask_app, session):
    """ Verify that bulk-upload api detects duplicated IMSIs in the file"""
    file_path = '/var/www/html/dirbs-dps-api-1.0.0/tests/unittest_data/sample_files/sample_duplicate_imsi.csv'
    with open(file_path, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'mno': 'jazz',
        'file': (BytesIO(file_content), 'sample_duplicate_imsi.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    assert d1.get('Error') == 'File contains duplicated IMSIs'


def test_bulk_upload_file_incorrect_content(flask_app, session):
    """ Verify that bulk-upload api detects file with invalid/incorrect content"""
    file_path = '/var/www/html/dirbs-dps-api-1.0.0/tests/unittest_data/sample_files/sample_content_incorrect.csv'
    with open(file_path, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'mno': 'jazz',
        'file': (BytesIO(file_content), 'sample_content_incorrect.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    assert d1.get('Error') == 'File content is not Correct'


def test_bulk_upload_file_with_errors(flask_app, session):
    """ Verify that bulk-upload api detects file with invalid/incorrect content"""
    file_path = '/var/www/html/dirbs-dps-api-1.0.0/tests/unittest_data/sample_files/sample_with_errors.csv'
    with open(file_path, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'mno': 'jazz',
        'file': (BytesIO(file_content), 'sample_with_errors.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 200
    d1 = json.loads(rs.data.decode('utf-8'))
    assert d1.get('msg') == 'File successfully loaded'
    assert not d1.get('link') == ''


def test_bulk_upload_file_headers_incorrect(flask_app, session):
    """ Verify that bulk-upload api detects file with invalid/incorrect content"""
    file_path = '/var/www/html/dirbs-dps-api-1.0.0/tests/unittest_data/sample_files/sample_without_headers.csv'
    with open(file_path, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'mno': 'telenor',
        'file': (BytesIO(file_content), 'sample_without_headers.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    assert d1.get('Error') == 'File headers are missing or incorrect'


def test_bulk_upload_file_type_invalid(flask_app, session):
    """ Verify that bulk-upload api detects file with invalid/incorrect content"""
    file_path = '/var/www/html/dirbs-dps-api-1.0.0/tests/unittest_data/sample_files/sample_pdf_csv.pdf.csv'
    with open(file_path, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'mno': 'jazz',
        'file': (BytesIO(file_content), 'sample_pdf_csv.pdf.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    assert d1.get('Error') == 'File type is not valid'


def test_bulk_upload_no_file_or_incorrect(flask_app, session):
    """ Verify that bulk-upload api detects file with invalid/incorrect content"""
    file_path = '/var/www/html/dirbs-dps-api-1.0.0/tests/unittest_data/sample_files/sample_proper_file.csv'
    with open(file_path, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'mno': 'jazz',
        'file': (BytesIO(file_content), '')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    assert d1.get('Error') == 'No file or improper file found'


def test_bulk_upload_validation_invalid_mno(flask_app, session):
    """ Verify that bulk-upload api detects file with invalid/incorrect content"""
    file_path = '/var/www/html/dirbs-dps-api-1.0.0/tests/unittest_data/sample_files/sample_proper_file.csv'
    with open(file_path, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'mno': 'j@zz',
        'file': (BytesIO(file_content), 'sample_proper_file.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    print(rs.data)
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    assert d1.get('Error') == 'improper Operator-name provided'


def test_bulk_upload_validation_txt_file(flask_app, session):
    """ Verify that bulk-upload api can accept .txt files"""
    file_path = '/var/www/html/dirbs-dps-api-1.0.0/tests/unittest_data/sample_files/sample_text_file.txt'
    with open(file_path, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'mno': 'telenor',
        'file': (BytesIO(file_content), 'sample_text_file.txt')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    assert rs.status_code == 200
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert d1.get('msg') == 'File successfully loaded'


def test_bulk_upload_validation_wrong_extention_file(flask_app, session):
    """ Verify that bulk-upload api can accept .txt files"""
    file_path = '/var/www/html/dirbs-dps-api-1.0.0/tests/unittest_data/sample_files/sample_pdf.pdf'
    with open(file_path, 'rb') as test_file:
        file_content = test_file.read()
    data = {
        'mno': 'ufone',
        'file': (BytesIO(file_content), 'sample_pdf.pdf')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data)
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert d1.get('Error') == 'No file or improper file found'


def test_bulk_upload_validation_wrong_api_parameters(flask_app, session):
    """ Verify that bulk-upload api can accept .txt files"""
    file_path = '/var/www/html/dirbs-dps-api-1.0.0/tests/unittest_data/sample_files/sample_proper_file.csv'
    with open(file_path, 'rb') as test_file:
        file_content = test_file.read()
    data_1 = {
        'mnoo': 'zong',
        'file': (BytesIO(file_content), 'sample_proper_file.csv')
    }
    test_file.close()
    rs = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data_1)
    assert rs.status_code == 422
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert d1.get('Error') == 'improper Operator-name provided'
    data_2 = {
        'mno': 'jazz',
        'fileee': (BytesIO(file_content), 'sample_proper_file.csv')
    }
    rs2 = flask_app.post(MNO_BULK_UPLOAD, buffered=True, content_type='multipart/form-data', data=data_2)
    assert rs.status_code == 422
    d2 = json.loads(rs2.data.decode('utf-8'))
    print(d2)
    assert d2.get('Error') == 'No file or improper file found'


def test_bulk_upload_error__404_wrong_api(flask_app, db):
    """ Verify that bulk-upload api prompts when Error-404 is occurred """
    tmp_api = 'api/v1/mnooo-bulkkk-uploaddd'
    data = {
        'mno': 'zong',
        'file': (BytesIO(b'test'), 'sample_proper_file.csv')
    }
    rs = flask_app.post(tmp_api, buffered=True, content_type='multipart/form-data', data=data)
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert rs.status_code == 404


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
