import os
import imp

from sqlathanor import declarative_base

import constant

api_conf = imp.load_source("conf", os.path.dirname(constant.__file__)+"/service.conf")
DeclarativeBase = declarative_base()
