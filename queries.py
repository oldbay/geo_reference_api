import os
import imp
import json

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import constant
from model import DeclarativeBase
from model import (
    Users, 
    Groups, 
    Modules, 
    ModulesPermissions
)

def_nesting = 0

conf = imp.load_source("conf", os.path.dirname(constant.__file__)+"/service.conf")
if conf.DBPath:
    DBPath = conf.DBPath
else:
    DBPath = 'sqlite:///:memory:'
engine = create_engine(DBPath, echo=conf.DBEcho)
DeclarativeBase.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def post(table, qdict):
    que = table.new_from_json(json.dumps(qdict))
    session.add(que)
    session.commit()

def get(table, qdict):

    max_nesting = qdict.get('max_nesting', def_nesting)
    if max_nesting != def_nesting: del(qdict['max_nesting'])
    
    table_query = session.query(table)
    find_list = table_query.filter_by(**qdict)

    result = []
    for find_obj in find_list:
        result.append(
            json.loads(
                find_obj.to_json(max_nesting=max_nesting)
            )
        )
    return result

def qrun(queries):
    for q in queries:
        print (
            q["opt"](q["tab"], q["que"])
        )
        print ("")

if __name__ == "__main__":
    queries = [
        {
            "opt": post,
            "tab": Groups,
            "que": {
                "name": "Группа1", 
            } 
        }, 
        {
            "opt": post,
            "tab": Modules,
            "que": {
                "name": "Модуль1", 
            } 
        }, 
        {
            "opt": post,
            "tab": Modules,
            "que": {
                "name": "Модуль2", 
            } 
        }, 
        {
            "opt": post,
            "tab": Groups,
            "que": {
                "name": "Группа2", 
            } 
        }, 
        #{
            #"opt": post,
            #"tab": ModulesPermissions,
            #"que": {
                #"permission_level": 1,
                #"group_id": 1,
                #"module_id": 1,
            #} 
        #}, 
        #{
            #"opt": post,
            #"tab": ModulesPermissions,
            #"que": {
                #"permission_level": 0,
                #"group_id": 1,
                #"module_id": 2,
            #} 
        #}, 
        #{
            #"opt": post,
            #"tab": ModulesPermissions,
            #"que": {
                #"permission_level": 2,
                #"group_id": 2,
                #"module_id": 1,
            #} 
        #}, 
        #{
            #"opt": post,
            #"tab": ModulesPermissions,
            #"que": {
                #"permission_level": 0,
                #"group_id": 2,
                #"module_id": 2,
            #} 
        #}, 
        {
            "opt": post,
            "tab": Users,
            "que": {
                "name": "Миша", 
                "group_id": 1,
            } 
        }, 
        {
            "opt": post,
            "tab": Users,
            "que": {
                "name": "Ваня", 
                "group_id": 1,
            } 
        }, 
        {
            "opt": post,
            "tab": Users,
            "que": {
                "name": "Петя", 
                "group_id": 2,
            } 
        }, 
        {
            "opt": get,
            "tab": Groups,
            "que": {
                "max_nesting": 2,
            }
        }, 
        {
            "opt": get,
            "tab": Modules,
            "que": {
                "max_nesting": 2,
            }
        }, 
        {
            "opt": get,
            "tab": ModulesPermissions,
            "que": {
                "max_nesting": 2,
            }
        }, 
        {
            "opt": get,
            "tab": ModulesPermissions,
            "que": {
                "group": "Группа2",
                "module": "Модуль2",
                "max_nesting": 2,
            }
        }, 
        #{
            #"opt": get,
            #"tab": Users,
            #"que": {
                #"id": 1,
            #}
        #}, 
        #{
            #"opt": get,
            #"tab": Users,
            #"que": {
                #"name": "Петя",
            #}
        #}, 
        {
            "opt": get,
            "tab": Users,
            "que": {
                "max_nesting": 1,
            }
        }, 
    ]
    qrun(queries)
