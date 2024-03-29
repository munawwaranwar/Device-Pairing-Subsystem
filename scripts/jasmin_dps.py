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


# jasmin_dps.py

import json
import requests
from time import strftime
from flask import Flask, request

app = Flask(__name__)

ERROR_MSG = "Incorrect Message Format. Please send HELP to 8787"
ERROR_SPACES = "Incorrect Message Format. Please check the White spaces in the SMS."
ERROR_TECH = "SMS Format is incorrect"
DPS_URL = "http://192.168.100.52/api/v1/"
ERROR_MSISDN = "Sender Number is not correct, please specify number in correct format"


# noinspection PyUnusedLocal,HttpUrlsUsage
@app.route('/dps-jasmin', methods=['POST'])
def main():

    if request.method == 'POST':

        """
        SMS content/text must contain keywords specific to different APIs of DPS. That includes keywords of both SMS &
        USSD. Below dictionary contains all the allowed keywords to be matched later in code.
        """

        keywords = {"first_pair": ['FIRST', 'first', 'First'],
                    "add_pair": ['ADD', 'add', 'Add'],
                    "confirm_pair": ['YES', 'yes', 'Yes', 'NO', 'no', 'No'],
                    "release_pair": ['RELEASE', 'release', 'Release'],
                    "sim_change": ['SIM', 'sim', 'Sim'],
                    "find_pairs": ['FIND', 'find', 'Find'],
                    "verify_pair": ['VERIFY', 'verify', 'Verify'],
                    "dps_ussd": ["USSD", "ussd"],
                    }

        # Extracting parameters from API
        # kwargs = request.data.decode()
        kwargs = request.values
        # kwargs = request.get_json(force=True)

        # MSISDN Validation
        sender_no = msisdn_validation(kwargs['from'])

        # Fetching receiver's number or Shortcode
        receiver = kwargs['to']

        # Fetching Mobile Operator's name
        operator = kwargs['origin-connector']

        if sender_no == "wrong sender number":
            dns_sms(kwargs['from'], receiver, ERROR_SPACES, operator)
            return ERROR_MSISDN, 422

        # striping white spaces from start and end
        sms_text = kwargs['content'].strip()
        white_spaces = sms_text.count(' ')   # count of total white spaces within SMS text

        if white_spaces == 1:
            key1, key2 = sms_text.split(' ', 1)

            if key1 in keywords['first_pair']:
                fp_response = first_pair(key2, sender_no, operator)

                # Calling Jasmin SMS Rest API to send First-Pair API's response back to sender via SMS
                # jasmin_sms(sender_no, kwargs['to'], fp_response)

                # Calling DNS SMS-API to send First-Pair API's response back to sender via SMS
                dns_sms(sender_no, receiver, fp_response, operator)

                return fp_response

            elif key1 in keywords['add_pair']:
                ap_response = add_pairs(sender_no, key2)

                # Calling Jasmin SMS Rest API to send Add-Pair API's response back to sender via SMS
                # jasmin_sms(sender_no, receiver, ap_response)

                # Calling DNS SMS-API to send First-Pair API's response back to sender via SMS
                dns_sms(sender_no, receiver, ap_response, operator)

                return ap_response

            elif key1 in keywords['confirm_pair']:
                cp_response = confirm_pair(key2, sender_no, operator, key1)

                # Calling Jasmin SMS Rest API to send Confirm-Pair API's response back to sender via SMS
                # jasmin_sms(sender_no, kwargs['to'], cp_response)

                # Calling DNS SMS-API to send First-Pair API's response back to sender via SMS
                dns_sms(sender_no, receiver, cp_response, operator)

                return cp_response

            elif key1 in keywords['release_pair']:
                rp_response = release_pair(sender_no, key2)

                # Calling Jasmin SMS Rest API to send Release-Pair APIs' response back to sender via SMS
                # jasmin_sms(sender_no, kwargs['to'], rp_response)

                # Calling DNS SMS-API to send First-Pair API's response back to sender via SMS
                dns_sms(sender_no, receiver, rp_response, operator)

                return rp_response

            elif key1 in keywords['sim_change']:
                sc_response = sim_change(sender_no, operator, key2)

                # Calling Jasmin SMS Rest API to send Release-Pair APIs' response back to sender via SMS
                # jasmin_sms(sender_no, kwargs['to'], sc_response)

                # Calling DNS SMS-API to send First-Pair API's response back to sender via SMS
                dns_sms(sender_no, receiver, sc_response, operator)

                return sc_response

            elif key1 in keywords['find_pairs']:
                fip_response = find_pairs(sender_no, key2)

                # Calling Jasmin SMS Rest API to send Release-Pair APIs' response back to sender via SMS
                # jasmin_sms(sender_no, kwargs['to'], fip_response)

                # Calling DNS SMS-API to send First-Pair API's response back to sender via SMS
                dns_sms(sender_no, receiver, fip_response, operator)

                return fip_response

            else:
                dns_sms(sender_no, receiver, ERROR_MSG, operator)
                return ERROR_MSG, 422

        # To detect SMS type of "Verify Pairs"
        elif white_spaces == 2:
            key, pair_code, imei = sms_text.split(' ', 2)

            if key in keywords['verify_pair']:
                vp_response = verify_paircode(pair_code, imei)

                # Calling Jasmin SMS Rest API to send Release-Pair APIs' response back to sender via SMS
                # jasmin_sms(sender_no, kwargs['to'], vp_response)

                # Calling DNS SMS-API to send First-Pair API's response back to sender via SMS
                dns_sms(sender_no, receiver, vp_response, operator)

                return vp_response
            else:
                dns_sms(sender_no, receiver, ERROR_MSG, operator)
                return ERROR_MSG, 422

        # To detect USSD String which must be without spaces and comma separated
        elif white_spaces == 0:

            technology = sms_text.split(',')[0]

            if technology in keywords['dps_ussd']:

                dps_case = case_search(int(sms_text.split(',')[1]))
                ussd_time = strftime("%Y-%m-%d %H:%M:%S")

                URL = DPS_URL + "dps-ussd"
                headers = {'content-type': 'application/json'}
                payload = {"sender_no": sender_no, "receiver": receiver, "time": ussd_time, "operator": operator,
                           "case": dps_case, "technology": technology, "msg_text": sms_text}

                response = requests.get(url=URL,
                                        params=payload,
                                        headers=headers)

                # Calling Jasmin SMS Rest API to send Release-Pair APIs' response back to sender via SMS
                # jasmin_sms(sender_no, receiver, response.text)

                # Calling DNS SMS-API to send DPS API's response back to sender
                dns_sms(sender_no, receiver, response.text, operator)

                return response.text
            else:
                jasmin_sms(sender_no, receiver, ERROR_TECH)
                dns_sms(sender_no, receiver, ERROR_TECH, operator)
                return ERROR_TECH, 422
        else:
            dns_sms(sender_no, receiver, ERROR_SPACES, operator)
            return ERROR_SPACES, 422


