import os
import imp
import constant

from sqlathanor import declarative_base, Column, relationship, AttributeConfiguration

from sqlalchemy import create_engine
from sqlalchemy import Integer, ForeignKey, Unicode, PickleType, DateTime, Boolean

from sqlalchemy.orm import column_property
from sqlalchemy import select

conf = imp.load_source("conf", os.path.dirname(constant.__file__)+"/service.conf")

if conf.DBPath:
    DBPath = conf.DBPath
else:
    DBPath = 'sqlite:///'+os.path.dirname(constant.__file__)+'/db/data.sqlite'

DeclarativeBase = declarative_base()


class Users(DeclarativeBase):

    __tablename__ = 'users'
    
    __serialization__ = [
        AttributeConfiguration(name='id', supports_json=True), 
        AttributeConfiguration(name='name', supports_json=True), 
        AttributeConfiguration(name='key', supports_json=(True, False)), 
        AttributeConfiguration(name='group_id', supports_json=(True, False)), 
    ]
    
    id = Column(Integer, primary_key=True,)
    name = Column(Unicode(256), nullable=False, unique=True)
    key = Column(Unicode(512))
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)


class Groups(DeclarativeBase):

    __tablename__ = 'groups'

    __serialization__ = [
        AttributeConfiguration(name='id', supports_json=True), 
        AttributeConfiguration(name='name', supports_json=True), 
        AttributeConfiguration(name='users', supports_json=(False, True)), 
        AttributeConfiguration(name='modules', supports_json=(False, True)), 
    ]

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(256), nullable=False, unique=True)
    users = relationship('Users')
    modules = relationship('ModulesPermissions')


class Modules(DeclarativeBase):

    __tablename__ = 'modules'

    __serialization__ = [
        AttributeConfiguration(name='id', supports_json=True), 
        AttributeConfiguration(name='name', supports_json=True), 
        AttributeConfiguration(name='groups', supports_json=(False, True)), 
    ]

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(256), nullable=False, unique=True)
    groups = relationship('ModulesPermissions')


class ModulesPermissions(DeclarativeBase):

    __tablename__ = 'modules_permissions'

    __serialization__ = [
        AttributeConfiguration(name='id', supports_json=True), 
        AttributeConfiguration(name='permission_level', supports_json=True), 
        AttributeConfiguration(name='group_id', supports_json=(True, False)), 
        AttributeConfiguration(name='module_id', supports_json=(True, False)), 
        AttributeConfiguration(name='group', supports_json=(False, True)), 
        AttributeConfiguration(name='module', supports_json=(False, True)), 
    ]

    id = Column(Integer, primary_key=True)
    permission_level = Column(Integer, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=False)
    group = column_property(select([(Groups.name)], group_id == Groups.id))
    module = column_property(select([(Modules.name)], module_id == Modules.id))


# calculating columns

#User
Users.group = column_property(
    select([(Groups.name)], Users.group_id == Groups.id)
)
Users.__serialization__.append(
    AttributeConfiguration(name='group', supports_json=(False, True))
)

engine = create_engine(DBPath, echo=conf.DBEcho)
DeclarativeBase.metadata.create_all(engine)
