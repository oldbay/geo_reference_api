#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

import os
import imp
import paramiko
from urllib2 import urlopen
from lxml import html
from urlparse import urlparse
import time
from crypt import crypt
from hmac import compare_digest
from random import choice
from string import ascii_uppercase, ascii_lowercase, digits

import constant
conf = imp.load_source("conf", os.path.dirname(constant.__file__)+"/service.conf")

from db_interface import Operation

# import Queue
# Queues = {}


class Ssh(object):

    """
    connect from ssh to deploy server
    """

    def_path = "env PATH=$PATH:"+conf.path
    def_key = os.path.dirname(constant.__file__)+"/"+conf.key
    param_log = os.path.dirname(constant.__file__)+"/log/paramiko.log"

    def __init__(self, host=conf.host, sshuser=conf.sshuser, keypath=def_key):
        paramiko.util.log_to_file(self.param_log)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            host,
            username=sshuser,
            key_filename=keypath
        )

    def __del__(self):
        self.ssh.close()

    def command(self, cmd, path=def_path):
        stdin, stdout, stderr = self.ssh.exec_command(path+" "+cmd)
        return {
            "stdout": [
                out[:-1]
                for out
                in stdout.readlines()
                if out != None
            ],
            "stderr": [
                out[:-1]
                for out
                in stderr.readlines()
                if out != None
            ],
        }

    def ssh_close(self):
        self.ssh.close()


class Html(object):

    def __init__(self):
        self.url = "http://"+conf.host+"/"

    def filelist(self, dirs=[]):
        if dirs == []:
            dirs = [self.url]
        newdirs = []
        for _dir in dirs:
            try:
                _urlpath = urlopen(_dir)
            except:
                return False
            else:
                _data = html.parse(_urlpath)
                _hrefs = _data.xpath('/html/body/pre/a/@href')
            for _href in _hrefs:
                if _href[-1] == "/" and _href[0] != "/":
                    newdirs.append(_dir+_href)
        if newdirs == []:
            filedirs = []
            for _dir in dirs:
                try:
                    _urlpath = urlopen(_dir)
                except:
                    return False
                else:
                    _data = html.parse(_urlpath)
                    _hrefs = _data.xpath('/html/body/pre/a/@href')
                    _path = _dir.split("/")[3:-1]
                    # fix version name
                    src = Source()
                    src.name = _path[0]
                    src.ver = _path[2]
                    fix_ver = src.ver2ver()
                    _path[2] = fix_ver
                    # end fix
                for _href in _hrefs:
                    if _href[0] != "?" and _href[0] != "/":
                        _filepath = []
                        _filepath = _path[:]
                        _filepath.append(_href)
                        filedirs.append(_filepath)
            return filedirs
        else:
            return self.filelist(newdirs)


class Init(object):

    """
    Total init or update database
    """

    __dbi = Operation()

    def __init__(self, activ=True):
        self.__iactiv = activ
        if self.__iactiv:
            self.users_add()
            self.sources_add()
            self.packages_add()

    def users_add(self):
        usr = User()
        usr.user2db()
        usr.job2db()

    def users_info(self, _detail=False):
        _query = self.__dbi.user_query("all")
        users = []
        for uname in [ usr.name for usr in _query ]:
            if _detail:
                usr = User(uname)
                job = usr.job_info()
            else:
                job = False
            users.append({
                "name": uname,
                "jobs": job
            })
        return users

    def sources_add(self):
        cmd = Ssh().command("dep_pkg -P")
        if cmd["stderr"] == []:
            _query = self.__dbi.prog_query("all")
            srcs = [src.name for src in _query]
            for name in cmd["stdout"]:
                print "add "+name
                self.__dbi.prog_add(name, constant.init["job"])
                if name in srcs:
                    srcs.remove(name)
                src = Source()
                src.name = name
                src.vers2db()
            for src in srcs:
                print "del "+src
                self.__dbi.prog_del(src)

    def sources_info(self, _detail=False):
        _query = self.__dbi.prog_query("all")
        sources = []
        for prog, job in [[prog.name, prog.job_num] for prog in _query]:
            if _detail:
                src = Source()
                src.name = prog
                vers = src.info()[0]["ver"]
            else:
                vers = False
            sources.append({
                "prog": prog,
                "ver": vers,
                "job": job
            })
        return sources

    def packages_add(self):
        _query = self.__dbi.file_query("all")
        pkgs = [[pkg.prog_nam,
                 pkg.const_arch,
                 pkg.ver_nam,
                 pkg.name] for pkg in _query]
        files = Html().filelist()
        # print files
        for _file in files:
            if _file not in pkgs:
               # print _file
               _test = self.__dbi.file_add(_file[3], _file[0], _file[2], _file[1])
               if not _test:
                   pkgs.append(_file)
            else:
                pkgs.remove(_file)
        for _pkg in pkgs:
            self.__dbi.file_del(_pkg[3], _pkg[0], _pkg[2], _pkg[1])

    def packages_info(self):
        _query = self.__dbi.file_query("all")
        return [{"prog": pkg.prog_nam,
                 "arch": pkg.const_arch,
                 "type": pkg.const_type,
                 "ver": pkg.ver_nam,
                 "fname": pkg.name} for pkg in _query]


