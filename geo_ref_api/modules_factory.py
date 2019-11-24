import os
import imp

from sqlathanor import declarative_base


########################################################################
class ExceptionDependModule(Exception):
    """
    Exception for depends module
    """

    #----------------------------------------------------------------------
    def __init__(self, text):
        """Constructor"""
        self.text = text


########################################################################
DeclarativeBase = declarative_base()

def get_tables_dict(*args):
    #test depends
    tables_module = [
        my.__module_name__ 
        for my 
        in DeclarativeBase.__subclasses__()
    ]
    for depend in args:
        if depend not in tables_module:
            raise ExceptionDependModule(
                "Depend Module '{}' not found".format(
                    depend, 
                )
            )
    # table dict
    tables_dict = {
        my.__tablename__:my 
        for my 
        in DeclarativeBase.__subclasses__()
    }
    return tables_dict


########################################################################
class ApiModuleConstructor(object):
    """
    Constructor for inhertance class ApiModule
    """
    
    #Reinicializing in your modules:
    #    __module_name__ = "Nmae your module"
    #    __module_depends__ = ["depends1", "depends2"]
    #    __module_doc__ = __doc__
    #    __tables_dict__ = get_tables_dict(*__module_depends__)
    
    __module_name__ = None
    __module_depends__ = []
    __module_doc__ = __doc__
    __tables_dict__ = get_tables_dict(*__module_depends__)

    #----------------------------------------------------------------------
    #def __init__(self, *args, **kwargs):
        #"""Constructor"""
 
    
get_table_cls = lambda module, table_name: module.__tables_dict__[table_name] 