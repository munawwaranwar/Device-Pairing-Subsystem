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

from app import db, conf
from flask_babel import _
from ..models.imeis import Imei
from ..models.owner import Owner
from flask_restful import Resource
from flask_apispec import use_kwargs
from ..models.devices import Devices
from ..models.pairing_codes import Pairing_Codes
from app.api.common.jasmin_apis import JasminAPIs
from app.api.common.generate_paircode import gen_paircode
from ..schema.input_schema import DeviceRegistrationSchema
from app.api.assets.response import STATUS_CODES, MIME_TYPES
from app.api.assets.error_handlers import custom_paircode_response


# noinspection PyBroadException,PyUnusedLocal,PyUnresolvedReferences
class DeviceRegistration(Resource):
    """Flask resource for Device Registration."""

    @staticmethod
    @use_kwargs(DeviceRegistrationSchema().fields_dict, locations=['json'])
    def post(**kwargs):
        """method to create device registration request."""
        try:

            chk_owner_id = Owner.query.filter(Owner.contact == '{}'.format(kwargs['contact_no'])).first()
            if not chk_owner_id:
                add_owner = Owner(contact=kwargs['contact_no'])
                db.session.add(add_owner)
                db.session.flush()
                owner_id = add_owner.id
            else:
                owner_id = chk_owner_id.id
            add_device = Devices(model=kwargs['model'],
                                 brand=kwargs['brand'],
                                 serial_no=kwargs['serial_no'].strip(),
                                 mac=kwargs['mac'].strip(),
                                 rat=kwargs['rat'].strip(','),
                                 owner_id=owner_id)

            db.session.add(add_device)
            db.session.flush()
            for i in kwargs['imei']:
                add_imei = Imei(imei=i,
                                device_id=add_device.id)

                db.session.add(add_imei)
                db.session.flush()
            pair_code = gen_paircode()
            add_paircode = Pairing_Codes(pair_code=pair_code,
                                         is_active=True,
                                         device_id=add_device.id)
            db.session.add(add_paircode)
            db.session.flush()
            db.session.commit()

            """ ****************** Kannel-Block replaced with Jasmin ******************
            message = _("Device has been registered with Authority. Your Activation Pair-Code is %(pc)s",
                        pc=pair_code)
            chg_msisdn = '0' + kwargs['contact_no'][2:]

            payload = {'username': conf['kannel_username'], 'password': conf['kannel_password'],
                       'smsc': conf['kannel_smsc'], 'from': conf['kannel_shortcode'], 'to': chg_msisdn,
                       'text': message}

            requests.get(conf['kannel_sms'], params=payload)
            """

            message = _("Device has been registered with Authority. Your Activation Pair-Code is %(pc)s",
                        pc=pair_code)
            response = JasminAPIs.jasmin_sms(kwargs['contact_no'], conf['kannel_shortcode'], message)

            return custom_paircode_response(_("Device's information has been successfully loaded"),
                                            pair_code, status=STATUS_CODES.get('OK'),
                                            mimetype=MIME_TYPES.get('JSON'))

        except Exception as e:
            db.session.rollback()       # pragma: no cover

        finally:
            db.session.close()