class QProc(object):

    """
    Class Queue for run command
    """

    __dbi = Operation()

    def __init__(self):
        self.run_cache = {}
        # clear old queue
        self.__dbi.queue_del()

    def __del__(self):
        print "STOP QUEUE PROCESS"

    def __qend(self, queue, job, index, state):
        if conf.QEcho:
            print "------------------------------------"
            print "JOB: "+str(job)+" is end, status="+state
            print "------------------------------------"
        # read job log
        cmd = Ssh().command("scr_sess -l -n "+str(job))
        log = cmd['stdout']
        # read file list in log
        files = []
        if conf.QEcho:
            print "-----------"
            print "FILES:"
            print "-----------"
        for _str in log:
            sstr = _str.split(":")
            if sstr[0] == "FILE_OUT":
                filename = sstr[-1].split(constant.csvd)[-1]
                if conf.QEcho:
                    print filename
                files.append(filename)
        # write log & files to job
        log = "\n".join(log)
        self.__dbi.job_mod_log(job, log)
        if conf.QEcho:
            print "-----------"
            print "OUT LOG:"
            print "-----------"
            print log
        # quend
        _obj = self.__dbi.queue_qend(queue)
        _obj.qend(state, files)
        # delete end job to deploy server
        cmd = Ssh().command("scr_sess -r -n "+str(job))
        if conf.QEcho and cmd["stderr"] == []:
            print "-------------------------------------"
            print "JOB "+str(job) +" delite to deploy server"
            print "-------------------------------------"

    def qround(self):
        run = False
        _query = self.__dbi.queue_query("all")
        if _query != []:
            self.task_run = {}
            run = True
            if conf.QEcho:
                print "---------------"
                print "START QUEUE STEP "
                print "---------------"
        while run:
            # query queue
            _query = self.__dbi.queue_query("all")
            # stop round for empty
            if _query == []:
                if conf.QEcho:
                    print "---------------"
                    print "END QUEUE STEP "
                    print "---------------"
                run = False
                continue
            # refresh all screen sessions
            cmd = Ssh().command("scr_sess -C -S")
            jobs = [c.split(";")[0] for c in cmd["stdout"]]
            stats = [c.split(";")[-1] for c in cmd["stdout"]]
            # QUEUE body
            for _queue in _query:
                queue = _queue.qkey
                _que = self.__dbi.que_query("first", queue)
                if _que.stat:
                    job = _que.job_num
                    index = jobs.index(str(job))
                    state = stats[index]
                    if state != constant.state["n2s"]["run"]:
                        self.__qend(queue, job, index, state)
                else:
                    #qstart
                    _obj = self.__dbi.queue_get(queue)
                    _obj.qstart()

    def proc(self, sleep_sec):
        while True:
            self.qround()
            time.sleep(sleep_sec)


