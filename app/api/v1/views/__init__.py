"""
DPS APIs' routes package.
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

from flask import Blueprint, Response, request, make_response, send_file
import json
from app import conf, app
from app.api.v1.common.athrty_search_form import SearchAuthority
from app.api.v1.common.generate_paircode import gen_paircode
from app.api.v1.common.additional_pair import add_pair
from app.api.v1.common.add_pair_confirmation import add_pair_cnfrm
from app.api.v1.common.rel_single_pair import rel_single
from app.api.v1.common.rel_all_pairs import rel_all
from app.api.v1.common.sim_change import sim_chg
from app.api.v1.common.verify_paircode import vfy_paircode
from app.api.v1.common.find_pairs import find_pairs
from app.api.v1.common.first_pair import first_pair
from app.api.v1.common.athrty_inpt_form import authority_input
from app.api.v1.common.mno_first_page import fetch_msisdns
from app.api.v1.common.mno_bulk_download import bulk_msisdns
from app.api.v1.common.mno_bulk_upload import BulkUpload
from app.api.v1.common.mno_sngl_upload import sngl_imsi
from app.api.v1.common.mno_error_file import error_url
from flask_babel import lazy_gettext as _


api = Blueprint('v1', __name__.split('.')[0])


@api.route('/base', methods=['GET'])
def base_api():
    data = {
        "messsage": "DPS API version 1"
    }
    return Response(json.dumps(data), status=200, mimetype='application/json')


@api.route('/paircode', methods=['GET'])
def gen_paircode2():
    pc1 = gen_paircode()
    data = {
        "Pair-Code": pc1
    }
    return Response(json.dumps(data), status=200, mimetype='application/json')


@api.route('/first-pair', methods=['POST'])
def fst_pair():
    req_data = request.get_json()
    pair_code = req_data.get('Pair_Code')
    sender_no = req_data.get('Sender_No')
    mno = req_data.get('Operator')
    if not pair_code:
        return "Pair-Code is missing in SMS"
    if not sender_no:
        return "sender number is missing in SMS"
    if not mno:
        return "operator's name is missing in SMS"
    message, stat = first_pair(pair_code, sender_no, mno)

    return Response(json.dumps(message), status=stat, mimetype='text/html')


@api.route('/add-pair', methods=['POST'])
def add_pairs():
    req_data = request.get_json()
    sender_no = req_data.get('Sender_No')
    add_msisdn = req_data.get('MSISDN')
    if not sender_no:
        return "primary number is missing in SMS"
    if not add_msisdn:
        return "secondary number is missing in SMS"
    message = add_pair(add_msisdn, sender_no)

    return message


@api.route('/add-cnfrm', methods=['PUT'])
def add_cnfrm():
    req_data = request.get_json()
    header = req_data.get('Confirm')
    sender_no = req_data.get('Sender_No')
    primary_msisdn = req_data.get('Primary_No')
    mno = req_data.get('Operator')
    if not header:
        return "Confirmation is missing in SMS"
    if not sender_no:
        return "Sender number is missing in SMS"
    if not primary_msisdn:
        return "Primary number is missing in SMS"
    if not mno:
        return "Operator's name is missing in SMS"

    message = add_pair_cnfrm(header, primary_msisdn, sender_no, mno)
    return message


@api.route('/rel-single', methods=['DELETE'])
def rel_sngl():
    req_data = request.get_json()
    del_msisdn = req_data.get('MSISDN')
    sender_no = req_data.get('Sender_No')
    if not sender_no:
        return "Sender number is missing in SMS"
    if not del_msisdn:
        return "Secondary number is missing in SMS"

    message = rel_single(del_msisdn, sender_no)
    return message


@api.route('/rel-all', methods=['DELETE'])
def release_all():
    req_data = request.get_json()
    sender_no = req_data.get('Sender_No')
    if not sender_no:
        return "Sender number is missing in SMS"

    message = rel_all(sender_no)
    return message


@api.route('/sim-chg', methods=['DELETE'])
def sim_change():
    req_data = request.get_json()
    sender_no = req_data.get('Sender_No')
    mno = req_data.get('Operator')
    if not sender_no:
        return "Sender number is missing in SMS"
    if not mno:
        return "Operator's name is missing in SMS"

    message = sim_chg(sender_no, mno)
    return message


@api.route('/vfy-paircode', methods=['GET'])
def vrfy_paircode():
    paircode = request.args.get('Pair_Code')
    sms_imei = request.args.get('IMEI')
    if not paircode:
        return "Pair-Code is missing in SMS"
    if not sms_imei:
        return "IMEI is missing in SMS"

    message = vfy_paircode(paircode, sms_imei)
    return message


@api.route('/find-pairs', methods=['GET'])
def find_pair():
    sender_no = request.args.get('Sender_No')
    if not sender_no:
        return "Sender number is missing in SMS"

    message = find_pairs(sender_no)
    if message == []:
        message = "No Pair is associated with ({})".format(sender_no)
    return Response(json.dumps(message), status=200, mimetype='text/html')


@api.route('/sbmt-dev-info', methods=['POST'])
def sbmt_dev_info():
    args = ['CONTACT', 'MODEL', 'BRAND', 'Serial_No', 'RAT', 'IMEI']
    mac = None
    req_data = request.get_json()
    for key in args:
        if key not in req_data:
            data = {'Error': _('%(key)s not found', key=key)}
            return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')

    for k in req_data:
        if k == 'CONTACT':
            contact = req_data.get('CONTACT')
            if 'CC' in contact:
                cc = contact.get("CC")
            else:
                data = {"Error": _("Country-Code not found")}
                return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')
            if 'SN' in contact:
                sn = contact.get("SN")
            else:
                data = {"Error": _("Subscriber-Number not found")}
                return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')
        elif k == 'MODEL':
            model = req_data.get('MODEL')
        elif k == 'BRAND':
            brand = req_data.get('BRAND')
        elif k == 'Serial_No':
            serial_no = req_data.get('Serial_No')
        elif k == 'RAT':
            rat = req_data.get('RAT')
        elif k == 'IMEI':
            imei = req_data.get('IMEI')
        elif k == 'MAC':
            mac = req_data.get('MAC')

    if not mac:
        mac = None

    if imei and len(imei) <= conf['imeis_per_device']:
        message, stat = authority_input(contact, model, brand, serial_no, mac, rat, imei)
        return Response(app.j_encoder.encode(message), status=stat, mimetype='application/json')
    else:
        data = {
                "Error": _("Up to %(var1)s IMEIs per device are allowed only", var1=conf['imeis_per_device'])
               }
        return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')


@api.route('/authority-search', methods=['POST'])
def athrty_search():
    existance = {"mac_exist": False, "serial_exist": False, "contact_exist": False, "imei_exist": False}
    args = request.get_json()
    limit = args.get("limit")
    start = args.get("start")
    if 'search_args' in args:
        req_data = args.get("search_args")
    else:
        data = {"Error": _("search_args is not correct")}
        return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')
    for key in req_data:
        if key == 'MAC':
            existance['mac_exist'] = True
        elif key == 'CONTACT':
            existance['contact_exist'] = True
        elif key == 'Serial_No':
            existance['serial_exist'] = True
        elif key == 'IMEI':
            existance['imei_exist'] = True
        else:
            data = {
                "Error": "one or more parameters are not correct"
            }
            return Response(json.dumps(data), status=422, mimetype='application/json')


    count = len(req_data)
    msg, stat = SearchAuthority.authority_search(start, limit, req_data, count, existance)
    return Response(app.j_encoder.encode(msg), status=stat, mimetype='application/json')


@api.route('/mno-first-page', methods=['GET'])  # from MNO's Portal to get MSISDN list for IMSIs (when page loading)
def get_pair():
    mno = request.args.get('mno')
    st = request.args.get('start')
    lt = request.args.get('limit')
    if not mno:
        data = {
            "Error": _("operator's name is missing")
        }
        return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')

    if not st:
        data = {
            "Error": _("start is missing")
        }
        return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')

    if not lt:
        data = {
            "Error": _("limit is missing")
        }
        return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')

    msg, stat = fetch_msisdns(mno, st, lt)
    return Response(app.j_encoder.encode(msg), status=stat, mimetype='application/json')


@api.route('/mno-bulk-download', methods=['GET'])
def bulk_downloads():
    mno = request.args.get('mno')
    cmplt_path = bulk_msisdns(mno)
    if cmplt_path == "wrong mno":
        data = {
                "Error": _("Improper Operator-Name provided")
               }
        return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')
    elif cmplt_path == "No File found":
        data = {
                "Error": _("No File found")
               }
        return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')
    else:
        response = make_response(send_file(cmplt_path, as_attachment=True))
        response.headers['Cache-Control'] = 'no-store'
        return response
            #return send_from_directory(directory=complete_path, filename=file_name)
            # in this case we need two parameters, directory and file name separately


@api.route('/mno-single-upload', methods=['PUT'])
def sngl_uploads():
    req_data = request.get_json()
    mno = req_data.get('mno')
    imsi = req_data.get('IMSI')

    if 'MSISDN' in req_data:
        msisdn = req_data.get('MSISDN')
        if 'CC' not in msisdn:
            data = {"Error": _("Country-Code is missing")}
            return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')
        if 'SN' not in msisdn:
            data = {"Error": _("Subscriber-Number is missing")}
            return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')
    else:
        data = {
            "Error": _("MSISDN is missing")
        }
        return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')

    if not mno:
        data = {
            "Error": _("operator's name is missing")
        }
        return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')

    if not imsi:
        data = {
            "Error": _("IMSI is missing")
        }
        return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')

    msg, stat = sngl_imsi(mno, msisdn, imsi)
    return Response(app.j_encoder.encode(msg), status=stat, mimetype='application/json')


@api.route('/mno-bulk-upload', methods=['POST'])
def bulk_uploads():
    msg, stat = BulkUpload.bulk_imsis()
    return Response(app.j_encoder.encode(msg), status=stat, mimetype='application/json')


@api.route('/mno-error-file', methods=['GET'])
def error_file():
    url = request.args.get('url')
    if not url:
        data = {
            "Error": _("URL is missing")
        }
        return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')

    file_path = error_url(url)

    if file_path == "no file found":
        data = {
                "Error": _("File not found")
               }
        return Response(app.j_encoder.encode(data), status=422, mimetype='application/json')
    else:
        return send_file(file_path, as_attachment=True)
