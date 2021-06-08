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
# noinspection PyProtectedMember
from tests._helpers import *
import json
from app import conf


ATHTY_INPUT = 'api/v1/device-reg'
HEADERS = {'Content-Type': "application/json"}


# noinspection PyUnusedLocal,PyShadowingNames,DuplicatedCode
def test_athty_input_happy_case(flask_app, db):
    """Verify that device registration api response correctly when all parameters are valid"""

    imei = ["37327433394FBC5", "386735ABC903832"]
    payload = athty_input_payload("923002161904", "Mate-10", "HUAWEI", "X5TrgPq", "4G", imei, "9A-34-CD-4E-EB:FA")

    rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
    print(rsl.data)
    assert rsl.status_code == 200
    data = json.loads(rsl.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert data.get('message') == "Device's information has been successfully loaded"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data.get('message') == "La información del dispositivo se ha cargado correctamente"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data.get('message') == "Informasi perangkat telah berhasil dimuat"


# noinspection PyUnusedLocal,PyShadowingNames,DuplicatedCode
def test_athty_functionality_unique_serial_no(flask_app, db):
    """Verify that device registration api only accepts unique serial_no"""

    imei = ["37327433394FBC5", "386735ABC903832"]
    payload = athty_input_payload("923002161904", "Mate-10", "HUAWEI", "X5TrgPq", "4G", imei, "9A-34-CD-4E-EB:FA")
    rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
    print(rsl.data)
    rs2 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
    print(rs2.data)
    assert rs2.status_code == 422
    data = json.loads(rs2.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert data.get('message') == "Device with same Serial number already exists"
    elif conf['supported_languages']['default_language'] == 'es':
        assert data.get('message') == "El dispositivo con el mismo número de serie ya existe"
    elif conf['supported_languages']['default_language'] == 'id':
        assert data.get('message') == "Perangkat dengan nomor seri yang sama sudah ada"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_invalid_contact_no(flask_app, db):
    """Verify that athty-input api doesn't allow invalid MSISDN for contact number"""

    sn = ['9230021619047892364', '0O9230a21D19x4', '30@216!904$', '']
    imei = ["37327433394FBC5", "386735ABC903832"]
    for val in sn:
        payload = athty_input_payload(val, "Mate-10", "HUAWEI", "X5TrgPq", "4G", imei,
                                      "9A-34-CD-4E-EB:FA")
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print("\nContact_No : ", val, "\n", rsl.data)
        assert rsl.status_code == 422
        data = json.loads(rsl.data.decode('utf-8'))
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['contact_no'][0] == 'MSISDN format is not correct'
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['contact_no'][0] == "El formato MSISDN no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['contact_no'][0] == "Format MSISDN tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_invalid_rat_formats(flask_app, db):
    """Verify that athty-input api doesn't allow invalid rat"""
    imei = ["37327433394FBC5", "386735ABC903832"]
    rat = ['5G,6G', '6G', '6g', 'GSM', 'GSM,WCDMA', 'GSM,LTE', 'GSM,WCDMA,LTE', 'gsm,wcdma,lte',
           'LTE', '2G:3G:4G', '2G-3G-4G', '2G/3G', '3G;4G', '2g,3g,4g', '', '@ny_0th3r sTr!ng']
    for val in rat:
        payload = athty_input_payload("+923002161904", "Mate-10", "HUAWEI", "X5TrgPq", val, imei,
                                      "9A-34-CD-4E-EB:FA")
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print("\nRAT : ", val, "\n", rsl.data)
        # assert rsl.status_code == 422
        data = json.loads(rsl.data.decode('utf-8'))
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['rat'][0] == 'RAT is not correct'
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['rat'][0] == "RAT no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['rat'][0] == "RAT tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_valid_rat_formats(flask_app, db):
    """Verify that athty-input api allows only valid rat"""
    imei = ["37327433394FBC5", "386735ABC903832"]
    rat = ['2G', '3G', '4G', '5G', '5G,3G', '2G,4G', '2G,5G', '3G,4G', '3G,5G', '4G,5G',
           '2G,3G,4G', '3G,4G,5G', '4G,5G,2G', '2G,3G,4G,5G']
    for val in rat:
        payload = athty_input_payload("923002161904", "Mate-10", "HUAWEI", 'D4tUo09C', val, imei,
                                      "9A-34-CD-4E-EB:FA")
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print("valid RAT format: ", val)
        # assert rsl.status_code == 200
        data = json.loads(rsl.data.decode('utf-8'))
        if conf['supported_languages']['default_language'] == 'en':
            assert not data == 'RAT is not correct'
        elif conf['supported_languages']['default_language'] == 'es':
            assert not data == "RAT no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert not data == "RAT tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_valid_mac_formats(flask_app, db):
    """Verify that athty-input api allows only valid mac"""
    imei = ["37327433394FBC5", "386735ABC903832"]
    mac = ["AA:AA:AA:FF:FF:FF", "AA-AA-AA-FF-FF-FF", "AAA.AAA.FFF.FFF",
           "00:25:96:FF:FE:12:34:56", "0025:96FF:FE12:3456"]
    serial_no = 'X'
    for val in mac:
        payload = athty_input_payload("923002161904", "Mate-10", "HUAWEI", serial_no, "2G", imei, val)
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print("\nValid MAC format: ", val)
        print(rsl.data)
        serial_no = serial_no + serial_no
        assert rsl.status_code == 200
        data = json.loads(rsl.data.decode('utf-8'))
        assert not data.get('message') == "MAC format is not correct"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_invalid_mac_english_msg(flask_app, db):
    """Verify that athty-input api doesn't allow invalid mac"""
    imei = ["37327433394FBC5", "386735ABC903832"]
    mac = ["AC:AA:aH:FF:FF:8n", "AA:AA::AA:FF:FF", "Aa-AA-AA-Ff-FF-FF-FF", "AAA.AAA.FFF.FFF.AAAAA",
           "AAA.AAA.FFF", "00:25:96:FF:FE:12:34:56:FE", "0025:96FF:FE12", "AL-@M-AA-XX-7$-d&",
           "00:25:96:GH:%E:12:YZ:5#", "0A2T:9@Fv:Fz1?:34|6", "A:4:B:C:5", "12345:ABCDE",
           "0025:96FF:FE12:3456:A1CE:FD6C:5561:ABCD:1234", "AB:BC"]
    for val in mac:
        payload = athty_input_payload("923002161904", "Mate-10", "HUAWEI", "Xc5dt8KlT", "2G,3G", imei, val)
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print("\n MAC :", val, "\n", rsl.data)
        assert rsl.status_code == 422
        data = json.loads(rsl.data.decode('utf-8'))
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['mac'][0] == "MAC format is not correct"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_invalid_mac_espanish_msg(flask_app, db):
    """Verify that athty-input api doesn't allow invalid mac"""

    HEADERS = {'Content-Type': "application/json", 'Accept-Language': 'es'}
    imei = ["37327433394FBC5", "386735ABC903832"]
    mac = ["AC:AA:aH:FF:FF:8n", "AA:AA::AA:FF:FF", "Aa-AA-AA-Ff-FF-FF-FF", "AAA.AAA.FFF.FFF.AAAAA",
           "AAA.AAA.FFF", "00:25:96:FF:FE:12:34:56:FE", "0025:96FF:FE12", "AL-@M-AA-XX-7$-d&",
           "00:25:96:GH:%E:12:YZ:5#", "0A2T:9@Fv:Fz1?:34|6", "A:4:B:C:5", "12345:ABCDE",
           "0025:96FF:FE12:3456:A1CE:FD6C:5561:ABCD:1234", "AB:BC"]
    for val in mac:
        payload = athty_input_payload("923002161904", "Mate-10", "HUAWEI", "Xc5dt8KlT", "2G,3G", imei, val)
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print("\n MAC :", val, "\n", rsl.data)
        assert rsl.status_code == 422
        data = json.loads(rsl.data.decode('utf-8'))
        if conf['supported_languages']['default_language'] == 'es':
            assert data['message']['mac'][0] == "El formato MAC no es correcto"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_invalid_mac_indonesian_msg(flask_app, db):
    """Verify that athty-input api doesn't allow invalid mac"""

    HEADERS = {'Content-Type': "application/json", 'Accept-Language': 'id'}
    imei = ["37327433394FBC5", "386735ABC903832"]
    mac = ["AC:AA:aH:FF:FF:8n", "AA:AA::AA:FF:FF", "Aa-AA-AA-Ff-FF-FF-FF", "AAA.AAA.FFF.FFF.AAAAA",
           "AAA.AAA.FFF", "00:25:96:FF:FE:12:34:56:FE", "0025:96FF:FE12", "AL-@M-AA-XX-7$-d&",
           "00:25:96:GH:%E:12:YZ:5#", "0A2T:9@Fv:Fz1?:34|6", "A:4:B:C:5", "12345:ABCDE",
           "0025:96FF:FE12:3456:A1CE:FD6C:5561:ABCD:1234", "AB:BC"]
    for val in mac:
        payload = athty_input_payload("923002161904", "Mate-10", "HUAWEI", "Xc5dt8KlT", "2G,3G", imei, val)
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print("\n MAC :", val, "\n", rsl.data)
        assert rsl.status_code == 422
        data = json.loads(rsl.data.decode('utf-8'))
        if conf['supported_languages']['default_language'] == 'id':
            assert data['message']['mac'][0] == "Format MAC tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_valid_model_names(flask_app, db):
    """Verify that athty-input api allow certain valid model names"""
    imei = ["37327433394FBC5", "386735ABC903832"]
    model = ["Note-5", "Samsung's Model", "LG (ligHt)", "ViVo's V-3 (super-cam)"]
    for val in range(0, 4):
        payload_1 = athty_input_payload("923002161904", model[val], "Samsung",
                                        "Xc5dtT", "4G", imei, "9A-34-CD-4E-EB:FA")
        rsl_1 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload_1))
        print("\nValid Model Format: ", model[val])
        print(rsl_1.data)
        data = json.loads(rsl_1.data.decode('utf-8'))
        if conf['supported_languages']['default_language'] == 'en':
            assert not data.get('message') == "Model format is not correct"
        elif conf['supported_languages']['default_language'] == 'es':
            assert not data.get('message') == "El formato del modelo no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert not data.get('message') == "Format model tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_invalid_model_names(flask_app, db):
    """Verify that athty-input api doesn't allow invalid model names"""

    imei = ["37327433394FBC5", "386735ABC903832"]
    invalid_models = ["Nok!@-2", "Q_Mobile Z4", "ViVo.V3", "LG%g3", "Opp0^H4", "Xi&oM!*, X$$"]
    for val in invalid_models:
        payload_2 = athty_input_payload("923002161904", val, "Samsung",
                                        "Xc5dtT", "4G", imei, "9A-34-CD-4E-EB:FA")
        rsl_2 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload_2))
        data = json.loads(rsl_2.data.decode('utf-8'))
        print("\n MAC :", val, "\n", rsl_2.data)
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['model'][0] == "Model name is not correct"
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['model'][0] == "El nombre del modelo no es correcto."
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['model'][0] == "Nama model tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_invalid_brand_names(flask_app, db):
    """Verify that athty-input api doesn't allow invalid brand names"""
    imei = ["37327433394FBC5", "386735ABC903832"]
    brand = ["Nok!@", "HU@we!", "S0Ny~~", "Q:Mob!()Le+", "Vi#$Vo0", "Opp&*O", "Xi@0M%Ee", "Q_Mobil3", "Xiaom`i"]
    for val in brand:
        payload_1 = athty_input_payload("923002161904", "Nokia-8", val,
                                        "Xc5dtT", "4G", imei, "9A-34-CD-4E-EB:FA")
        rsl_1 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload_1))
        data = json.loads(rsl_1.data.decode('utf-8'))
        print(rsl_1.data, val)
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['brand'][0] == "Brand name is not correct"
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['brand'][0] == "La marca no es correcta"
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['brand'][0] == "Nama merek tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_valid_brand_names(flask_app, db):
    """Verify that athty-input api allow certain valid Brand names"""

    imei = ["37327433394FBC5", "386735ABC903832"]
    valid_brands = ["Hua wei", "N0k-iA", "QMobil3"]
    for val in valid_brands:
        payload_2 = athty_input_payload("923002161904", "Nokia-8", val,
                                        "Xc6dtT", "4G", imei, "9A-34-CD-4E-EB:FA")
        rsl_2 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload_2))
        data_2 = json.loads(rsl_2.data.decode('utf-8'))
        print("Valid Brand format(s): ", val)
        print(data_2.get('message'))
        if conf['supported_languages']['default_language'] == 'en':
            assert not data_2.get('message') == "Brand name is not correct"
        elif conf['supported_languages']['default_language'] == 'es':
            assert not data_2.get('message') == "La marca no es correcta"
        elif conf['supported_languages']['default_language'] == 'id':
            assert not data_2.get('message') == "Nama merek tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_validations_imei_formats(flask_app, db):
    """Verify that athty-input api doesn't allow invalid IMEIs"""
    imeis = ["313789A", "3100937A6881478C5", "819G63455K18RT6", "31678@8&909*1#6F", "7b9f1a7d99c8d3e"]
    for imei in imeis:
        payload = athty_input_payload("923002161904", "Mate7", "HUAWEI", "T68FePq", "4G", imei, "9A-34-CD-4E-EB:FA")
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        data = json.loads(rsl.data.decode('utf-8'))
        print("\n IMEI :", imei, "\n", rsl.data)
        assert rsl.status_code == 422
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['imei'][0] == "IMEI is not correct"
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['imei'][0] == "IMEI no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['imei'][0] == "IMEI tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames,DuplicatedCode
def test_athty_input_validations_invalid_serial_no(flask_app, db):
    """Verify that device registration api doesn't allow invalid Serial-number"""

    serial = ['T68-FePq', 'K0@2a6!M04$']
    imei = ["37327433394FBC5", "386735ABC903832"]
    for val in serial:
        payload = athty_input_payload("923035161904", "Mate-9", "HUAWEI", val, "4G", imei, "9A-34-CD-4E-EB:FA")
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        print("\n Serial_No :", val, "\n", rsl.data)
        assert rsl.status_code == 422
        data = json.loads(rsl.data.decode('utf-8'))
        if conf['supported_languages']['default_language'] == 'en':
            assert data['message']['serial_no'][0] == 'Serial Number is not correct'
        elif conf['supported_languages']['default_language'] == 'es':
            assert data['message']['serial_no'][0] == "El número de serie no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert data['message']['serial_no'][0] == "Nomor seri tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames,DuplicatedCode