class User():

    """
    Class Uaser & Job comand
    """

    __dbi = Operation()

    def __init__(self, _name=False, _key=False):
        self.name = _name
        self.key = _key

    def user2db(self):
        if not self.name:
            self.__dbi.user_add()
        else:
            self.__dbi.user_add(self.name, self.key)

    def job2db(self, jname=False):
        if not self.name or not jname:
            self.__dbi.job_add()
        else:
            self.__dbi.job_add(jname, self.name)

    def usermod(self, _new_key = False):
        _token = "".join(choice(
            ascii_uppercase + ascii_lowercase + digits
            ) for x in range(16))
        _query = self.__dbi.user_query("all", self.name)
        if _query == []:
            _hash = crypt(self.key, _token)
            self.__dbi.user_add(self.name, _hash)
            return True
        elif len(_query) == 1:
            if self.auth():
                if _new_key:
                    _hash = crypt(_new_key, _token)
                    self.__dbi.user_mod_key(self.name, _hash)
                return True
            else:
                return False
        else:
            return False

    def auth(self):
        try:
            _query = self.__dbi.user_query("one", self.name)
        except:
            return False
        else:
            if _query != None:
                _testhash = str(_query.key)
                if compare_digest(_testhash, crypt(self.key, _testhash)):
                    return True
                else:
                    return False
            else:
                return False

    def job_info(self, job_num=False):
        jobs = []
        for job in self.__dbi.job_query("all", job_num, self.name):
            _qquery = self.__dbi.que_query("all", False, job.num)
            ques = [que.queue_key for que in _qquery]
            _squery = self.__dbi.prog_query("all", False, job.num)
            srcs = [src.name for src in _squery]
            _pquery = self.__dbi.file_query("all", False, False,
                                            False, False, False,
                                            job.num)
            pkgs = [pkg.name for pkg in _pquery]
            jobs.append({"job": job.num,
                         "cmd": job.cmd,
                         "log": job.log,
                         "queue": ques,
                         "srcs": srcs,
                         "pkgs": pkgs,
                         "state": constant.state["s2n"][job.const_state]
                         })
        return jobs


class Source(object):

    """
    Class cource commands
    """

    __dbi = Operation()
    name = False
    dig = False
    ver = False

    def vers2db(self):
        cmd = Ssh().command("dep_pkg -p -C -n "+self.name)
        if cmd["stderr"] == []:
            _query = self.__dbi.ver_query("all", self.name)
            vers = [ver.name for ver in _query]
            for ver in cmd["stdout"]:
                ver = ver.split(constant.csvd)[1]
                self.__dbi.ver_add(self.name, ver)
                if ver in vers:
                    vers.remove(ver)
            for ver in vers:
                self.__dbi.ver_del(self.name, ver)

    def info(self):
        _query = self.__dbi.ver_query("all", self.name)
        _vers = [ver.name for ver in _query]
        return [{"ver": _vers}]

    def ver2ver(self):
        if self.name:
            all_ver = self.info()[0]["ver"]
            for vname in all_ver:
                if self.ver == vname.split("/")[-1]:
                    return vname

    def create(self, user=constant.init["user"]):
        git_link = self.name
        self.name = False
        _parse = urlparse(git_link)
        if _parse.scheme != "" and _parse.netloc != "":
            self.qcmd = "scr dep_pkg -g "+git_link
            self.name = _parse.path.split("/")[-1].split(".")[0]
            self.user = user
            self.oper = "add"
            # Queue
            self.qkey = self.name+"_src"
            self.__dbi.queue_put(self.qkey, self)
            return True
        else:
            return False

    def remove(self, user=constant.init["user"]):
        if self.name:
            self.qcmd = "scr dep_pkg -R -n "+self.name
            self.user = user
            self.oper = "del"
            # Queue
            self.qkey = self.name+"_src"
            self.__dbi.queue_put(self.qkey, self)
            return True
        else:
            return False

    def qstart(self):
        cmd = Ssh().command(self.qcmd)
        if cmd["stderr"] == []:
            self.qjob = int(cmd["stdout"][0])
            self.__dbi.job_add(self.qjob, self.user)
            #Queue
            self.__dbi.queue_qstart(self.qkey, self.qjob, self)

    def qend(self, state, files = []):
        self.__dbi.job_mod_cmd(self.qjob, self.qcmd)
        if state == "0":
            self.__dbi.job_mod_state(self.qjob, constant.state["n2s"]["ok"])
            if self.oper == "add":
                self.__dbi.prog_add(self.name, self.qjob)
                self.vers2db()
            elif self.oper == "del":
                self.__dbi.prog_del(self.name)
        elif state == "1":
            self.__dbi.job_mod_state(self.qjob, constant.state["n2s"]["fail"])
        elif state == "2":
            self.qjob = constant.init["job"]
            #return queue
            self.__dbi.queue_put(self.qkey, self)


