#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

import os
import imp
from multiprocessing import Process
import signal
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from OpenSSL import SSL
from urllib2 import urlopen

import constant
conf = imp.load_source("conf", os.path.dirname(constant.__file__)+"/service.conf")

from cmd_interface import Init, QProc, User, Source, Package


class Rest_srv(object):

    """
    Rest web service
    """

    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.context = SSL.Context(SSL.SSLv23_METHOD)
        self.context.use_privatekey_file(
            os.path.dirname(constant.__file__)+"/"+conf.RKey)
        self.context.use_certificate_file(
            os.path.dirname(constant.__file__)+"/"+conf.RCert)

    def __del__(self):
        print "STOP REST PROCESS"

    def proc(self):
        self.api.add_resource(Rest_out, '/out')
        self.api.add_resource(Rest_user, '/user')
        self.api.add_resource(Rest_info, '/info')
        self.api.add_resource(Rest_domain, '/domain/<string:domain_id>')
        self.app.run(host=conf.RHost,
                     port=int(conf.RPort),
                     ssl_context=self.context)


class Rest_out(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('prog', type=str)
        self.parser.add_argument('dig', type=int)
        self.parser.add_argument('ver', type=str)
        self.parser.add_argument('fname', type=str)

    def post(self):
        args = self.parser.parse_args()
        if args["prog"] != None and\
           args["dig"] != None and\
           args["ver"] != None and\
           args["fname"] != None:

            _pkg = Package()
            _pkg.name = args["prog"]
            _pkg.dig = args["dig"]
            _pkg.ver = args["ver"]
            _type = _pkg.info(args["fname"])[0]["type"]
            if _type == "log":
                url = "http://"+conf.host+\
                    "/"+args["prog"]+\
                    "/"+constant.arch[args["dig"]]+\
                    "/"+args["ver"].split("/")[-1]+\
                    "/"+args["fname"]
                try:
                    url_link = urlopen(url)
                except:
                    abort(404, message="File not found")
                else:
                    _file = url_link.read()
                    url_link.close()
                    return _file, 201
        else:
            return '',404


class Rest_user(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str)
        self.parser.add_argument('key', type=str)
        self.parser.add_argument('newkey', type=str)
        self.parser.add_argument('jnum', type=int)

    def get(self):
        args = self.parser.parse_args()
        if args["name"] == None:
            abort(404, message="Username doesn't exist")
        else:
            if args["jnum"] == None:
                _jnum = False
            else:
                _jnum = args["jnum"]
            return User(args["name"]).job_info(_jnum)

    def put(self):
        args = self.parser.parse_args()
        _test = False
        if args["name"] != None and args["key"] != None and args["newkey"] == None:
            _test = User(args["name"], args["key"]).usermod()
        elif args["name"] != None and args["key"] != None and args["newkey"] != None:
            _test = User(args["name"], args["key"]).usermod(args["newkey"])
        if _test:
            return '', 201
        else:
            abort(403, message="Useradd or usermod forbinden")


class Rest_info(Resource):

    def __init__(self):
        self.domains = ["src", "pkg", "user"]
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('domain', type=str)
        self.parser.add_argument('detail', type=int)

    def domain2val(self, args):
        if args["domain"] not in self.domains:
            self.domain = "src"
        else:
            self.domain = args['domain']
        if type(args["detail"]) is not int:
            self.detail = 0
        else:
            self.detail = args['detail']

    def get(self):
        args = self.parser.parse_args()
        self.domain2val(args)
        if self.domain == "src":
            return Init(False).sources_info(self.detail)
        if self.domain == "pkg":
            return Init(False).packages_info()
        if self.domain == "user":
            return Init(False).users_info(self.detail)


class Rest_domain(Resource):

    def __init__(self):
        self.domains = ["src", "pkg"]
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str)
        self.parser.add_argument('dig', type=int)
        self.parser.add_argument('ver', type=str)
        self.parser.add_argument('uname', type=str)
        self.parser.add_argument('ukey', type=str)

    def domain2obj(self, domain_id):
        if domain_id not in self.domains:
            abort(404,
                  message="Domain {} doesn't exist".
                  format(domain_id))
        else:
            if domain_id == "src":
                _obj = Source()
            elif domain_id == "pkg":
                _obj = Package()
            else:
                _obj = False
        return _obj

    def auth(self, args):
        _test = False
        if args["uname"] != None and args["ukey"] != None:
            _test = User(args["uname"], args["ukey"]).auth()
        if not _test:
            abort(401, message="Authorization failed")

    def get(self, domain_id):
        _obj = self.domain2obj(domain_id)
        args = self.parser.parse_args()
        _obj.name = args["name"]
        _obj.dig = args["dig"]
        _obj.ver = args["ver"]
        _out = _obj.info()
        return _out

    def delete(self, domain_id):
        _obj = self.domain2obj(domain_id)
        args = self.parser.parse_args()
        self.auth(args)
        _obj.name = args["name"]
        _obj.dig = args["dig"]
        _obj.ver = args["ver"]
        if _obj.remove(args["uname"]):
            return '', 204
        else:
            return '', 400

    def put(self, domain_id):
        _obj = self.domain2obj(domain_id)
        args = self.parser.parse_args()
        self.auth(args)
        _obj.name = args["name"]
        _obj.dig = args["dig"]
        _obj.ver = args["ver"]
        if _obj.create(args["uname"]):
            return '', 201
        else:
            return '', 400


class Proc_all(object):

    """
    Start process list
    """

    def __init__(self, objs):
        self.procs = objs
        for proc in self.procs:
            proc.start()

    def start(self):
        print self.procs
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGQUIT, self.stop)
        for proc in self.procs:
            proc.join()

    def stop(self, *args):
        for proc in self.procs:
            proc.terminate()


def Run(_argv=False):
    Init(1)
    All = Proc_all([
        Process(target=QProc().proc,
                name='QUEUE',
                args=(constant.qetime,)),
        Process(target=Rest_srv().proc,
                name='REST'),
    ])
    All.start()


if __name__ == "__main__":
    Run()