def test_athty_input_validations_valid_serial_no(flask_app, db):
    """Verify that athty-input api only allow valid Serial-number."""

    serial = ['T68FePqG4B0', '12345678', 'abcdefgh', 'ABCDEVWXYZ']
    imei = ["37327433394FBC5", "386735ABC903832"]
    for val in serial:
        payload = athty_input_payload("923035161904", "Mate-9", "HUAWEI", val, "4G", imei, "9A-34-CD-4E-EB:FA")
        rsl = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(payload))
        assert rsl.status_code == 200
        data = json.loads(rsl.data.decode('utf-8'))
        print("\n Serial_No :", val, "\n", data.get('message'))
        if conf['supported_languages']['default_language'] == 'en':
            assert data.get('message') != 'Serial Number is not correct'
        elif conf['supported_languages']['default_language'] == 'es':
            assert not data.get('message') == "El número de serie no es correcto"
        elif conf['supported_languages']['default_language'] == 'id':
            assert not data.get('message') == "Nomor seri tidak benar"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_error__404_wrong_api(flask_app, db):
    """ Verify that athty-input api prompts when Error-400 is occurred """
    tmp_api = 'api/v1/sbmtttt-devvvv-infoooo'
    imei = ["37327444494FBC5", "386735ABC905652"]
    payload = athty_input_payload("923452176804", "F-7", "OPPO", "G6S9dRtj", "4G", imei, "9A-34-CD-4E-EB:FA")
    rsl = flask_app.post(tmp_api, headers=HEADERS, data=json.dumps(payload))
    dataa = json.loads(rsl.data.decode('utf-8'))
    print(dataa)
    assert rsl.status_code == 404


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_error_405_method_not_allowed(flask_app, db):
    """ Verify that athty-input api prompts when Error-405 is occurred """
    res1 = flask_app.get(ATHTY_INPUT)
    assert res1.status_code == 405
    print("\nHTTP-Method : GET \n msg : ", res1.data)
    res2 = flask_app.put(ATHTY_INPUT)
    assert res2.status_code == 405
    print("HTTP-Method : PUT \n msg : ", res2.data)
    res3 = flask_app.delete(ATHTY_INPUT)
    assert res3.status_code == 405
    print("HTTP-Method : DELETE \n msg : ", res3.data)
    res4 = flask_app.patch(ATHTY_INPUT)
    assert res4.status_code == 405
    print("HTTP-Method : PATCH \n msg : ", res4.data)


