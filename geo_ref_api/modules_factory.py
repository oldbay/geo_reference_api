import os
import imp

from sqlathanor import declarative_base


########################################################################
class ExceptionDepend(Exception):
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
    """
    Load ApiModule.__module_depends__ & ApiModule.__table_dict__
    and control module depends to error in ExceptionDepend
    """
    
    #test depends
    tables_module = [
        my.__module_name__ 
        for my 
        in DeclarativeBase.__subclasses__()
    ]
    for depend in args:
        if depend not in tables_module:
            raise ExceptionDepend(
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
    return list(args), tables_dict


########################################################################
class ApiModuleConstructor(object):
    """
    Constructor for inhertance class ApiModule
    """
    
    #Reinicializing in your modules:
    #    __module_name__ = "Nmae your module"
    #    __module_doc__ = __doc__
    #    __module_depends__, __tables_dict__ = get_tables_dict(
    #        "depends1", 
    #        "depends2"
    #    )
    
    __module_name__ = None
    __module_doc__ = __doc__
    __module_depends__, __tables_dict__ = get_tables_dict()

 
def get_table_cls (module, table_name):
    """
    Load depends table from ApiModule.__tables_dict__
    and control table depends to error in ExceptionDepend
    """
    
    if table_name in module.__tables_dict__:
        return module.__tables_dict__[table_name]
    else:
        raise ExceptionDepend(
            "Depend Table '{}' not found".format(
                table_name, 
            )
        )