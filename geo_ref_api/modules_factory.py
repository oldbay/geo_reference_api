import os
import imp

from sqlathanor import declarative_base


########################################################################
DeclarativeBase = declarative_base()
get_tables_dict = lambda : {
    my.__tablename__:my 
    for my 
    in DeclarativeBase.__subclasses__()
}

########################################################################
class ApiModuleConstructor(object):
    """
    Constructor for inhertance class ApiModule
    """
    
    #Reinicializing in your modules:
    #    __module_name__ = "Nmae your module"
    #    __module_depends__ = ["depends1", "depends2"]
    #    __module_doc__ = __doc__
    #    __tables_dict__ = get_tables_dict()
    
    __module_name__ = None
    __module_depends__ = []
    __module_doc__ = __doc__
    __tables_dict__ = get_tables_dict()

    #----------------------------------------------------------------------
    #def __init__(self, *args, **kwargs):
        #"""Constructor"""
 
    
get_table_cls = lambda module, table_name: module.__tables_dict__[table_name] 