import os
import imp
import constant

from sqlathanor import declarative_base, Column, relationship

from sqlalchemy import create_engine
from sqlalchemy import Integer, ForeignKey, Unicode, PickleType, DateTime, Boolean

conf = imp.load_source("conf", os.path.dirname(constant.__file__)+"/service.conf")

if conf.DBPath:
    DBPath = conf.DBPath
else:
    DBPath = 'sqlite:///'+os.path.dirname(constant.__file__)+'/db/data.sqlite'

DeclarativeBase = declarative_base()


class User(DeclarativeBase):

    """ user """

    __tablename__ = 'user'
    
    id = Column(
        Integer, 
        primary_key=True, 
        autoincrement=True, 
        supports_dict=True, 
    )
    name = Column(
        Unicode(256), 
        nullable=False, 
        unique=True, 
        supports_dict=True, 
    )
    key = Column(
        Unicode(512), 
        supports_dict=True, 
    )
    group_id = Column(
        Integer, 
        ForeignKey('group.id'), 
        #nullable=False, 
        supports_dict=True, 
    )


class Group(DeclarativeBase):

    """ group """

    __tablename__ = 'group'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(256), nullable=False, unique=True)
    users = relationship('User')


class Module(DeclarativeBase):

    """ group """

    __tablename__ = 'module'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(256), nullable=False, unique=True)

engine = create_engine(DBPath, echo=conf.DBEcho)
DeclarativeBase.metadata.create_all(engine)
