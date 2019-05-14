"""
Unit Test Module for Authority-Input API
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

# noinspection PyUnresolvedReferences,PyProtectedMember
from tests._fixtures import *
# noinspection PyProtectedMember
from tests._helpers import *
import json

ATHTY_INPUT = 'api/v1/sbmt-dev-info'
HEADERS = {'Content-Type': "application/json"}


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_happy_case(flask_app, db):
    """Verify that athty-input api response correctly when all parameters are valid"""
    country_code = '92'
    imei = ["37327433394FBC5", "386735ABC903832"]
    payload = athty_input_payload(country_code, "3002161904",
                                  "Mate-10", "HUAWEI", "X5TrgPq", "4G", imei, "9A-34-CD-4E-EB:FA")

    rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
    print(rsl.data)
    assert rsl.status_code == 200
    data = json.loads(rsl.data.decode('utf-8'))
    assert data.get('msg') == "Device's information has been successfully loaded"
    rs2 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
    print(rs2.data)
    assert rs2.status_code == 422
    data = json.loads(rs2.data.decode('utf-8'))
    assert data.get('Error') == "Device with same Serial number already exists"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_invalid_counrty_code(flask_app, db):
    """Verify that athty-input api doesn't allow invalid country-code"""
    country_code = '0971'
    imei = ["37327433394FBC5", "386735ABC903832"]
    payload = athty_input_payload(country_code, "3002161904", "Mate-10", "HUAWEI", "X5TrgPq", "4G", imei,
                                  "9A-34-CD-4E-EB:FA")
    rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
    print(rsl.data)
    assert rsl.status_code == 422
    data = json.loads(rsl.data.decode('utf-8'))
    assert data.get('Error') == 'Contact-MSISDN format is not correct'


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_invalid_subscriber_no(flask_app, db):
    """Verify that athty-input api doesn't allow invalid subscriber-number (SN)"""
    sn = ['30021619047892364', '30a21D19x4', '30@216!904$']
    imei = ["37327433394FBC5", "386735ABC903832"]
    for val in sn:
        payload = athty_input_payload("92", val, "Mate-10", "HUAWEI", "X5TrgPq", "4G", imei,
                                      "9A-34-CD-4E-EB:FA")
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print(rsl.data)
        assert rsl.status_code == 422
        data = json.loads(rsl.data.decode('utf-8'))
        assert data.get('Error') == 'Contact-MSISDN format is not correct'


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_invalid_rat_formats(flask_app, db):
    """Verify that athty-input api doesn't allow invalid rat"""
    imei = ["37327433394FBC5", "386735ABC903832"]
    rat = ['5G,6G', '6G', '6g', 'GSM', 'GSM,WCDMA', 'GSM,LTE', 'GSM,WCDMA,LTE', 'gsm,wcdma,lte',
           'LTE', '2G:3G:4G', '2G-3G-4G', '2G/3G', '3G;4G', '2g,3g,4g', '@ny_0th3r sTr!ng']
    for val in rat:
        payload = athty_input_payload("92", "3002161904", "Mate-10", "HUAWEI", "X5TrgPq", val, imei,
                                      "9A-34-CD-4E-EB:FA")
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print(rsl.data, val)
        assert rsl.status_code == 422
        data = json.loads(rsl.data.decode('utf-8'))
        assert data.get('Error') == 'RAT format is not correct'


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_valid_rat_formats(flask_app, db):
    """Verify that athty-input api allows only valid rat"""
    imei = ["37327433394FBC5", "386735ABC903832"]
    rat = ['2G', '3G', '4G', '5G', '5G,3G', '2G,4G', '2G,5G', '3G,4G', '3G,5G', '4G,5G',
           '2G,3G,4G', '3G,4G,5G', '4G,5G,2G', '2G,3G,4G,5G']
    for val in rat:
        payload = athty_input_payload("92", "3002161904", "Mate-10", "HUAWEI", 'D4tUo09C', val, imei,
                                      "9A-34-CD-4E-EB:FA")
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print("valid RAT format: ", val)
        # assert rsl.status_code == 200
        data = json.loads(rsl.data.decode('utf-8'))
        assert not data.get('Error') == 'RAT format is not correct'


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_valid_mac_formats(flask_app, db):
    """Verify that athty-input api allows only valid mac"""
    imei = ["37327433394FBC5", "386735ABC903832"]
    mac = ["AA:AA:AA:FF:FF:FF", "AA-AA-AA-FF-FF-FF", "AAA.AAA.FFF.FFF",
           "00:25:96:FF:FE:12:34:56", "0025:96FF:FE12:3456"]
    serial_no = 'X'
    for val in mac:
        payload = athty_input_payload("92", "3002161904", "Mate-10", "HUAWEI", serial_no, "2G", imei, val)
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print("Valid MAC format: ", val)
        serial_no = serial_no + serial_no
        assert rsl.status_code == 200
        data = json.loads(rsl.data.decode('utf-8'))
        assert data.get('msg') == "Device's information has been successfully loaded"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_invalid_mac_formats(flask_app, db):
    """Verify that athty-input api doesn't allow invalid mac"""
    imei = ["37327433394FBC5", "386735ABC903832"]
    mac = ["AC:AA:aH:FF:FF:8n", "AA:AA:AA:FF:FF", "AA-AA-AA-FF-FF-FF-FF", "AAA.AAA.FFF.FFF.AAA",
           "AAA.AAA.FFF", "00:25:96:FF:FE:12:34:56:FE", "0025:96FF:FE12", "0025:96FF:FE12:3456:A1CE",
           "AL-@M-AA-XX-7$-d&", "00:25:96:GH:%E:12:YZ:5#", "0A2T:9@Fv:Fz1?:34|6"]
    for val in mac:
        payload = athty_input_payload("92", "3002161904", "Mate-10", "HUAWEI", "Xc5dt8KlT", "2G,3G", imei, val)
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print(rsl.data, val)
        assert rsl.status_code == 422
        data = json.loads(rsl.data.decode('utf-8'))
        assert data.get('Error') == "MAC format is not correct"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_invalid_mac_espanish_msg(flask_app, db):
    """Verify that athty-input api doesn't allow invalid mac"""

    HEADERS = {'Content-Type': "application/json", 'Accept-Language': 'es'}
    imei = ["37327433394FBC5", "386735ABC903832"]
    mac = ["AC:AA:aH:FF:FF:8n", "AA:AA:AA:FF:FF", "AA-AA-AA-FF-FF-FF-FF", "AAA.AAA.FFF.FFF.AAA",
           "AAA.AAA.FFF", "00:25:96:FF:FE:12:34:56:FE", "0025:96FF:FE12", "0025:96FF:FE12:3456:A1CE",
           "AL-@M-AA-XX-7$-d&", "00:25:96:GH:%E:12:YZ:5#", "0A2T:9@Fv:Fz1?:34|6"]
    for val in mac:
        payload = athty_input_payload("92", "3002161904", "Mate-10", "HUAWEI", "Xc5dt8KlT", "2G,3G", imei, val)
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print(rsl.data, val)
        assert rsl.status_code == 422
        data = json.loads(rsl.data.decode('utf-8'))
        assert data.get('Error') == "El formato MAC no es correcto"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_invalid_mac_indonesian_msg(flask_app, db):
    """Verify that athty-input api doesn't allow invalid mac"""

    HEADERS = {'Content-Type': "application/json", 'Accept-Language': 'id'}
    imei = ["37327433394FBC5", "386735ABC903832"]
    mac = ["AC:AA:aH:FF:FF:8n", "AA:AA:AA:FF:FF", "AA-AA-AA-FF-FF-FF-FF", "AAA.AAA.FFF.FFF.AAA",
           "AAA.AAA.FFF", "00:25:96:FF:FE:12:34:56:FE", "0025:96FF:FE12", "0025:96FF:FE12:3456:A1CE",
           "AL-@M-AA-XX-7$-d&", "00:25:96:GH:%E:12:YZ:5#", "0A2T:9@Fv:Fz1?:34|6"]
    for val in mac:
        payload = athty_input_payload("92", "3002161904", "Mate-10", "HUAWEI", "Xc5dt8KlT", "2G,3G", imei, val)
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print(rsl.data, val)
        assert rsl.status_code == 422
        data = json.loads(rsl.data.decode('utf-8'))
        assert data.get('Error') == "Format MAC tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_model_formats(flask_app, db):
    """Verify that athty-input api doesn't allow invalid mac"""
    imei = ["37327433394FBC5", "386735ABC903832"]
    model = ["Mate-10", "Nokia.8", "iPhone_Max", "Note 5", "qoute's_Phone", ]
    for val in range(0, 5):
        payload_1 = athty_input_payload("92", "3002161904", model[val], "Samsung",
                                        "Xc5dtT", "4G", imei, "9A-34-CD-4E-EB:FA")
        rsl_1 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload_1))
        print("Valid Model Format: ", model[val])
        data = json.loads(rsl_1.data.decode('utf-8'))
        assert not data.get('Error') == "Model format is not correct"
    invalid_model = "Nok!@-2"
    payload_2 = athty_input_payload("92", "3002161904", invalid_model, "Samsung",
                                    "Xc5dtT", "4G", imei, "9A-34-CD-4E-EB:FA")
    rsl_2 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload_2))
    data_2 = json.loads(rsl_2.data.decode('utf-8'))
    print(rsl_2.data, invalid_model)
    assert data_2.get('Error') == "Model format is not correct"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_brand_formats(flask_app, db):
    """Verify that athty-input api doesn't allow invalid mac"""
    imei = ["37327433394FBC5", "386735ABC903832"]
    brand = ["Nok!@", "HU@we!", "S0Ny~~", "Q:Mob!@#$%&*()Le+"]
    for val in range(0, 4):
        payload_1 = athty_input_payload("92", "3002161904", "Nokia-8", brand[val],
                                        "Xc5dtT", "4G", imei, "9A-34-CD-4E-EB:FA")
        rsl_1 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload_1))
        data = json.loads(rsl_1.data.decode('utf-8'))
        print(rsl_1.data, brand[val])
        assert data.get('Error') == "Brand format is not correct"
    valid_brand = "H_u.a-w'e i"
    payload_2 = athty_input_payload("92", "3002161904", "Nokia-8", valid_brand,
                                    "Xc5dtT", "4G", imei, "9A-34-CD-4E-EB:FA")
    rsl_2 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload_2))
    data_2 = json.loads(rsl_2.data.decode('utf-8'))
    print("Valid Brand format(s): ", valid_brand)
    assert not data_2.get('Error') == "Brand format is not correct"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_imei_formats(flask_app, db):
    """Verify that athty-input api doesn't allow invalid mac"""
    imei = ["313789A", "3100937A6881478C5", "819G63455K18RT6", "31678@8&909*1#6", "7b9f1a7d99c8d3e"]
    payload = athty_input_payload("92", "3002161904", "Mate7", "HUAWEI", "T68FePq", "4G", imei, "9A-34-CD-4E-EB:FA")
    rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
    data = json.loads(rsl.data.decode('utf-8'))
    print(rsl.data)
    assert rsl.status_code == 422
    assert data.get('Error') == "IMEI format is not correct"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_invalid_serial_no(flask_app, db):
    """Verify that athty-input api doesn't allow invalid subscriber-number (SN)"""
    serial = ['T68-FePq', 'K0@2a6!M04$']
    imei = ["37327433394FBC5", "386735ABC903832"]
    for val in serial:
        payload = athty_input_payload("92", "3035161904", "Mate-9", "HUAWEI", val, "4G", imei, "9A-34-CD-4E-EB:FA")
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print(rsl.data, val)
        assert rsl.status_code == 422
        data = json.loads(rsl.data.decode('utf-8'))
        assert data.get('Error') == 'Serial-Number format is not correct'


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_error__404_wrong_api(flask_app, db):
    """ Verify that athty-input api prompts when Error-400 is occurred """
    tmp_api = 'api/v1/sbmtttt-devvvv-infoooo'
    imei = ["37327444494FBC5", "386735ABC905652"]
    payload = athty_input_payload("92", "3452176804", "F-7", "OPPO", "G6S9dRtj", "4G", imei, "9A-34-CD-4E-EB:FA")
    rsl = flask_app.post(tmp_api, headers=HEADERS, data=json.dumps(payload))
    dataa = json.loads(rsl.data.decode('utf-8'))
    print(dataa)
    assert rsl.status_code == 404


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_error_405_method_not_allowed(flask_app, db):
    """ Verify that athty-input api prompts when Error-405 is occurred """
    res1 = flask_app.get(ATHTY_INPUT)
    assert res1.status_code == 405
    res2 = flask_app.put(ATHTY_INPUT)
    assert res2.status_code == 405
    res3 = flask_app.delete(ATHTY_INPUT)
    assert res3.status_code == 405
    res4 = flask_app.patch(ATHTY_INPUT)
    assert res4.status_code == 405


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_missing_parameters(flask_app, db):
    """ Verify that athty-input api prompts when any parameter is missing """
    imei = ["278364974027487", "238409485761298"]
    for cond in range(1, 8):
        pl_1 = athty_input_payload("92", "3002161904", "Mate-6", "HUAWEI",
                                   "He5aZPq", "4G", imei, "9A-34-CD-4E-EB:FA", cond)
        rs_1 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(pl_1))
        print(rs_1.data)
        assert rs_1.status_code == 422
        d1 = json.loads(rs_1.data.decode('utf-8'))
        if cond == 1:
            assert d1.get('Error') == 'Country-Code not found'
        if cond == 2:
            assert d1.get('Error') == 'Subscriber-Number not found'
        if cond == 3:
            assert d1.get('Error') == 'MODEL not found'
        if cond == 4:
            assert d1.get('Error') == 'BRAND not found'
        if cond == 5:
            assert d1.get('Error') == 'Serial_No not found'
        if cond == 6:
            assert d1.get('Error') == 'RAT not found'
        if cond == 7:
            assert d1.get('Error') == 'IMEI not found'


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_missing_mac(flask_app, db):
    """ Verify that athty-input api works correctly when optional mac is missing """
    imei = ["278364974027487", "238409485761298"]
    pl = athty_input_payload("92", "3002161904", "Mate-6", "HUAWEI", "He5aZPq", "4G", imei)
    rs = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(pl))
    assert rs.status_code == 200
    d1 = json.loads(rs.data.decode('utf-8'))
    print(d1)
    assert d1.get('msg') == "Device's information has been successfully loaded"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_functionality_single_contact_multiple_devices(flask_app, db):
    """ Verify that athty-input api can register multiple devices via single contact number """
    imei = ["278364974027487", "238409485761298"]
    pl1 = athty_input_payload("92", "3002161904", "Mate-7", "HUAWEI",
                              "He5xas3q", "4G", imei, "9A-34-CD-4E-EB:FA")
    pl2 = athty_input_payload("92", "3002161904", "OnePLus6", "Oneplus",
                              "SG7U9OnA", "4G", imei, "9A-34-CD-4E-22:FA")
    pl3 = athty_input_payload("92", "3479273047", "Nokia-8", "NOKIA", "Q2jsu8cx",
                              "3G,4G", imei, "FF-45-BE-4C-47:DA")

    rs1 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(pl1))
    rs2 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(pl2))
    rs3 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(pl3))
    assert rs1.status_code == 200
    assert rs2.status_code == 200
    assert rs3.status_code == 200
    d1 = json.loads(rs1.data.decode('utf-8'))
    d2 = json.loads(rs2.data.decode('utf-8'))
    d3 = json.loads(rs3.data.decode('utf-8'))
    print(d1, d2)
    assert d1.get('msg') == "Device's information has been successfully loaded"
    assert d2.get('msg') == "Device's information has been successfully loaded"
    assert d3.get('msg') == "Device's information has been successfully loaded"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_functionality_max_imeis_per_device(flask_app, db):
    """Verify that athty-input api allows only 5 IMEIs per device"""
    country_code = '92'
    imei_1 = ["111111111111111", "222222222222222", "333333333333333",
              "444444444444444", "555555555555555"]
    imei_2 = ["111111111111111", "222222222222222", "333333333333333",
              "444444444444444", "555555555555555", "666666666666666"]
    pl_1 = athty_input_payload(country_code, "3002161904", "Mate-10", "HUAWEI",
                               "Aq2dfur7", "4G", imei_1, "9A-34-CD-4E-EB:FA")
    pl_2 = athty_input_payload(country_code, "3002161904", "Mate-10", "HUAWEI",
                               "9Hu3edoG", "4G", imei_2, "9A-34-CD-4E-EB:FA")

    rsl_1 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(pl_1))
    print(rsl_1.data)
    assert rsl_1.status_code == 200
    d1 = json.loads(rsl_1.data.decode('utf-8'))
    assert d1.get('msg') == "Device's information has been successfully loaded"
    rsl_2 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(pl_2))
    print(rsl_2.data)
    assert rsl_2.status_code == 422
    d2 = json.loads(rsl_2.data.decode('utf-8'))
    assert d2.get('Error') == "Up to 5 IMEIs per device are allowed only"
