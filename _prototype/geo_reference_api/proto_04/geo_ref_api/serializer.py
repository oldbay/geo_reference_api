import os
import json
import copy
import imp
import importlib
from datetime import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from . import config
from .modules_factory import ExceptionDepend

# loading module base
from .api_modules import base
# loading other modules
load_modules_name = []
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
    else:
        load_modules_name.append(imp_module)
# DeclarativeBase is last import
from .modules_factory import DeclarativeBase, ApiModuleConstructor

nesting_name = 'api_nesting'
modules_table_name = 'modules'
users_table_name = 'users'
#groups_table_name = 'groups'
modules_permissions_table_name = 'modules_permissions'
find_prefix = 'api_find_{}'

# create base
if config.DBPath:
    DBPath = config.DBPath
else:
    DBPath = 'sqlite:///:memory:'
engine = create_engine(DBPath, echo=config.DBEcho)
DeclarativeBase.metadata.create_all(engine)


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
        "module": api_module,
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
    for serial_obj in table_class.__serialization__:
        col_name = serial_obj.name
        try:
            col_type = table_class.__dict__[col_name].type.python_type
        except AttributeError:
            col_type = dict

        if serial_obj.supports_json[0]:
            if 'POST' in table_class.__http__:
                api_resources[res_name]['POST'].update({col_name: col_type})
                api_struct[api_module][res_name]['POST'].update(
                    {col_name: col_type.__name__}
                )
            if 'PUT' in table_class.__http__:
                api_resources[res_name]['PUT'].update({col_name: col_type})
                api_struct[api_module][res_name]['PUT'].update(
                    {col_name: col_type.__name__}
                )
        if serial_obj.supports_json[1]:
            if 'GET' in table_class.__http__:
                api_resources[res_name]['GET'].update({col_name: col_type})
                api_struct[api_module][res_name]['GET'].update(
                    {col_name: col_type.__name__}
                )
            if col_type is not dict:
                if 'PUT' in table_class.__http__:
                    api_resources[res_name]['PUT'].update(
                        {find_prefix.format(col_name): col_type}
                    )
                    api_struct[api_module][res_name]['PUT'].update(
                        {find_prefix.format(col_name): col_type.__name__}
                    )
                if 'DELETE' in table_class.__http__:
                    api_resources[res_name]['DELETE'].update(
                        {find_prefix.format(col_name): col_type}
                    )
                    api_struct[api_module][res_name]['DELETE'].update(
                        {find_prefix.format(col_name): col_type.__name__}
                    )
    if 'GET' in table_class.__http__ and api_resources[res_name]['GET']:
        api_resources[res_name]['GET'].update({nesting_name: int})
        api_struct[api_module][res_name]['GET'].update({nesting_name: int.__name__})
    
    table2resource = False
    for http in ['GET', 'POST', 'PUT', 'DELETE']:
        if not api_resources[res_name][http]:
            del(api_resources[res_name][http])
            del(api_struct[api_module][res_name][http])
        else:
            table2resource = True
    
    if not table2resource:
        del(api_resources[res_name])
        del(api_struct[api_module][res_name])


# session
Session = sessionmaker(bind=engine)
session = Session()


# Create or update modules table
modules_query = session.query(api_resources[modules_table_name]['obj'])
modules_db_name = set([my.name for my in modules_query.all()])
modules_imp_name = set([my for my in api_struct])
# add new modules
for modname in list(modules_imp_name-modules_db_name):
    new_mod = api_resources['modules']['obj']()
    new_mod.name = modname
    new_mod.access = True
    new_mod.enable = True
    session.add(new_mod)
    session.commit()

mod_query = session.query(api_resources[modules_table_name]['obj'])
# access=True old modules
for modname in list(set.intersection(modules_db_name, modules_imp_name)):
    for mod_obj in mod_query.filter_by(name=modname):
        mod_obj.access = True
        session.commit()
# acces=False old modules or delite
for modname in list(modules_db_name-modules_imp_name):
    for mod_obj in mod_query.filter_by(name=modname):
        if mod_obj.delete == True:
            session.delete(mod_obj)
        else:
            mod_obj.access = False
        session.commit()


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


def select(table, qdict, username=None):
    max_nesting = qdict.get(nesting_name, config.DefNesting)
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

def insert(table, qdict, username=None):
    tab_obj = table.new_from_json(json.dumps(qdict))
    tab_obj.api_user = username
    tab_obj.api_time = datetime.now()
    session.add(tab_obj)
    session.commit()
    return select(table, qdict)

def update(table, qdict, username=None):
    find_attrs, qdict_attrs = find_prefix_attrs(qdict)
    
    table_query = session.query(table)
    find_list = table_query.filter_by(**find_attrs)
    for tab_obj in find_list:
        tab_obj.update_from_json(json.dumps(qdict_attrs))
        tab_obj.api_user = username
        tab_obj.api_time = datetime.now()
        session.commit()
        
    find_attrs.update(qdict_attrs)
    return select(table, find_attrs)

def delete(table, qdict, username=None):
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

def serialize(query):
    # test resource : 404
    if query['res'] in api_resources:
        resource = api_resources[query['res']]['obj']
        modulename = api_resources[query['res']]['module']
    else:
        return 404, {"error": 
            "Resource '{0}' not found".format(query['res'])
            } 

    # test http method: 405
    if query['req'] in api_resources[query['res']]:
        request = api_requsts[query['req']]
    else:
        return 405, {"error": 
            "HTTP Method '{0}' not Allowed for Resource '{1}'".format(
                query['req'],
                query['res'], ) 
            } 

    # test found user: 403
    table_query = session.query(api_resources[users_table_name]['obj'])
    user_group = False
    for usr_obj in table_query.filter_by(name=query['usr']):
        user_group = usr_obj.group
   
    if user_group: 
        username = query['usr']
    else:
        return 403, {"error": 
            "Forbidden: User '{0}' not found".format(query['usr'])
            }
     
    # test access user group to resource: 403
    permiss_query = session.query(api_resources[modules_permissions_table_name]['obj'])
    permiss_level = config.MinPermiss
    for permiss_obj in permiss_query.filter_by(group=user_group, module=modulename):
        permiss_level = permiss_obj.permission_level
    if query['req'] not in config.AccessMatrix[permiss_level]:
        return 403, {"error": 
            "For User '{0}' forbidden use the Method '{1}' for Resource '{2}'".format(
                query['usr'], 
                query['req'], 
                query['res'], )
            }
    
    # tiny validate 400
    serial_query = query['que']
    validate = api_resources[query['res']][query['req']]
    for key in serial_query:
        if key not in validate:
            return 400, {"error": 
                "Key '{0}' not valid for: '{1}'".format(
                    key,
                    {key: validate[key].__name__ for key in validate}, )
                } 
        if not isinstance(serial_query[key], validate[key]):
            return 400, {"error":
                "For key '{0}' type '{1}' not valid, but expected type: '{2}'".format(
                    key,
                    type(serial_query[key]).__name__,
                    validate[key].__name__, ) 
                }
    
    # start serialization: 200
    return 200, request(resource, serial_query, username)