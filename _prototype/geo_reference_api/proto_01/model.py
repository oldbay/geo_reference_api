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


class Users(DeclarativeBase):

    """ user """

    __tablename__ = 'users'
    
    __serialization__ = [
        AttributeConfiguration(name='id', supports_json=True), 
        AttributeConfiguration(name='name', supports_json=True), 
        AttributeConfiguration(name='key', supports_json=(True, False)), 
        AttributeConfiguration(name='group_id', supports_json=(True, False)), 
        #AttributeConfiguration(name='group', supports_json=(False, True)), 
        AttributeConfiguration(name='group_name', supports_json=(False, True)), 
    ]
    
    id = Column(Integer, primary_key=True,)
    name = Column(Unicode(256), nullable=False, unique=True,)
    key = Column(Unicode(512),)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False,)
    group = relationship('Groups', back_populates='users',)
    #group_name = column_property(select([(Groups.name)], group_id == Groups.id))


class Modules(DeclarativeBase):

    """ group """

    __tablename__ = 'modules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(256), nullable=False, unique=True)


Users.group_name = column_property(select([(Groups.name)], Users.group_id == Groups.id))



engine = create_engine(DBPath, echo=conf.DBEcho)
DeclarativeBase.metadata.create_all(engine)
