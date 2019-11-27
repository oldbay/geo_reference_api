import os
import json
import copy
import imp
import importlib
from datetime import datetime


from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import (
    IntegrityError as SqlAlchemyIntegrityError,
)

from . import config
from .modules_factory import ExceptionDepend

import logging
import logging.config
logging.config.dictConfig(config.Logging)
logger = logging.getLogger("serializer")

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
        logger.warning(
            "Broken Depends for Load module '{0}' : '{1}'".format(
                imp_module, 
                err, 
            )
        )
    else:
        load_modules_name.append(imp_module)

# DeclarativeBase is last import
from .modules_factory import DeclarativeBase


########################################################################
class ApiSerializer:
    """
    Serializer API
    """

    nesting_name = 'api_nesting'
    modules_table_name = 'modules'
    users_table_name = 'users'
    #groups_table_name = 'groups'
    modules_permissions_table_name = 'modules_permissions'
    find_prefix = 'api_find_{}'

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        self.api_requsts = {
            "GET": self.select,
            "POST": self.insert,
            "PUT": self.update,
            "DELETE": self.delete,
        }
        
        # create base
        if config.DBPath:
            DBPath = config.DBPath
        else:
            DBPath = 'sqlite:///:memory:'
        self.engine = create_engine(DBPath, echo=config.DBEcho)
        DeclarativeBase.metadata.create_all(self.engine)
        
        self.create_api()
        
        # session
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        
        self.create_modules_tab()
        
        logger.info("Serializer init")

    def create_api(self):
        self.api_resources = {}
        self.api_struct = {}
        for table_class in DeclarativeBase.__subclasses__():
            api_module = table_class.__module_name__
            if api_module not in self.api_struct:
                self.api_struct[api_module] = {
                    "module_depends": table_class.__module_depends__,
                    "module_doc": table_class.__module_doc__,
                }
            res_name = table_class.__tablename__
            self.api_resources[res_name] = {
                "obj": table_class,
                "module": api_module,
                "GET": {},
                "POST": {},
                "PUT": {},
                "DELETE": {},
            }
            self.api_struct[api_module][res_name] = {
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
                        self.api_resources[res_name]['POST'].update({col_name: col_type})
                        self.api_struct[api_module][res_name]['POST'].update(
                            {col_name: col_type.__name__}
                        )
                    if 'PUT' in table_class.__http__:
                        self.api_resources[res_name]['PUT'].update({col_name: col_type})
                        self.api_struct[api_module][res_name]['PUT'].update(
                            {col_name: col_type.__name__}
                        )
                if serial_obj.supports_json[1]:
                    if 'GET' in table_class.__http__:
                        self.api_resources[res_name]['GET'].update({col_name: col_type})
                        self.api_struct[api_module][res_name]['GET'].update(
                            {col_name: col_type.__name__}
                        )
                    if col_type is not dict:
                        if 'PUT' in table_class.__http__:
                            self.api_resources[res_name]['PUT'].update(
                                {self.find_prefix.format(col_name): col_type}
                            )
                            self.api_struct[api_module][res_name]['PUT'].update(
                                {self.find_prefix.format(col_name): col_type.__name__}
                            )
                        if 'DELETE' in table_class.__http__:
                            self.api_resources[res_name]['DELETE'].update(
                                {self.find_prefix.format(col_name): col_type}
                            )
                            self.api_struct[api_module][res_name]['DELETE'].update(
                                {self.find_prefix.format(col_name): col_type.__name__}
                            )
            if 'GET' in table_class.__http__ and self.api_resources[res_name]['GET']:
                self.api_resources[res_name]['GET'].update(
                    {self.nesting_name: int}
                )
                self.api_struct[api_module][res_name]['GET'].update(
                    {self.nesting_name: int.__name__}
                )
            
            table2resource = False
            for http in ['GET', 'POST', 'PUT', 'DELETE']:
                if not self.api_resources[res_name][http]:
                    del(self.api_resources[res_name][http])
                    del(self.api_struct[api_module][res_name][http])
                else:
                    table2resource = True
            
            if not table2resource:
                del(self.api_resources[res_name])
                del(self.api_struct[api_module][res_name])
    
    def create_modules_tab(self):
        modules_query = self.session.query(
            self.api_resources[self.modules_table_name]['obj']
        )
        modules_db_name = set([my.name for my in modules_query.all()])
        modules_imp_name = set([my for my in self.api_struct])
        # add new modules
        for modname in list(modules_imp_name-modules_db_name):
            new_mod = self.api_resources['modules']['obj']()
            new_mod.name = modname
            new_mod.access = True
            new_mod.enable = True
            self.session.add(new_mod)
            self.session.commit()
        
        mod_query = self.session.query(
            self.api_resources[self.modules_table_name]['obj']
        )
        # access=True old modules
        for modname in list(set.intersection(modules_db_name, modules_imp_name)):
            for mod_obj in mod_query.filter_by(name=modname):
                mod_obj.access = True
                self.session.commit()
        # acces=False old modules or delite
        for modname in list(modules_db_name-modules_imp_name):
            for mod_obj in mod_query.filter_by(name=modname):
                if mod_obj.delete == True:
                    self.session.delete(mod_obj)
                else:
                    mod_obj.access = False
                self.session.commit()
        
    def get_api_resources(self):
        return self.api_resources

    def get_api_struct(self):
        return self.api_struct

    def print_api_struct(self):
        print (
            json.dumps(
                self.get_api_struct(),
                sort_keys=True, 
                indent=4,
                separators=(',', ':'), 
                ensure_ascii=False
            )
        )

    def find_prefix_attrs(self, qdict):
        qdict_attrs = copy.deepcopy(qdict)
        find_attrs = {}
        for key in qdict.keys():
            attrs_test = key.split(self.find_prefix.format(''))
            if len(attrs_test) == 2:
                find_attrs[attrs_test[-1]] = qdict[key]
                del(qdict_attrs[key]) 
        find_attrs.update()
        return find_attrs, qdict_attrs
    
    def select(self, table, qdict, username=None):
        max_nesting = qdict.get(self.nesting_name, config.DefNesting)
        if self.nesting_name in qdict.keys(): del(qdict[self.nesting_name])
        
        table_query = self.session.query(table)
        find_list = table_query.filter_by(**qdict)
    
        result = []
        for tab_obj in find_list:
            result.append(
                json.loads(
                    tab_obj.to_json(max_nesting=max_nesting)
                )
            )
        return 200, result
    
    def insert(self, table, qdict, username=None):
        tab_obj = table.new_from_json(json.dumps(qdict))
        tab_obj.api_user = username
        tab_obj.api_time = datetime.now()
        self.session.add(tab_obj)
        try:
            self.session.commit()
        except SqlAlchemyIntegrityError as err:
            self.session.rollback()
            return 409, {"error": str(err)}
        return 201, self.select(table, qdict)[-1]
    
    def update(self, table, qdict, username=None):
        find_attrs, qdict_attrs = self.find_prefix_attrs(qdict)
        
        table_query = self.session.query(table)
        find_list = table_query.filter_by(**find_attrs)
        for tab_obj in find_list:
            tab_obj.update_from_json(json.dumps(qdict_attrs))
            tab_obj.api_user = username
            tab_obj.api_time = datetime.now()
            try:
                self.session.commit()
            except SqlAlchemyIntegrityError as err:
                self.session.rollback()
                return 409, {"error": err}
            
        find_attrs.update(qdict_attrs)
        return 201, self.select(table, find_attrs)[-1]
    
    def delete(self, table, qdict, username=None):
        find_attrs, qdict_attrs = self.find_prefix_attrs(qdict)
        
        table_query = self.session.query(table)
        find_list = table_query.filter_by(**find_attrs)
        for tab_obj in find_list:
            self.session.delete(tab_obj)
            self.session.commit()
            
        return 204, self.select(table, find_attrs)[-1]
    
    
    def serialize(self, query):
        # test resource : 404
        if query['res'] in self.api_resources:
            resource = self.api_resources[query['res']]['obj']
            modulename = self.api_resources[query['res']]['module']
        else:
            return 404, {"error": 
                "Resource '{0}' not found".format(query['res'])
                } 
    
        # test http method: 405
        if query['req'] in self.api_resources[query['res']]:
            request = self.api_requsts[query['req']]
        else:
            return 405, {"error": 
                "HTTP Method '{0}' not Allowed for Resource '{1}'".format(
                    query['req'],
                    query['res'], ) 
                } 
    
        # test found user: 403
        table_query = self.session.query(self.api_resources[self.users_table_name]['obj'])
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
        permiss_query = self.session.query(
            self.api_resources[self.modules_permissions_table_name]['obj']
        )
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
        validate = self.api_resources[query['res']][query['req']]
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
        return request(resource, serial_query, username)