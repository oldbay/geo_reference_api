import os
import json
import copy
import imp
import importlib
from datetime import datetime

import copy

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
    res_struct = {
        "GET": {
            "filter": {},
            "data": {},
        },
        "POST": {
            "filter": {},
            "data": {},
        },
        "PUT": {
            "filter": {},
            "data": {},
        },
        "DELETE": {
            "filter": {},
            "data": {},
        },
    }

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
        self.api_resources_sruct = {}
        self.api_modules_struct = {}
        for table_class in DeclarativeBase.__subclasses__():
            api_module = table_class.__module_name__
            if api_module not in self.api_modules_struct:
                self.api_modules_struct[api_module] = {
                    "module_depends": table_class.__module_depends__,
                    "module_doc": table_class.__module_doc__,
                    "resources": {},
                }
            res_name = table_class.__tablename__
            self.api_resources[res_name] = {
                "obj": table_class,
                "module": api_module,
            }
            self.api_resources[res_name].update(
                copy.deepcopy(self.res_struct)
            )
            self.api_resources_sruct[res_name] = {}
            self.api_resources_sruct[res_name].update(
                copy.deepcopy(self.res_struct)
            )
            self.api_modules_struct[api_module]['resources'][res_name] = {
                "resource_doc": table_class.__doc__,
            }
            
            for serial_obj in table_class.__serialization__:
                col_name = serial_obj.name
                try:
                    col_type = table_class.__dict__[col_name].type.python_type
                except AttributeError:
                    col_type = None
        
                if serial_obj.supports_json[0]:
                    for http in ['POST', 'PUT']:
                        if http in table_class.__http__:
                            self.api_resources[res_name][http]['data'].update(
                                {col_name: col_type}
                            )
                            self.api_resources_sruct[res_name][http]['data'].update(
                                {col_name: col_type.__name__}
                            )
                if serial_obj.supports_json[1]:
                    if col_type:
                        for http in ['GET', 'PUT', 'DELETE']:
                            if http in table_class.__http__:
                                self.api_resources[res_name][http]['filter'].update(
                                    {col_name: col_type}
                                )
                                self.api_resources_sruct[res_name][http]['filter'].update(
                                    {col_name: col_type.__name__}
                                )
                                if http == 'GET':
                                    self.api_resources[res_name][http]['filter'].update(
                                        {self.nesting_name: int}
                                    )
                                    self.api_resources_sruct[res_name][http]['filter'].update(
                                        {self.nesting_name: int.__name__}
                                    )
            # clean  
            table2resource = False
            for http in ['GET', 'POST', 'PUT', 'DELETE']:
                for met in ['data', 'filter']:
                    if not self.api_resources[res_name][http][met]:
                        del(self.api_resources[res_name][http][met])
                        del(self.api_resources_sruct[res_name][http][met])
                
                if not self.api_resources[res_name][http]:
                    del(self.api_resources[res_name][http])
                    del(self.api_resources_sruct[res_name][http])
                elif http == 'PUT' and len(self.api_resources[res_name][http]) < 2:
                    del(self.api_resources[res_name][http])
                    del(self.api_resources_sruct[res_name][http])
                else:
                    table2resource = True
            
            if not table2resource:
                del(self.api_resources[res_name])
                del(self.api_resources_sruct[res_name])
                del(self.api_modules_struct[api_module]['resources'][res_name])
    
    def create_modules_tab(self):
        modules_query = self.session.query(
            self.api_resources[self.modules_table_name]['obj']
        )
        modules_db_name = set([my.name for my in modules_query.all()])
        modules_imp_name = set([my for my in self.api_modules_struct])
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

    def get_api_resources_struct(self):
        return self.api_resources_sruct

    def print_api_resources_struct(self):
        print (
            json.dumps(
                self.get_api_resources_struct(),
                sort_keys=True, 
                indent=4,
                separators=(',', ':'), 
                ensure_ascii=False
            )
        )

    def get_api_modules_struct(self):
        return self.api_modules_struct

    def print_api_modules_struct(self):
        print (
            json.dumps(
                self.get_api_modules_struct(),
                sort_keys=True, 
                indent=4,
                separators=(',', ':'), 
                ensure_ascii=False
            )
        )

    def select(self, table, qdict, username=None):
        if not qdict:
            api_filter = {}
        else:
            #400
            api_filter = qdict['filter']
        max_nesting = api_filter.get(self.nesting_name, config.DefNesting)
        if self.nesting_name in api_filter.keys(): del(api_filter[self.nesting_name])
        
        table_query = self.session.query(table)
        find_list = table_query.filter_by(**api_filter)
    
        result = []
        for tab_obj in find_list:
            result.append(
                json.loads(
                    tab_obj.to_json(max_nesting=max_nesting)
                )
            )
        return 200, result
    
    def insert(self, table, qdict, username=None):
        # 400
        api_filter = qdict['data']
        
        tab_obj = table.new_from_json(json.dumps(api_filter))
        tab_obj.api_user = username
        tab_obj.api_time = datetime.now()
        self.session.add(tab_obj)
        try:
            self.session.commit()
        except SqlAlchemyIntegrityError as err:
            self.session.rollback()
            return 409, {"error": str(err)}
        return 201, self.select(table, {"filter": api_filter})[-1]
    
    def update(self, table, qdict, username=None):
        # 400 
        api_filter = qdict['filter']
        api_data = qdict['data']
        
        table_query = self.session.query(table)
        find_list = table_query.filter_by(**api_filter)
        for tab_obj in find_list:
            tab_obj.update_from_json(json.dumps(api_data))
            tab_obj.api_user = username
            tab_obj.api_time = datetime.now()
            try:
                self.session.commit()
            except SqlAlchemyIntegrityError as err:
                self.session.rollback()
                return 409, {"error": err}
        
        # different keys data to filter (update only different keys)!!!!!    
        api_filter.update(api_data)
        return 201, self.select(table, {"filter": api_filter})[-1]
    
    def delete(self, table, qdict, username=None):
        #400
        api_filter = qdict['filter']
        
        table_query = self.session.query(table)
        find_list = table_query.filter_by(**api_filter)
        for tab_obj in find_list:
            self.session.delete(tab_obj)
            self.session.commit()
            
        post_del = self.select(table, {"filter": api_filter})[-1]
        if not post_del:
            return 204, []
        else:
            return 409, {"error":
                "Delete date is not empty: {}".format(str(post_del))
            }
    
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
                "For User '{0}' forbidden use HTTP:'{1}' for Resource '{2}'".format(
                    query['usr'], 
                    query['req'], 
                    query['res'], )
                }
        
        # tiny validate 400
        for met in query['que'].keys():
            serial_query = query['que'][met]
            if met not in self.api_resources[query['res']][query['req']]:
                return 400, {"error": 
                    "Method '{0}' not valid for '{1}':'{2}'".format(
                        met, 
                        query['req'],
                        query['res'], ) 
                    }
            else:
                validate = self.api_resources[query['res']][query['req']][met]
            for key in serial_query:
                if key not in validate:
                    return 400, {"error": 
                        "Key '{0}[{1}]' not valid for: '{2}'".format(
                            met, 
                            key,
                            {key: validate[key].__name__ for key in validate}, )
                        } 
                if not isinstance(serial_query[key], validate[key]):
                    return 400, {"error":
                        "For key '{0}[{1}]' type '{2}' not valid, expected: '{3}'".format(
                            met, 
                            key,
                            type(serial_query[key]).__name__,
                            validate[key].__name__, ) 
                        }
        
        # start serialization: 200
        return request(resource, query['que'], username)