import os
import imp
import json

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import constant
from model import DeclarativeBase

def_nesting = 0
conf = imp.load_source("conf", os.path.dirname(constant.__file__)+"/service.conf")

# create base
if conf.DBPath:
    DBPath = conf.DBPath
else:
    DBPath = 'sqlite:///:memory:'
engine = create_engine(DBPath, echo=conf.DBEcho)
DeclarativeBase.metadata.create_all(engine)


# create api
api_resources = {}
for table_class in DeclarativeBase.__subclasses__():
    res_name = table_class.__tablename__
    res_serial = {}
    res_deserial = {}
    for serial_obj in table_class.__serialization__:
        col_name = serial_obj.name
        try:
            col_type = table_class.__dict__[col_name].type.python_type
        except AttributeError:
            col_type = dict
        col_api = {
            col_name: col_type,
        }
        if serial_obj.supports_json[1]:
            res_serial.update(col_api)
        if serial_obj.supports_json[0]:
            res_deserial.update(col_api)

    if res_serial or res_deserial:
        api_resources[res_name] = {
            "obj": table_class,
            "serial": res_serial,
            "deserial": res_deserial,
        }

for name in api_resources:
    print (name)
    print (api_resources[name])


# session
Session = sessionmaker(bind=engine)
session = Session()

def insert(table, qdict):
    que = table.new_from_json(json.dumps(qdict))
    session.add(que)
    session.commit()

def select(table, qdict):
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

# update
# {"id":num(for find) "key":"name"} id add to deserialize from update 

# delite
# {"id":num(for find)} id add to deserialize from delite 



api_requsts = {
    "GET": select,
    "POST": insert,
}
print (api_requsts)


# run
def qrun(queries):
    for q in queries:
        request = api_requsts[q['req']]
        resource = api_resources[q['res']]['obj']
        query = q['que']
        print (
            request(resource, query)
        )
        print ("")


if __name__ == "__main__":
    queries = [
        {
            "req": "POST",
            "res": 'groups',
            "que": {
                "name": "Группа1", 
            } 
        }, 
        {
            "req": "POST",
            "res": 'modules',
            "que": {
                "name": "Модуль1", 
            } 
        }, 
        {
            "req": "POST",
            "res": 'modules',
            "que": {
                "name": "Модуль2", 
            } 
        }, 
        {
            "req": "POST",
            "res": 'groups',
            "que": {
                "name": "Группа2", 
            } 
        }, 
        {
            "req": "POST",
            "res": 'users',
            "que": {
                "name": "Миша", 
                "group_id": 1,
            } 
        }, 
        {
            "req": "POST",
            "res": 'users',
            "que": {
                "name": "Ваня", 
                "group_id": 1,
            } 
        }, 
        {
            "req": "POST",
            "res": 'users',
            "que": {
                "name": "Петя", 
                "group_id": 2,
            } 
        }, 
        {
            "req": "GET",
            "res": 'groups',
            "que": {
                "max_nesting": 2,
            }
        }, 
        {
            "req": "GET",
            "res": 'modules',
            "que": {
                "max_nesting": 2,
            }
        }, 
        {
            "req": "GET",
            "res": 'modules_permissions',
            "que": {
                "max_nesting": 2,
            }
        }, 
        {
            "req": "GET",
            "res": 'modules_permissions',
            "que": {
                "group": "Группа2",
                "module": "Модуль2",
                "max_nesting": 2,
            }
        }, 
        #{
            #"req": "GET",
            #"res": 'users',
            #"que": {
                #"id": 1,
            #}
        #}, 
        #{
            #"req": "GET",
            #"res": 'users',
            #"que": {
                #"name": "Петя",
            #}
        #}, 
        {
            "req": "GET",
            "res": 'users',
            "que": {
                "max_nesting": 1,
            }
        }, 
    ]
    qrun(queries)
