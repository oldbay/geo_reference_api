#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

import os
import imp
from datetime import datetime

import constant
conf = imp.load_source("conf", os.path.dirname(constant.__file__)+"/service.conf")

from sqlalchemy.orm import sessionmaker
from model import engine, Que, Queue, User, Job, Prog, Ver, File


class Database(object):

    """
    Connect to database and return a Session object
    """

    def connect(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        return session


class Operation(object):

    """
    Database operations
    query - use qtype=(all,one,first)
    """

    def __init__(self):
        self.__session = Database().connect()

    def __del__(self):
        self.__session.close()

    def que_query(self, _qtype, _qkey=False, _job=False):
        query = self.__session.query(Que)
        query = query.order_by(Que.qtime)
        if _qkey:
            query = query.filter_by(queue_key=u""+_qkey)
        if _job:
            query = query.filter_by(job_num=int(_job))
        if _qtype == "all":
            return query.all()
        elif _qtype == "one":
            return query.one()
        elif _qtype == "first":
            return query.first()

    def queue_query(self, _qtype, _qkey=False):
        query = self.__session.query(Queue)
        if _qkey:
            query = query.filter_by(qkey=u""+_qkey)
        if _qtype == "all":
            return query.all()
        elif _qtype == "one":
            return query.one()
        elif _qtype == "first":
            return query.first()

    def queue_put(self, _qkey, _obj):
        try:
            _query = self.queue_query("one", _qkey)
        except:
            _add_row = Queue()
            _add_row.qkey = u""+_qkey
            self.__session.add(_add_row)
            self.__session.commit()
            _queue_id = self.queue_query("one", _qkey).id
        else:
            _queue_id = _query.id
        add_row = Que()
        add_row.qtime = datetime.now()
        add_row.obj = _obj
        add_row.queue_id = _queue_id
        self.__session.add(add_row)
        self.__session.commit()

    def queue_get(self, _qkey):
        _q = self.que_query("first", _qkey)
        if _q is not None:
            if not _q.stat:
                _obj = _q.obj
                _q.stat = True
                self.__session.commit()
                return _obj
            else:
                return False
        else:
            return False

    def queue_qstart(self, _qkey, _job, _obj):
        _q = self.que_query("first", _qkey)
        try:
            _qjob = self.job_query("one", _job)
        except:
            print "aaa"
            return False
        if _q is not None:
            if _q.stat:
                _q.obj = _obj
                _q.job_id = _qjob.id
                self.__session.commit()
                return True
            else:
                return False
        else:
            return False

    def queue_qend(self, _qkey):
        _q = self.que_query("first", _qkey)
        if _q is not None:
            if _q.stat:
                _obj = _q.obj
                self.__session.delete(_q)
                self.__session.commit()
                _query = self.queue_query("one", _qkey)
                if _query.ques == []:
                    self.__session.delete(_query)
                    self.__session.commit()
                return _obj
            else:
                return False
        else:
            return False

    def queue_del(self, _qkey=False):
        _query = self.que_query("all", _qkey)
        for _q in _query:
            self.__session.delete(_q)
            self.__session.commit()
        _query = self.queue_query("all", _qkey)
        for _q in _query:
            self.__session.delete(_q)
            self.__session.commit()

    def user_query(self, _qtype, _name=False, _key=False):
        query = self.__session.query(User)
        if _name:
            query = query.filter_by(name=u""+_name)
        if _key:
            query = query.filter_by(key=u""+_key)
        if _qtype == "all":
            return query.all()
        elif _qtype == "one":
            return query.one()
        elif _qtype == "first":
            return query.first()

    def user_add(self,
                 _name=constant.init["user"],
                 _key=constant.init["key"]
                 ):
        _query = self.user_query("all", _name)
        if _query == []:
            add_row = User()
            add_row.name = u""+_name
            add_row.key = u""+_key
            self.__session.add(add_row)
            self.__session.commit()

    def user_mod_key(self, _name, _key):
        # test user name
        try:
            _query = self.user_query("one", _name)
        except:
            pass
        else:
            _query.key = u""+_key
            self.__session.commit()

    def user_del(self, _name):
        _query = self.user_query("all", _name)
        for _q in _query:
            # delete jobs of user
            self.job_del(_q.name)
            # delete user
            self.__session.delete(_q)
            self.__session.commit()

    def job_query(self, _qtype, _num=False, _uname=False, _state=False):
        query = self.__session.query(Job)
        if _num:
            query = query.filter_by(num=int(_num))
        if _uname:
            query = query.filter_by(user_nam=u""+_uname)
        if _state:
            query = query.filter_by(const_state=u""+_state)
        if _qtype == "all":
            return query.all()
        elif _qtype == "one":
            return query.one()
        elif _qtype == "first":
            return query.first()

    def job_add(self,
                _num=constant.init["job"],
                _uname=constant.init["user"],
                _state=constant.state["n2s"]["run"]
                ):
        # test init job
        if _num == constant.init["job"] and _uname == constant.init["user"]:
            _state = constant.init["state"]
            self.user_add()
        # test user of job
        try:
            _uquery = self.user_query("one", _uname)
        except:
            pass
        else:
            _query = self.job_query("all", _num)
            if _query == []:
                add_row = Job()
                add_row.num = int(_num)
                add_row.user_id = _uquery.id
                add_row.const_state = u""+_state
                self.__session.add(add_row)
                self.__session.commit()

    def job_mod_state(self, _num, _state):
        # test job number
        try:
            _query = self.job_query("one", _num)
        except:
            pass
        else:
            _query.const_state = u""+_state
            self.__session.commit()

    def job_mod_cmd(self, _num, _cmd):
        # test job number
        try:
            _query = self.job_query("one", _num)
        except:
            pass
        else:
            _query.cmd = u""+_cmd
            self.__session.commit()

    def job_mod_log(self, _num, _log):
        # test job number
        try:
            _query = self.job_query("one", _num)
        except:
            pass
        else:
            _query.log = u""+_log
            self.__session.commit()

    def job_del(self, _num=False, _uname=False, _state=False):
        _query = self.job_query("all", _num, _uname, _state)
        for _q in _query:
            # migrate programms to init job
            for q_prog in _q.progs:
                q_prog.job_id = self.job_query(
                    "one",constant.init["job"]
                ).id
                self.__session.commit()
            # migrate files to init job
            for q_file in _q.files:
                q_file.job_id = self.job_query(
                    "one",constant.init["job"]
                ).id
                self.__session.commit()
            self.__session.delete(_q)
            self.__session.commit()

    def prog_query(self, _qtype, _name=False, _job=False):
        query = self.__session.query(Prog)
        if _name:
            query = query.filter_by(name=u""+_name)
        if _job:
            query = query.filter_by(job_num=int(_job))
        if _qtype == "all":
            return query.all()
        elif _qtype == "one":
            return query.one()
        elif _qtype == "first":
            return query.first()

    def prog_add(self, _name, _job=constant.init["job"]):
        # test programm name
        _query = self.prog_query("all", _name)
        if _query == []:
            add_row = Prog()
            add_row.name = u""+_name
            add_row.job_id = self.job_query("one", _job).id
            self.__session.add(add_row)
            self.__session.commit()

    def prog_del(self, _name=False, _job=False):
        _query = self.prog_query("all", _name, _job)
        for _q in _query:
            # delete versions of prog
            self.ver_del(_q.name)
            # delete prog
            self.__session.delete(_q)
            self.__session.commit()

    def ver_query(self, _qtype,
                  _prog=False,
                  _vname=False
                  ):
        query = self.__session.query(Ver)
        if _prog:
            query = query.filter_by(prog_nam=u""+_prog)
        if _vname:
            query = query.filter_by(name=u""+_vname)
        if _qtype == "all":
            return query.all()
        elif _qtype == "one":
            return query.one()
        elif _qtype == "first":
            return query.first()

    def ver_add(self, _prog, _vname):
        # test programm for version
        try:
            _pquery = self.prog_query("one", _prog)
        except:
            pass
        else:
            # find version
            _query = self.ver_query("all", _prog, _vname)
            if _query == []:
                add_row = Ver()
                add_row.name = u""+_vname
                add_row.prog_id = _pquery.id
                self.__session.add(add_row)
                self.__session.commit()

    def ver_del(self, _prog, _vname=False):
        _query = self.ver_query("all", _prog, _vname)
        for _q in _query:
            # delete file of ver
            self.file_del(False, _q.prog_nam, _q.name)
            # delete ver
            self.__session.delete(_q)
            self.__session.commit()

    def file_query(self, _qtype,
                   _name=False,
                   _prog=False,
                   _ver=False,
                   _type=False,
                   _arch=False,
                   _job=False
                   ):
        query = self.__session.query(File)
        if _name:
            query = query.filter_by(name=u""+_name)
        if _prog:
            query = query.filter_by(prog_nam=u""+_prog)
        if _ver:
            query = query.filter_by(ver_nam=u""+_ver)
        if _type:
            query = query.filter_by(const_type=u""+_type)
        if _arch:
            query = query.filter_by(const_arch=u""+_arch)
        if _job:
            query = query.filter_by(job_num=int(_job))
        if _qtype == "all":
            return query.all()
        elif _qtype == "one":
            return query.one()
        elif _qtype == "first":
            return query.first()

    def file_add(self,
                 _name,
                 _prog,
                 _ver,
                 _arch,
                 _job=constant.init["job"]
                 ):
        # test version for file
        try:
            _vquery = self.ver_query("one", _prog, _ver)
        except:
            return False
        else:
            # find fle
            _query = self.file_query("all",
                                     _name,
                                     _prog,
                                     _ver,
                                     False,
                                     _arch)
            if _query == []:
                ex = _name.split(".")[-1]
                _type = constant.ftype[ex]
                add_row = File()
                add_row.name = u""+_name
                add_row.ver_id = _vquery.id
                add_row.const_type = u""+_type
                add_row.const_arch = u""+_arch
                add_row.job_id = self.job_query("one", _job).id
                self.__session.add(add_row)
                self.__session.commit()
            return True

    def file_del(self,
                 _name=False,
                 _prog=False,
                 _ver=False,
                 _arch=False,
                 _job=False):
        _query = self.file_query("all",
                                 _name,
                                 _prog,
                                 _ver,
                                 False,
                                 _arch,
                                 _job)
        for _q in _query:
            self.__session.delete(_q)
            self.__session.commit()
