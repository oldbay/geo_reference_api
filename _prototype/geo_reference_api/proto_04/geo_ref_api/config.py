import os, sys
import imp
import importlib
import types

#sqlalchemy database path (if default to false)
DBPath = False

#sqlalcemy echo SQL query
DBEcho = True

#Group permission for Module
AccessMatrix = {
    0: [],
    1: ['GET'],
    2: ['GET', 'PUT'],
    3: ['GET', 'POST', 'PUT', 'DELETE'],
}
MinPermiss = 0
DefPermiss = 1
MaxPermiss = 3

#Base Users
BaseAdminUser = 'admin'
BaseAdminGroup = 'admins'

#Load modules
ApiModules = []

#Query options
DefNesting = 2


# raplace default from config file
if "GEO_REF_API_CONF" in os.environ:
    conf_name = os.path.realpath(os.environ["GEO_REF_API_CONF"])
    if os.path.isfile(conf_name):
        conf = imp.load_source("conf", conf_name)
    else:
        conf = importlib.import_module(conf_name)

    # find variables
    for var in list(locals().keys()):
        if type(locals()[var]) != types.ModuleType and var[:1] != "_":
            if var in conf.__dict__:
                if isinstance(locals()[var], dict):
                    locals()[var][key].update(conf.__dict__[var])
                else:
                    locals()[var] = conf.__dict__[var]