# noinspection HttpUrlsUsage
def first_pair(paircode, sender_no, operator):
    """Function to call First-Pair API of DPS."""

    if len(paircode) == 8:

        URL = DPS_URL + "first-pair"
        headers = {'content-type': 'application/json'}
        data = {"sender_no": sender_no, "operator": operator, "pair_code": paircode}
        response = requests.post(url=URL,
                                 data=json.dumps(data),
                                 headers=headers)
        result = response.json()

        if isinstance(result, dict):
            return result['message'][list(result['message'].keys())[0]][0]
        else:
            return response.text
    else:
        return ERROR_MSG


# noinspection HttpUrlsUsage
def add_pairs(primary_msisdn, secondary_msisdn):
    """Function to call Add-Pairs API of DPS."""

    if 10 < len(secondary_msisdn) < 16:

        if secondary_msisdn.isdigit():

            msisdn = msisdn_validation(secondary_msisdn)

            URL = DPS_URL + "secondary-pairs"
            headers = {'content-type': 'application/json'}
            data = {"primary_msisdn": primary_msisdn, "secondary_msisdn": msisdn}
            response = requests.post(url=URL,
                                     data=json.dumps(data),
                                     headers=headers)
            result = response.json()

            if isinstance(result, dict):
                return result['message'][list(result['message'].keys())[0]][0]
            else:
                return response.text
        else:
            return "Secondary Number contains non-digit values, please specify number in correct format"
    else:
        return 'Secondary Number is not correct, please specify number in correct format'


# noinspection HttpUrlsUsage
def confirm_pair(primary_msisdn, secondary_msisdn, operator, confirm):
    """Function to call Confirm-Pair API of DPS."""

    if 10 < len(primary_msisdn) < 16:

        if primary_msisdn.isdigit():

            msisdn = msisdn_validation(primary_msisdn)

            URL = DPS_URL + "secondary-confirm"
            headers = {'content-type': 'application/json'}

            data = {"primary_msisdn": msisdn, "secondary_msisdn": secondary_msisdn,
                    "operator": operator, "confirm": confirm}

            response = requests.post(url=URL,
                                     data=json.dumps(data),
                                     headers=headers)
            result = response.json()

            if isinstance(result, dict):
                return result['message'][list(result['message'].keys())[0]][0]
            else:
                return response.text
        else:
            return "Primary-Number contains non-digit values, please specify number in correct format"
    else:
        return 'Primary-Number is not correct, please specify number in correct format'


