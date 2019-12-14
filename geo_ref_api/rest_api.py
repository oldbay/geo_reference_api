
from flask import Flask, json, request
from flask_restful import Api, Resource

from .serializer import ApiSerializer
from .auth_processing import AuthProcessing
from . import config

import logging
import logging.config
logging.config.dictConfig(config.Logging)
logger = logging.getLogger("rest_api")


########################################################################
class RestApi(object):
    """"""

    api_serial = ApiSerializer()
    auth_proc = AuthProcessing()
    app = Flask(__name__)
    api = Api(app)
    
    options_opt = {
        "OPTIONS": {
            "filter":{
                "api_user": str.__name__,
                "api_group": str.__name__,
            }
        }
    }
    options_def = {
        "auth": {
            "GET": auth_proc.auth_args, 
            "OPTIONS": {},
        },
        "user_info": {
            "GET": {}, 
            "OPTIONS": {},
        },
        "struct_info": {
            "GET": {}, 
            "OPTIONS": {},
        },
    }

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        def_res_dict = {
            'auth': {
                'get': self.auth_http_get,
                'options': self.def_http_options,
            },
            'user_info': {
                'get': self.user_info_http_get,
                'options': self.def_http_options,
            },
            'struct_info': {
                'get': self.struct_info_http_get,
                'options': self.def_http_options,
            },
        }
        for api_key in list(def_res_dict.keys()):
            self.api.add_resource(
                type(
                    '{}'.format(api_key),
                    (Resource,),
                    def_res_dict[api_key]
                ),
                '/{}'.format(api_key)
            )

        api_cont_dict = self.api_serial.get_api_resources_struct()
        for api_key in list(api_cont_dict.keys()):
            res_dict = {
                "options": self.serial_http_options,
            }
            res_dict.update(
                {
                    key.lower():self.serial_http_met
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
                {"options": self.serial_http_options}
            ),
            '/'
        )
        
    def serial_http_met(self):
        ticket = request.headers['ticket']
        ticket_info = self.auth_proc.get_ticket_info(ticket)
        if ticket_info[0] == 200:
            usrname = ticket_info[-1][config.JwtUserKey]
            serial_req = {
                    "met": request.method,
                    "res": request.path.split('/')[-1],
                    "usr": usrname,
                    "req": request.get_json(force=True),
                }
            resp = self.api_serial.serialize(serial_req)
        else:
            resp = ticket_info
        return self.app.response_class(
            response=json.dumps(resp[-1]),
            status=resp[0],
            mimetype='application/json'
        )
    
    def serial_http_options(self):
        res = request.path.split('/')[-1]
        req = request.get_json(force=True)
        if 'filter' in req.keys():
            username = req['filter'].get('api_user', None)
            groupname = req['filter'].get('api_group', None)
        else:
            username = None
            groupname = None
        api_cont_dict = self.api_serial.get_api_resources_struct(
            username=username,
            groupname=groupname
        )
        if not res:
            res_cont_dict = {}
            res_cont_dict.update(self.options_opt)
            res_cont_dict.update(self.options_def)
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
    
    def def_http_options(self):
        res = request.path.split('/')[-1]
        return self.app.response_class(
            response=json.dumps(self.options_def[res]),
            status=200,
            mimetype='application/json'
        )

    def auth_http_get(self):
        req = request.get_json(force=True)
        username = req.get('username', None)
        if not username:
            return self.app.response_class(
                response=json.dumps("{error: Key 'username' not found in method 'auth'}"),
                status=400,
                mimetype='application/json'
            )
        else:
            del(req['username'])
            resp = self.auth_proc.get_auth(username, **req)
            return self.app.response_class(
                response=json.dumps(resp[-1]),
                status=resp[0],
                mimetype='application/json'
            )

    def user_info_http_get(self):
        ticket = request.headers['ticket']
        ticket_info = self.auth_proc.get_ticket_info(ticket)
        return self.app.response_class(
            response=json.dumps(ticket_info[-1]),
            status=ticket_info[0],
            mimetype='application/json'
        )

    def struct_info_http_get(self):
        return self.app.response_class(
            response=json.dumps(self.api_serial.get_api_modules_struct()),
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