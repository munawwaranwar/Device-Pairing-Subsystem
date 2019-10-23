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

import json
import copy
import pytest
import shutil
from testing.postgresql import Postgresql
from tests._helpers import *
from app.api.v1.common.lazy_text_encoder import JSON_Encoder


@pytest.yield_fixture(scope='session')
def app(tmpdir_factory):
    """Method to create an app for testing."""
    # need to import this late as it might have side effects
    from app import app as app_, db

    # need to save old configurations of the app
    # to restore them later upon tear down

    #app_.j_encoder = JSON_Encoder()
    old_url_map = copy.copy(app_.url_map)
    old_view_functions = copy.copy(app_.view_functions)
    app_.testing = True
    app_.debug = False
    old_config = copy.copy(app_.config)

    # initialize temp database and yield app
    with Postgresql() as postgresql:
        app_.config['SQLALCHEMY_DATABASE_URI'] = postgresql.url()

        temp_download = tmpdir_factory.mktemp('downloads')
        temp_uploads = tmpdir_factory.mktemp('uploads')
        app_.config['DPS_UPLOADS'] = str(temp_uploads)
        app_.config['DPS_DOWNLOADS'] = str(temp_download)

        yield app_

    # restore old configs after successful session
    app_.url_map = old_url_map
    app_.view_functions = old_view_functions
    app_.config = old_config
    shutil.rmtree(str(temp_download))
    shutil.rmtree(str(temp_uploads))
    postgresql.stop()


@pytest.fixture(scope='session')
def flask_app(app):
    """fixture for injecting flask test client into every test."""
    #app.j_encoder = JSON_Encoder()
    yield app.test_client()


@pytest.yield_fixture(scope='session')
def db(app):
    """fixture to inject temp db instance into tests."""
    # need to import this late it might cause problems
    from app import db

    # create and configure database
    db.app = app
    db.create_all()

    create_view(db)
    #create_database(db)
    yield db

    # teardown database
    db.engine.execute('DROP TABLE owner CASCADE')
    db.engine.execute('DROP TABLE devices CASCADE')
    db.engine.execute('DROP TABLE imei CASCADE')
    db.engine.execute('DROP TABLE pairing_codes CASCADE')
    db.drop_all()


@pytest.yield_fixture(scope='session')
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session_ = db.create_scoped_session(options=options)
    db.session = session_

    yield session_

    transaction.rollback()
    connection.close()
    session_.remove()

