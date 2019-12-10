import os, sys
import json

conf_dict = {
    #sqlalchemy database path
    #"DBPath": 'sqlite:///:memory:', #only serialize test, flask app is not worked 
    "DBPath": 'sqlite:///db.sqlite', 
    #sqlalcemy echo SQL query
    "DBEcho": True,
    #Group permission for Module
    "AccessMatrix": { 
        0: [],
        1: ["GET"],
        2: ["GET", "PUT"],
        3: ["GET", "POST", "PUT", "DELETE"],
    }, 
    "MinPermiss": 0, 
    "DefPermiss": 1, 
    "MaxPermiss": 3,
    #Base Users
    "BaseAdminUser": "admin", 
    "BaseAdminAuthUser": "sysadmin", 
    "BaseAdminGroup": "admins",
    "BaseAdminAuthGroup": "sysadmins",
    #Load API modules, example:
    #"ApiModules": [
        #"example_modules.test01", 
        #"example_modules.test11", 
        #"example_modules.test12", 
        #"example_modules/test21.py"
    #]
    "ApiModules": [],
    #Load Auth module
    "AuthModule":{
        "module": "geo_ref_api.auth_modules.ssh",
        "args": {
            "url": "127.0.0.1",
            "port": 22,
        },
    }, 
    # JWT params
    "JwtUserKey": "username",
    "JwtSecretKey": "secret",
    "JwtAlgo": "HS256",
    # Time of live JWT ticket in seconds(to future)
    #"JwtTimeout": 600,
    "JwtTimeout": None,
    #Query options
    "DefNesting": 2,
    # Defaults names for API Serializer(not cange!)
    "ApiSerialDefaults": {
        "nesting_name": "api_nesting", 
        "modules_table_name": "modules", 
        "users_table_name": "users", 
        "users_groups_table_name": "users_groups", 
        "groups_table_name": "groups", 
        "modules_permissions_table_name": "modules_permissions", 
    },
    # Logging config
    "Logging": {
        "version":1,
        "handlers":{
            "file":{
                "class":"logging.FileHandler",
                "formatter":"simple",
                "filename":"api.log", 
            }, 
            "console":{
                "class":"logging.StreamHandler",
                "formatter":"simple",
                "stream": "ext://sys.stdout", 
            }
        },
        "loggers":{
            "serializer":{
                "handlers":["console"],
                "level":"INFO",
            }, 
            "rest_api":{
                "handlers":["console"],
                "level":"INFO",
            }, 
            "auth_processing":{
                "handlers":["console"],
                "level":"INFO",
            }
        },
        "formatters":{
            "simple":{
                "format":"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }        
    },
}

# raplace default from config file
if "GEO_REF_API_CONF" in os.environ:
    conf_name = os.path.realpath(os.environ["GEO_REF_API_CONF"])
    if os.path.isfile(conf_name):
        with open(conf_name) as file_: 
            json_conf = json.load(file_)
        conf_dict.update(json_conf)
    
for var in conf_dict:
    locals()[var] = conf_dict[var]