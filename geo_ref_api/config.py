import os, sys
import json

conf_dict = {
    #sqlalchemy database path (if default to false)
    "DBPath": False, 
    #sqlalcemy echo SQL query
    "DBEcho": True,
    #Group permission for Module
    "AccessMatrix": { 
        0: [],
        1: ['GET'],
        2: ['GET', 'PUT'],
        3: ['GET', 'POST', 'PUT', 'DELETE'],
    }, 
    "MinPermiss": 0, 
    "DefPermiss": 1, 
    "MaxPermiss": 3,
    #Base Users
    "BaseAdminUser": "admin", 
    "BaseAdminGroup": "admins",
    #Load modules
    "ApiModules": [],
    #Query options
    "DefNesting": 2,
    # API authentication
    "AuthSecretKey": "secret",
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