class Package(object):

    """
    Class package comands
    """

    __dbi = Operation()
    name = False
    dig = False
    ver = False

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name == "dig":
            if value:
                self.arch = constant.arch[value]
            else:
                self.arch = False

    def info(self, _fname=False):
        _query = self.__dbi.file_query("all",
                                       _fname,
                                       self.name,
                                       self.ver,
                                       False,
                                       self.arch)
        return [{"prog": pkg.prog_nam,
                 "arch": pkg.const_arch,
                 "type": pkg.const_type,
                 "ver": pkg.ver_nam,
                 "fname": pkg.name} for pkg in _query]

    def create(self, user=constant.init["user"]):
        _query = self.__dbi.ver_query("all", self.name, self.ver)
        if _query != []:
            if self.name and self.ver and self.dig:
                self.qcmd = "scr dep_pkg -B -n "+self.name+\
                    " -v "+self.ver+" -a "+str(self.dig)
                self.user = user
                self.oper = "add"
                # Queue
                self.qkey = self.name+"_"+str(self.dig)
                self.__dbi.queue_put(self.qkey, self)
                return True
            else:
                return False
        else:
            return False

    def remove(self, user=constant.init["user"]):
        if self.name and self.dig:
            if self.ver:
                _query = self.__dbi.file_query("all",
                                              False,
                                              self.name,
                                              self.ver,
                                              False,
                                              self.arch)
                if _query != []:
                    self.qcmd = "scr dep_pkg -r -n "+self.name+\
                        " -v "+self.ver+" -a "+str(self.dig)
                else:
                    return False
            else:
                self.qcmd = "scr dep_pkg -r -n "+self.name+\
                    " -a "+str(self.dig)
            self.user = user
            self.oper = "del"
            # Queue
            self.qkey = self.name+"_"+str(self.dig)
            self.__dbi.queue_put(self.qkey, self)
            return True
        else:
            return False

    def qstart(self):
        cmd = Ssh().command(self.qcmd)
        if cmd["stderr"] == []:
            self.qjob = int(cmd["stdout"][0])
            self.__dbi.job_add(self.qjob, self.user)
            #Queue
            self.__dbi.queue_qstart(self.qkey, self.qjob, self)

    def qend(self, state, files=[]):
        self.__dbi.job_mod_cmd(self.qjob, self.qcmd)
        if state == "0":
            self.__dbi.job_mod_state(self.qjob, constant.state["n2s"]["ok"])
            if self.oper == "add":
                for _file in files:
                    self.__dbi.file_add(_file,
                                        self.name,
                                        self.ver,
                                        self.arch,
                                        self.qjob)
            elif self.oper == "del":
                self.__dbi.file_del(False,
                                    self.name,
                                    self.ver,
                                    self.arch)
        elif state == "1":
            self.__dbi.job_mod_state(self.qjob, constant.state["n2s"]["fail"])
            for _file in files:
                self.__dbi.file_add(_file,
                                    self.name,
                                    self.ver,
                                    self.arch,
                                    self.qjob)
        elif state == "2":
            self.qjob = constant.init["job"]
            # return queue
            self.__dbi.queue_put(self.qkey, self)
