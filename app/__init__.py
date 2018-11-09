"""
DPS notification resource package.
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

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import yaml
import json
import sys
from flask_cors import CORS
from flask import Response

app = Flask(__name__)
CORS(app)


try:
    with open('config.yml', 'r') as yaml_file:
        global_config = yaml.load(yaml_file)
except Exception as e:
    app.logger.error('Exception encountered during loading the config file')
    app.logger.exception(e)
    sys.exit(1)
# global_config = yaml.load(open("config.yml"))

conf = global_config['global']


app.config['SQLALCHEMY_DATABASE_URI']= '''postgresql://{}:{}@{}/{}'''.format(conf['dbusername'],conf['dbpassword'],
                                                                             conf['dbhost'],conf['dbname'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = int(conf['pool_size'])
app.config['SQLALCHEMY_POOL_RECYCLE'] = int(conf['pool_recycle'])
app.config['SQLALCHEMY_MAX_OVERFLOW'] = int(conf['overflow_size'])
app.config['SQLALCHEMY_POOL_TIMEOUT'] = int(conf['pool_timeout'])

db = SQLAlchemy()
db.init_app(app)


from app.views import api
app.register_blueprint(api, url_prefix='/api/v1')

@app.errorhandler(400)
def handle_400(err):
    return Response(json.dumps({"Error": "400 Bad Request"}), status=400, mimetype='application/json')

@app.errorhandler(405)
def handle_405(err):
    return Response(json.dumps({"Error": "Method not Allowed"}), status=405, mimetype='application/json')

@app.errorhandler(404)
def handle_405(err):
    return Response(json.dumps({"Error": "404 Not Found"}), status=404, mimetype='application/json')

from app.common.database import connect
pg_connt = connect()