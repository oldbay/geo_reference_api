import os
import json
import copy
import imp
import importlib

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from . import config
from .modules_factory import ExceptionDepend

# loading module base
from .api_modules import base
# loading other modules
for imp_module in config.ApiModules:
    try:
        if os.path.isfile(imp_module):
            imp.load_source("_", imp_module)
        else:
            importlib.import_module(imp_module)
    except ExceptionDepend as err:
        print(
            "Broken Depends for Load module '{0}' : '{1}'".format(
                imp_module, 
                err, 
            )
        )
# DeclarativeBase is last import
from .modules_factory import DeclarativeBase, ApiModuleConstructor

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
api_struct = {}
for table_class in DeclarativeBase.__subclasses__():
    api_module = table_class.__module_name__
    if api_module not in api_struct:
        api_struct[api_module] = {
            "module_depends": table_class.__module_depends__,
            "module_doc": table_class.__module_doc__,
        }
    res_name = table_class.__tablename__
    api_resources[res_name] = {
        "obj": table_class,
        "GET": {},
        "POST": {},
        "PUT": {},
        "DELETE": {},
    }
    api_struct[api_module][res_name] = {
        "resource_doc": table_class.__doc__,
        "GET": {},
        "POST": {},
        "PUT": {},
        "DELETE": {},
    }
    table2resource = False
    for serial_obj in table_class.__serialization__:
        col_name = serial_obj.name
        try:
            col_type = table_class.__dict__[col_name].type.python_type
        except AttributeError:
            col_type = dict

        if serial_obj.supports_json[0]:
            table2resource = True
            api_resources[res_name]['POST'].update({col_name: col_type})
            api_struct[api_module][res_name]['POST'].update(
                {col_name: col_type.__name__}
            )
            api_resources[res_name]['PUT'].update({col_name: col_type})
            api_struct[api_module][res_name]['PUT'].update(
                {col_name: col_type.__name__}
            )
        if serial_obj.supports_json[1]:
            table2resource = True
            api_resources[res_name]['GET'].update({col_name: col_type})
            api_struct[api_module][res_name]['GET'].update(
                {col_name: col_type.__name__}
            )
            if col_type is not dict:
                api_resources[res_name]['PUT'].update(
                    {find_prefix.format(col_name): col_type}
                )
                api_struct[api_module][res_name]['PUT'].update(
                    {find_prefix.format(col_name): col_type.__name__}
                )
                api_resources[res_name]['DELETE'].update(
                    {find_prefix.format(col_name): col_type}
                )
                api_struct[api_module][res_name]['DELETE'].update(
                    {find_prefix.format(col_name): col_type.__name__}
                )
    if api_resources[res_name]['GET']:
        api_resources[res_name]['GET'].update({nesting_name: int})
        api_struct[api_module][res_name]['GET'].update({nesting_name: int.__name__})
        
    if not table2resource:
        del(api_requsts[res_name])
        del(api_struct[api_module][res_name])


# Api struct wiev
for module in api_struct:
    print ("module: {} -...".format(module))
    for mod_key in api_struct[module]:
        if isinstance(api_struct[module][mod_key], dict):
            print (
                "    resource: {} -...".format(mod_key)
            )
            for api_key in api_struct[module][mod_key]:
                if isinstance(api_struct[module][mod_key][api_key], dict):
                    print (
                        "        {} -...".format(api_key)
                    )
                    for res_var in api_struct[module][mod_key][api_key]:
                        print (
                            "            {0}: {1}".format(
                                res_var, api_struct[module][mod_key][api_key][res_var]
                            )
                        )
                else:
                    print (
                        "        {0}: {1}".format(
                            api_key, api_struct[module][mod_key][api_key]
                        )
                    )
        else:
            print (
                "    {0}: {1}".format(mod_key, api_struct[module][mod_key])
            )
print ("*"*10)


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

def serialize_run(query):
    request = api_requsts[query['req']]
    resource = api_resources[query['res']]['obj']
    validate = api_resources[query['res']][query['req']]
    serial_query = query['que']
    # type validate
    for key in serial_query:
        if not isinstance(serial_query[key], validate[key]):
            print (
                "query:'{0}'\n\
                For key '{1}' type '{2}' not valid, but expected type: '{3}'".format(
                    query,
                    key,
                    type(serial_query[key]).__name__,
                    validate[key].__name__, 
                )
            )
            return False
    return request(resource, serial_query)