# noinspection PyUnusedLocal,PyShadowingNames,PyArgumentList
def test_athty_input_missing_parameters(flask_app, db):
    """ Verify that athty-input api prompts when any parameter is missing """

    imei = ["278364974027487", "238409485761298"]
    for cond in range(1, 7):

        pl_1 = athty_input_payload("923002161904", "Mate-6", "HUAWEI", "He5aZPq", "4G", imei,
                                   "9A-34-CD-4E-EB:FA", cond)
        rs_1 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(pl_1))
        d1 = json.loads(rs_1.data.decode('utf-8'))

        print("\n", rs_1.data)
        assert rs_1.status_code == 422
        if cond == 1:
            assert d1['message']['contact_no'][0] == "Missing data for required field."
        elif cond == 2:
            assert d1['message']['model'][0] == "Missing data for required field."
        elif cond == 3:
            assert d1['message']['brand'][0] == "Missing data for required field."
        elif cond == 4:
            assert d1['message']['serial_no'][0] == "Missing data for required field."
        elif cond == 5:
            assert d1['message']['rat'][0] == "Missing data for required field."
        elif cond == 6:
            assert d1['message']['imei'][0] == "Missing data for required field."


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_missing_mac(flask_app, db):
    """ Verify that athty-input api works correctly when optional mac is missing """

    imei = ["278364974027487", "238409485761298"]
    pl = athty_input_payload("923002161904", "Mate-6", "HUAWEI", "He5aZPq", "4G", imei, "9A-34-CD-4E-EB:FA", 7)
    rs = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(pl))
    print(rs.data)
    assert rs.status_code == 200
    d1 = json.loads(rs.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('message') == "Device's information has been successfully loaded"
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('message') == "La información del dispositivo se ha cargado correctamente"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('message') == "Informasi perangkat telah berhasil dimuat"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_functionality_single_contact_multiple_devices(flask_app, db):
    """ Verify that athty-input api can register multiple devices via single contact number """

    imei = ["278364974027487", "238409485761298"]
    pl1 = athty_input_payload("923002161904", "Mate-7", "HUAWEI",
                              "He5xas3q", "4G", imei, "9A-34-CD-4E-EB:FA")
    pl2 = athty_input_payload("923002161904", "OnePLus6", "Oneplus",
                              "SG7U9OnA", "4G", imei, "9A-34-CD-4E-22:FA")
    pl3 = athty_input_payload("923479273047", "Nokia-8", "NOKIA", "Q2jsu8cx",
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
    print("\n", d1, "\n", d2, "\n", d3)
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('message') == "Device's information has been successfully loaded"
        assert d2.get('message') == "Device's information has been successfully loaded"
        assert d3.get('message') == "Device's information has been successfully loaded"
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('message') == "La información del dispositivo se ha cargado correctamente"
        assert d2.get('message') == "La información del dispositivo se ha cargado correctamente"
        assert d3.get('message') == "La información del dispositivo se ha cargado correctamente"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('message') == "Informasi perangkat telah berhasil dimuat"
        assert d2.get('message') == "Informasi perangkat telah berhasil dimuat"
        assert d3.get('message') == "Informasi perangkat telah berhasil dimuat"


# noinspection PyUnusedLocal,PyShadowingNames
def test_athty_input_functionality_max_imeis_per_device(flask_app, db):
    """Verify that athty-input api allows only 5 IMEIs per device"""

    imei_1 = ["111111111111111", "222222222222222", "333333333333333",
              "444444444444444", "555555555555555"]
    imei_2 = ["111111111111111", "222222222222222", "333333333333333",
              "444444444444444", "555555555555555", "666666666666666"]
    pl_1 = athty_input_payload("923002161904", "Mate-10", "HUAWEI",
                               "Aq2dfur7", "4G", imei_1, "9A-34-CD-4E-EB:FA")
    pl_2 = athty_input_payload("923002161904", "Mate-10", "HUAWEI",
                               "9Hu3edoG", "4G", imei_2, "9A-34-CD-4E-EB:FA")

    rsl_1 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(pl_1))
    print(rsl_1.data)
    assert rsl_1.status_code == 200
    d1 = json.loads(rsl_1.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert d1.get('message') == "Device's information has been successfully loaded"
    elif conf['supported_languages']['default_language'] == 'es':
        assert d1.get('message') == "La información del dispositivo se ha cargado correctamente"
    elif conf['supported_languages']['default_language'] == 'id':
        assert d1.get('message') == "Informasi perangkat telah berhasil dimuat"

    rsl_2 = flask_app.post(ATHTY_INPUT, headers=HEADERS, data=json.dumps(pl_2))
    print(rsl_2.data)
    assert rsl_2.status_code == 422
    d2 = json.loads(rsl_2.data.decode('utf-8'))
    if conf['supported_languages']['default_language'] == 'en':
        assert d2['message']['imei'][0] == "Only 5 IMEIs per device are allowed"
    elif conf['supported_languages']['default_language'] == 'es':
        assert d2['message']['imei'][0] == "Solo se permiten 5 IMEI por dispositivo"
    elif conf['supported_languages']['default_language'] == 'es':
        assert d2['message']['imei'][0] == "Hanya 5 IMEI per perangkat yang diizinkan"