# noinspection HttpUrlsUsage
def release_pair(primary_msisdn, secondary_msisdn):
    """Function to call Release-Single & Release-All APIs of DPS."""

    headers = {'content-type': 'application/json'}

    if secondary_msisdn in ["ALL", "all", "All"]:

        data = {"primary_msisdn": primary_msisdn}
        URL = DPS_URL + "rel-all-pairs"

        response = requests.delete(url=URL,
                                   data=json.dumps(data),
                                   headers=headers)

        return response.text
    else:
        if 10 < len(secondary_msisdn) < 16:
            if secondary_msisdn.isdigit():
                msisdn = msisdn_validation(secondary_msisdn)
                data = {"primary_msisdn": primary_msisdn, "secondary_msisdn": msisdn}
                URL = DPS_URL + "rel-single-pair"

                response = requests.delete(url=URL,
                                           data=json.dumps(data),
                                           headers=headers)
                return response.text
            else:
                return "Secondary Number contains non-digit values, please specify number in correct format"
        else:
            return 'Secondary Number is not correct, please specify number in correct format'


# noinspection HttpUrlsUsage
def sim_change(msisdn, operator, key):
    """Function to call Sim-Change APIs of DPS."""

    if key in ['CHANGE', 'change', 'Change']:
        headers = {'content-type': 'application/json'}
        data = {"msisdn": msisdn, "operator": operator}
        URL = DPS_URL + "sim-change"

        response = requests.delete(url=URL,
                                   data=json.dumps(data),
                                   headers=headers)
        return response.text
    else:
        return ERROR_MSG


# noinspection HttpUrlsUsage
def find_pairs(primary_msisdn, key):
    """Function to call Find-Pairs API of DPS."""

    if key in ['PAIRS', 'pairs', 'Pairs']:
        params = {"primary_msisdn": primary_msisdn}
        headers = {'content-type': 'application/json'}
        URL = DPS_URL + "find-pairs"

        response = requests.get(url=URL, headers=headers, data=json.dumps(params))

        result = response.json()
        if isinstance(result, dict):
            return "Primary MSISDN is not correct"
        else:
            result = response.text.replace('[', '')
            result = result.replace(']', '')
            return result
    else:
        return ERROR_MSG


# noinspection HttpUrlsUsage
def verify_paircode(paircode, imei):
    """Function to call Verify-Pairs API of DPS."""

    if len(paircode) == 8:
        if 14 <= len(imei) <= 16:
            params = {"pair_code": paircode, "imei": imei}
            headers = {'content-type': 'application/json'}
            URL = DPS_URL + "verify-paircode"
            # response = requests.get(url=URL, params=params)
            response = requests.request("GET", URL, headers=headers, data=json.dumps(params))

            result = response.json()

            if isinstance(result, dict):
                return result['message']['json']['imei'][0]
            else:
                return response.text
        else:
            return "IMEI length is not correct. Plz specify correct IMEI"
    else:
        return "Pair-Code is not correct. Plz specify correct Pair-Code"


def msisdn_validation(sender_no):
    """Function to modify Sender's MSISDN to DPS accepted format. """

    if sender_no[0:2] == '92':
        return sender_no
    elif sender_no[0:3] == '009':
        return sender_no[2:]
    elif sender_no[0:3] == '+92':
        return sender_no[1:]
    elif sender_no[0:2] == '03':
        return '92' + sender_no[1:]
    elif sender_no[0:3] == '%2B':
        return sender_no[3:]
    else:
        return "wrong sender number"


# noinspection HttpUrlsUsage
def jasmin_sms(sender, receiver, sms_content):
    """Function to call Jasmin Single-SMS Rest API."""

    url = "http://192.168.100.40:8080/secure/send"
    params = {"to": sender, "from": receiver, "coding": 0, "content": sms_content}
    headers = {'content-type': 'application/json', 'Authorization': "Basic em9uZzoxMjM="}
    response = requests.post(url=url, data=json.dumps(params), headers=headers)
    print(response.status_code, response.text)


# noinspection HttpUrlsUsage
def dns_sms(*args):
    """Function to call DNS SMS-API."""

    # url = "http://192.168.100.40:8080/secure/send"
    URL = "http://192.168.100.53/sms/"

    data = {}
    if len(args) == 3:
        data = {
            "sms_to": args[0],
            "sms_from": args[1],
            "sms_content": args[2],
            "subsystem": "DPS",
        }
    elif len(args) == 4:
        data = {
            "sms_to": args[0],
            "sms_from": args[1],
            "sms_content": args[2],
            "operator": args[3],
            "subsystem": "DPS",
        }

    headers = {'content-type': 'application/json'}
    response = requests.post(url=URL, data=json.dumps(data), headers=headers)
    print(response.status_code, response.text)


def case_search(menu_code):
    """Function to decide the DPS case from USSD content."""

    case = ""
    if menu_code == 11: case = "first_pair"
    elif menu_code == 21: case = "additional_pair"
    elif menu_code == 31: case = "del_single_pair"
    elif menu_code == 4: case = "del_all_pairs"
    elif menu_code == 5: case = "sim_change"
    elif menu_code == 611: case = "verify_pair"
    elif menu_code == 7: case = "find_pair"

    return case


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)
