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


class Users(DeclarativeBase):

    """ user """

    __tablename__ = 'users'
    
    id = Column(
        Integer, 
        primary_key=True, 
        supports_json=True, 
    )
    name = Column(
        Unicode(256), 
        nullable=False, 
        unique=True, 
        supports_json=True, 
    )
    key = Column(
        Unicode(512), 
        supports_json=True, 
    )
    group_id = Column(
        Integer, 
        ForeignKey('groups.id'), 
        #nullable=False, 
        supports_json=True, 
    )
    group = relationship(
        'Groups',
        back_populates='users', 
        supports_json=True, 
    )


class Groups(DeclarativeBase):

    """ group """

    __tablename__ = 'groups'

    id = Column(
        Integer,
        primary_key=True, 
        supports_json=True, 
    )
    name = Column(
        Unicode(256),
        nullable=False,
        unique=True, 
        supports_json=True, 
    )
    users = relationship(
        'Users',
        back_populates='group', 
        #backref='group', 
        supports_json=True, 
    )


class Modules(DeclarativeBase):

    """ group """

    __tablename__ = 'modules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(256), nullable=False, unique=True)

engine = create_engine(DBPath, echo=conf.DBEcho)
DeclarativeBase.metadata.create_all(engine)
