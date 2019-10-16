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

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import yaml
import json
import sys
from flask_cors import CORS
from flask import Response
from flask_babel import Babel
from app.api.v1.common.lazy_text_encoder import JSON_Encoder


app = Flask(__name__)
CORS(app)
app.j_encoder = JSON_Encoder()
babel = Babel(app)


try:
    with open('config.yml', 'r') as yaml_file:
        global_config = yaml.safe_load(yaml_file)
except Exception as e:  # pragma: no cover
    app.logger.error('Exception encountered during loading the config file')
    app.logger.exception(e)
    sys.exit(1)
# global_config = yaml.safe_load(open("config.yml"))

conf = global_config['global']


app.config['SQLALCHEMY_DATABASE_URI'] = '''postgresql://{}:{}@{}/{}'''.format(conf['dbusername'], conf['dbpassword'],
                                                                              conf['dbhost'], conf['dbname'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = int(conf['pool_size'])
app.config['SQLALCHEMY_POOL_RECYCLE'] = int(conf['pool_recycle'])
app.config['SQLALCHEMY_MAX_OVERFLOW'] = int(conf['overflow_size'])
app.config['SQLALCHEMY_POOL_TIMEOUT'] = int(conf['pool_timeout'])
app.config['DPS_DOWNLOADS'] = conf['Download_Path']
app.config['DPS_UPLOADS'] = conf['Upload_Path']
app.config['BABEL_DEFAULT_LOCALE'] = conf['supported_languages']['default_language']
app.config['SUPPORTED_LANGUAGES'] = conf['supported_languages']

db = SQLAlchemy()
db.init_app(app)


from app.api.v1.views import api
app.register_blueprint(api, url_prefix='/api/v1')


@app.errorhandler(400)
def handle_400(err):
    return Response(json.dumps({"Error": "Bad Request"}), status=400, mimetype='application/json')


@app.errorhandler(405)
def handle_405(err):
    return Response(json.dumps({"Error": "Method not Allowed"}), status=405, mimetype='application/json')


@app.errorhandler(404)
def handle_405(err):
    return Response(json.dumps({"Error": "Not Found"}), status=404, mimetype='application/json')


from app.api.v1.common.database import connect
pg_connt = connect()


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['SUPPORTED_LANGUAGES'])
