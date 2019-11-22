import os, sys
import imp
import importlib
import types

#sqlalchemy database path (if default to false)
DBPath = False
#sqlalcemy echo SQL query
DBEcho = True
#Default Group permission for Module
DefPermiss = 1


# raplace default from config file
if "GEO_REF_API_CONF" in os.environ:
    conf_name = os.path.realpath(os.environ["GEO_REF_API_CONF"])
    if os.path.basename(conf_name) in os.listdir(os.path.dirname(conf_name)):
        module_dirname = os.path.dirname(conf_name)
        module_name = os.path.basename(conf_name).split(".")[0]
        sys.path.append(module_dirname)
        try:
            conf = importlib.import_module(module_name)
        except ImportError:
            conf = imp.load_source("conf", conf_name)

        # find variables
        for var in list(locals().keys()):
            if type(locals()[var]) != types.ModuleType and var[:1] != "_":
                if var in conf.__dict__:
                    if isinstance(locals()[var], dict):
                        locals()[var][key].update(conf.__dict__[var])
                    else:
                        locals()[var] = conf.__dict__[var]
