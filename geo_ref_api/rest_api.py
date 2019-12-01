
from flask import Flask, json, request
from flask_restful import Api, Resource
import jwt

from .serializer import ApiSerializer 
from . import config


########################################################################
class RestApi(object):
    """"""

    user_key = 'username'
    secret_key = config.AuthSecretKey
    api_serial = ApiSerializer()
    app = Flask(__name__)
    api = Api(app)
    
    options_opt = {
        "OPTIONS": {
            "filter":{
                "api_user": str.__name__,
            }
        }
    }

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        api_cont_dict = self.api_serial.get_api_resources_struct()
        
        for api_key in list(api_cont_dict.keys()):
            res_dict = {
                "options": self.http_options,
            }
            res_dict.update(
                {
                    key.lower():self.http_met
                    for key
                    in api_cont_dict[api_key]
                }
            )
            self.api.add_resource(
                type(
                    '{}'.format(api_key),
                    (Resource,),
                    res_dict
                ),
                '/{}'.format(api_key)
            )
        self.api.add_resource(
            type(
                'root',
                (Resource,),
                {"options": self.http_options}
            ),
            '/'
        )
    def http_met(self):
        ticket = request.headers['ticket']
        usrname = jwt.decode(
            ticket,
            self.secret_key,
            algorithm='HS256'
            )[self.user_key]
        serial_req = {
                "met": request.method,
                "res": request.path.split('/')[-1],
                "usr": usrname,
                "req": request.get_json(force=True),
            }
        serial_resp = self.api_serial.serialize(serial_req)
        return self.app.response_class(
            response=json.dumps(serial_resp[-1]),
            status=serial_resp[0],
            mimetype='application/json'
        )
    
    def http_options(self):
        res = request.path.split('/')[-1]
        req = request.get_json(force=True)
        if 'filter' in req.keys():
            username = req['filter'].get('api_user', None)
        else:
            username = None
        api_cont_dict = self.api_serial.get_api_resources_struct(username=username)
        if not res:
            res_cont_dict = {}
            res_cont_dict.update(self.options_opt)
            for key in list(api_cont_dict.keys()):
                res_cont_dict[key] = api_cont_dict[key]
                res_cont_dict[key].update(self.options_opt)
        else:
            res_cont_dict = api_cont_dict.get(res, {})
            res_cont_dict.update(self.options_opt)
        return self.app.response_class(
            response=json.dumps(res_cont_dict),
            status=200,
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