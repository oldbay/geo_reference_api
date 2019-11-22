import json
import copy

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from . import config

# loading module base
from .api_modules import base
# loading other modules
from .api_modules import (
    test01, 
    test11, 
    test12, 
    test21, 
)
# DeclarativeBase is last import
from .modules_factory import DeclarativeBase, ApiModuleConstructor

#print ({my.__tablename__:my for my in DeclarativeBase.__subclasses__()})

def_nesting = 2
nesting_name = 'api_nesting'
find_prefix = 'api_find_{}'

# create base
if config.DBPath:
    DBPath = config.DBPath
else:
    DBPath = 'sqlite:///:memory:'
engine = create_engine(DBPath, echo=config.DBEcho)
DeclarativeBase.metadata.create_all(engine)

# session
Session = sessionmaker(bind=engine)
session = Session()

# create api
api_resources = {}
for table_class in DeclarativeBase.__subclasses__():
    api_module = table_class.__module_name__
    res_name = table_class.__tablename__
    res_doc = table_class.__doc__
    #print (res_name)
    #print (table_class.__tables_dict__) 
    res_get = {}
    res_post = {}
    res_put = {}
    res_delete = {}
    for serial_obj in table_class.__serialization__:
        col_name = serial_obj.name
        try:
            col_type = table_class.__dict__[col_name].type.python_type
        except AttributeError:
            col_type = dict
        if serial_obj.supports_json[0]:
            res_post.update({col_name: col_type})
            res_put.update({col_name: col_type})
        if serial_obj.supports_json[1]:
            res_get.update({col_name: col_type})
            res_put.update({find_prefix.format(col_name): col_type})
            res_delete.update({find_prefix.format(col_name): col_type})
    if res_get:
        res_get.update({nesting_name: int})
    if res_get or res_post or res_put or res_delete:
        api_resources[res_name] = {
            "obj": table_class,
            "module": api_module,
            "GET": res_get,
            "POST": res_post,
            "PUT": res_put,
            "DELETE": res_delete,
        }

#print ("*"*10)
#for name in api_resources:
    #print (name)
    #print (api_resources[name])


def select(table, qdict):
    max_nesting = qdict.get(nesting_name, def_nesting)
    if nesting_name in qdict.keys(): del(qdict[nesting_name])
    
    table_query = session.query(table)
    find_list = table_query.filter_by(**qdict)

    result = []
    for tab_obj in find_list:
        result.append(
            json.loads(
                tab_obj.to_json(max_nesting=max_nesting)
            )
        )
    return result

def insert(table, qdict):
    tab_obj = table.new_from_json(json.dumps(qdict))
    session.add(tab_obj)
    session.commit()
    return select(table, qdict)

def find_prefix_attrs(qdict):
    qdict_attrs = copy.deepcopy(qdict)
    find_attrs = {}
    for key in qdict.keys():
        attrs_test = key.split(find_prefix.format(''))
        if len(attrs_test) == 2:
            find_attrs[attrs_test[-1]] = qdict[key]
            del(qdict_attrs[key]) 
    find_attrs.update()
    return find_attrs, qdict_attrs

def update(table, qdict):
    find_attrs, qdict_attrs = find_prefix_attrs(qdict)
    
    table_query = session.query(table)
    find_list = table_query.filter_by(**find_attrs)
    for tab_obj in find_list:
        tab_obj.update_from_json(json.dumps(qdict_attrs))
        session.commit()
        
    find_attrs.update(qdict_attrs)
    return select(table, find_attrs)

def delete(table, qdict):
    find_attrs, qdict_attrs = find_prefix_attrs(qdict)
    
    table_query = session.query(table)
    find_list = table_query.filter_by(**find_attrs)
    for tab_obj in find_list:
        session.delete(tab_obj)
        session.commit()
        
    return select(table, find_attrs)

api_requsts = {
    "GET": select,
    "POST": insert,
    "PUT": update,
    "DELETE": delete,
}


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