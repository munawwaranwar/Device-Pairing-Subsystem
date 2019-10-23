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

import re
from app import conf
from flask_babel import _
from marshmallow import ValidationError


class Validations:
    """Class for input validations."""

    @staticmethod
    def validate_paircode(paircode):
        """Validates Pair-Code format."""
        match_paircode = re.match(conf['validation_regex']['paircode'], paircode)
        if match_paircode is None:
            raise ValidationError(_('Pair-Code format is not correct'))

    @staticmethod
    def validate_msisdn(msisdn):
        """Validates MSISDN format."""
        match_msisdn = re.match(conf['validation_regex']['msisdn'], msisdn)
        if match_msisdn is None:
            raise ValidationError(_('MSISDN format is not correct'))

    @staticmethod
    def validate_model(model):
        """Validates Model Name."""
        match_model = re.match(conf['regex'][conf['supported_languages']['default_language']]['model_name'], model)
        if match_model is None:
            raise ValidationError(_('Model name is not correct'))

    @staticmethod
    def validate_brand(brand):
        """Validates Brand Name."""
        match_brand = re.match(conf['regex'][conf['supported_languages']['default_language']]['model_name'], brand)
        if match_brand is None:
            raise ValidationError(_('Brand name is not correct'))

    @staticmethod
    def validate_serial_no(serial_no):
        """Validates Serial Number."""
        match_serial = re.match(conf['validation_regex']['serial_no'], serial_no)
        if match_serial is None:
            raise ValidationError(_('Serial Number is not correct'))

    @staticmethod
    def validate_mac(mac):
        """Validates MAC Name."""
        if mac is not "" and not mac and mac is not None:
            match_mac = re.match(conf['validation_regex']['mac'], mac)
            if match_mac is None:
                raise ValidationError(_('MAC format is not correct'))

    @staticmethod
    def validate_rat(rat):
        """Validates RAT Name."""
        match_rat = re.match(conf['validation_regex']['rat'], rat)
        if match_rat is None:
            raise ValidationError(_('RAT is not correct'))

    @staticmethod
    def validate_operator(mno):
        """Validates Operator Name."""
        if mno not in conf['MNO_Names'] or (re.match(conf['validation_regex']['mno'], mno) is None):
            raise ValidationError(_('Operator name is not correct'))

    @staticmethod
    def validate_single_imei(imei):
        """Validates RAT Name."""
        match_imei = re.match(conf['validation_regex']['imei'], imei)
        if match_imei is None:
            raise ValidationError(_('IMEI is not correct'))

    @staticmethod
    def validate_imeis(imeis):
        """Validates IMEI Format."""
        if len(imeis) == 0:
            raise ValidationError(_('At least one IMEI is required'))
        elif len(imeis) > 5:
            raise ValidationError(_("Only %(var1)d IMEIs per device are allowed", var1=conf['imeis_per_device']))
        for imei in imeis:
            match_imei = re.match(conf['validation_regex']['imei'], imei)
            if match_imei is None:
                raise ValidationError(_('IMEI is not correct'))

    @staticmethod
    def validate_confirm(confrm):
        """Validates confirmation strings."""

        if confrm not in ['YES', 'yes', 'Yes', 'NO', 'no', 'No']:
            raise ValidationError(_('Confirmation String is not correct'))

    @staticmethod
    def validate_start_limit(param):
        """ Validates start and limit parameters for pagination"""

        match_param = re.fullmatch(conf['validation_regex']['start_limit'], param)
        if match_param is None:
            raise ValidationError(_('Start or Limit values are not correct'))

    @staticmethod
    def validate_imsi(imsi):
        """ Validates IMSI format"""

        match_imsi = re.fullmatch(conf['validation_regex']['imsi'], imsi)
        if match_imsi is None:
            raise ValidationError(_('IMSI is not correct'))
