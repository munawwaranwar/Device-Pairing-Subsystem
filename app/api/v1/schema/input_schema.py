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

from marshmallow import Schema, fields
from app.api.common.validations import Validations


class FirstPairSchema(Schema):
    """Marshmallow schema for first-pair creation request."""

    class Meta:
        strict = True
    pair_code = fields.String(required=True, validate=Validations.validate_paircode)
    sender_no = fields.String(required=True, validate=Validations.validate_msisdn)
    operator = fields.String(required=True, validate=Validations.validate_operator)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class AdditionalPairSchema(Schema):
    """Marshmallow schema for Secondary-Pairs creation request."""

    class Meta:
        strict = True
    secondary_msisdn = fields.String(required=True, validate=Validations.validate_msisdn)
    primary_msisdn = fields.String(required=True, validate=Validations.validate_msisdn)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class DeviceRegistrationSchema(Schema):
    """Marshmallow schema for Device Registration request."""

    class Meta:
        strict = True
    contact_no = fields.String(required=True, validate=Validations.validate_msisdn)
    model = fields.String(required=True, validate=Validations.validate_model)
    brand = fields.String(required=True, validate=Validations.validate_brand)
    serial_no = fields.String(required=True, validate=Validations.validate_serial_no)
    mac = fields.String(required=False, missing="00:00:00:00", validate=Validations.validate_mac)
    rat = fields.String(required=True, validate=Validations.validate_rat)
    imei = fields.List(fields.String(), required=True, validate=Validations.validate_imeis)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class AddPairConfirmSchema(Schema):
    """Marshmallow schema for Secondary-Pairs confirmation request."""

    class Meta:
        strict = True
    secondary_msisdn = fields.String(required=True, validate=Validations.validate_msisdn)
    primary_msisdn = fields.String(required=True, validate=Validations.validate_msisdn)
    operator = fields.String(required=True, validate=Validations.validate_operator)
    confirm = fields.String(required=True, validate=Validations.validate_confirm)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class RelAllPairsSchema(Schema):
    """Marshmallow schema for all-pairs release request."""

    class Meta:
        strict = True
    primary_msisdn = fields.String(required=True, validate=Validations.validate_msisdn)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class SimChangeSchema(Schema):
    """Marshmallow schema for SIM Change request."""

    class Meta:
        strict = True
    msisdn = fields.String(required=True, validate=Validations.validate_msisdn)
    operator = fields.String(required=True, validate=Validations.validate_operator)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class VfyPaircodeSchema(Schema):
    """Marshmallow schema for PairCode verification request."""

    class Meta:
        strict = True
    pair_code = fields.String(required=True, validate=Validations.validate_paircode)
    imei = fields.String(required=True, validate=Validations.validate_single_imei)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class DeviceSearchSchema(Schema):
    """Marshmallow schema for device searching request."""

    class Meta:
        strict = True
    start = fields.String(required=True, validate=Validations.validate_start_limit)
    limit = fields.String(required=True, validate=Validations.validate_start_limit)
    contact = fields.String(required=False, validate=Validations.validate_msisdn)
    mac = fields.String(required=False)
    imei = fields.String(required=False)
    serial_no = fields.String(required=False, validate=Validations.validate_serial_no)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class MnoHomePageSchema(Schema):
    """Marshmallow schema for MNO's Home page request."""

    class Meta:
        strict = True
    start = fields.String(required=True, validate=Validations.validate_start_limit)
    limit = fields.String(required=True, validate=Validations.validate_start_limit)
    operator = fields.String(required=True, validate=Validations.validate_operator)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class SingleImsiSchema(Schema):
    """Marshmallow schema for Single IMSI upload request."""

    class Meta:
        strict = True
    msisdn = fields.String(required=True, validate=Validations.validate_msisdn)
    operator = fields.String(required=True, validate=Validations.validate_operator)
    imsi = fields.String(required=True, validate=Validations.validate_imsi)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class BulkDownloadSchema(Schema):
    """Marshmallow schema for Bulk MSISDN download request."""

    class Meta:
        strict = True
    operator = fields.String(required=True, validate=Validations.validate_operator)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class BulkUploadSchema(Schema):
    """Marshmallow schema for Bulk MSISDN download request."""

    class Meta:
        strict = True
    file = fields.String(required=False)
    operator = fields.String(required=True, validate=Validations.validate_operator)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class ErrorFileSchema(Schema):
    """Marshmallow schema for downloading error files."""

    class Meta:
        strict = True
    url = fields.String(required=True)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields
