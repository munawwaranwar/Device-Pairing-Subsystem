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
from .assets.error_handlers import *
from flask_restful import Api
from app import app
from .resources.device_registration import DeviceRegistration
from .resources.first_pair import FirstPair
from .resources.additional_pairs import AdditionalPairs
from .resources.additional_pairs_confirm import AdditionalPairsConfirmation
from .resources.rel_single_pair import ReleaseSinglePair
from .resources.rel_all_pairs import ReleaseAllPairs
from .resources.sim_change import SimChange
from .resources.verify_paircode import VerifyPairCode
from .resources.find_pairs import FindPairs
from .resources.device_search import DeviceSearch
from .resources.mno_home_page import MnoHomePage
from .resources.single_imsi_upload import SingleImsiUpload
from .resources.bulk_msisdn_download import BulkMsisdnDownload
from .resources.bulk_imsi_upload import BulkImsiUpload
from .resources.download_error_file import DownloadErrorFile

api = Api(app, prefix='/api/v1')

api.add_resource(FirstPair, '/first-pair')
api.add_resource(DeviceRegistration, '/device-reg')
api.add_resource(AdditionalPairs, '/secondary-pairs')
api.add_resource(AdditionalPairsConfirmation, '/secondary-confirm')
api.add_resource(ReleaseSinglePair, '/rel-single-pair')
api.add_resource(ReleaseAllPairs, '/rel-all-pairs')
api.add_resource(SimChange, '/sim-chg')
api.add_resource(VerifyPairCode, '/verify-paircode')
api.add_resource(FindPairs, '/find-pairs')
api.add_resource(DeviceSearch, '/device-search')
api.add_resource(MnoHomePage, '/mno-home-page')
api.add_resource(SingleImsiUpload, '/single-imsi-upload')
api.add_resource(BulkMsisdnDownload, '/bulk-msisdn-download')
api.add_resource(BulkImsiUpload, '/bulk-imsi-upload')
api.add_resource(DownloadErrorFile, '/download-error-file')
