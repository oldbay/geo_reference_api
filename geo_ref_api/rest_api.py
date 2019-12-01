
from flask import Flask, json, request
from flask_restful import Api, Resource
import jwt

from .serializer import ApiSerializer 
from . import config

#api_serial = ApiSerializer()

########################################################################
class RestApi:
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        self.user_key = 'username'
        self.secret_key = config.AuthSecretKey
        self.api_serial = ApiSerializer()
        self.app = Flask(__name__)
        self.api = Api(self.app)
        
        api_cont_dict = self.api_serial.get_api_resources_struct()
        
        for api_key in list(api_cont_dict.keys()):
            res_dict = {
                'user_key': self.user_key,
                'secret_key': self.secret_key,
                'app': self.app,
            }
            res_dict.update(
                {
                    key.lower():self.http_met
                    for key
                    in api_cont_dict[api_key]
                }
            )
            #print (res_dict)
            self.api.add_resource(
                type(
                    '{}'.format(api_key),
                    (Resource,),
                    res_dict
                ),
                '/{}'.format(api_key)
            )
    @staticmethod
    def http_met(self):
        ticket = request.headers['ticket']
        usrname = jwt.decode(
            ticket,
            self.secret_key,
            algorithm='HS256'
            )[self.user_key]
        serial_req = {
                "met": request.method,
                "res": request.path[1:],
                "usr": usrname,
                "req": request.get_json(force=True),
            }
        api_serial = ApiSerializer()
        serial_resp = api_serial.serialize(serial_req)
        return self.app.response_class(
            response=json.dumps(serial_resp[-1]),
            status=serial_resp[0],
            mimetype='application/json'
        )
    
    def run_test_server(self, **kwargs):
        """
        host='0.0.0.0'
        port='5444'
        debug=True
        """
        #for r in self.app.url_map.iter_rules():
            #print (r)
        self.app.run(**kwargs)

