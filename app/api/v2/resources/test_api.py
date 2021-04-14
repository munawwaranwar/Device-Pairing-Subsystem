from flask import request
from flask_restful import Resource
from flask_apispec import use_kwargs

class TestApi(Resource):

    def __init__(self):
        self._msg = request.args



    # @staticmethod
    # @use_kwargs( locations=['querystring'])
    def get(self):
        return self._msg['msg']
