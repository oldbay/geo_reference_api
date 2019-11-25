from sqlathanor import Column, relationship, AttributeConfiguration

from sqlalchemy import Integer, ForeignKey, Unicode, PickleType, DateTime, Boolean
from sqlalchemy.orm import column_property
from sqlalchemy import select
from sqlalchemy.event import listens_for

from geo_ref_api import DeclarativeBase, ApiModuleConstructor, get_tables_dict, config

class ApiModule(ApiModuleConstructor):
    """
    Базовый модуль
    """
    
    __module_name__ = 'base'
    __module_doc__ = __doc__
    __module_depends__, __tables_dict__ = get_tables_dict()
   

class Groups(DeclarativeBase, ApiModule):
    """
    Ресурс групп
    """

    __tablename__ = 'groups'

    __serialization__ = [
        AttributeConfiguration(name='id', supports_json=(False, True)), 
        AttributeConfiguration(name='name', supports_json=True), 
        AttributeConfiguration(name='users', supports_json=(False, True)), 
        AttributeConfiguration(name='modules', supports_json=(False, True)), 
    ]

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(256), nullable=False, unique=True)
    users = relationship('Users', cascade='all, delete-orphan')
    modules = relationship('ModulesPermissions', cascade='all, delete-orphan')


class Users(DeclarativeBase, ApiModule):
    """
    Ресурс пользователей
    """

    __tablename__ = 'users'
    
    __serialization__ = [
        AttributeConfiguration(name='id', supports_json=(False, True)), 
        AttributeConfiguration(name='name', supports_json=True), 
        AttributeConfiguration(name='key', supports_json=(True, False)), 
        AttributeConfiguration(name='group_id', supports_json=(True, False)), 
        AttributeConfiguration(name='group', supports_json=(False, True)), 
    ]
    
    id = Column(Integer, primary_key=True,)
    name = Column(Unicode(256), nullable=False, unique=True)
    key = Column(Unicode(512))
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    group = column_property(select([(Groups.name)], group_id == Groups.id))


class Modules(DeclarativeBase, ApiModule):

    __tablename__ = 'modules'

    __serialization__ = [
        AttributeConfiguration(name='id', supports_json=(False, True)), 
        AttributeConfiguration(name='name', supports_json=(False, True)), 
        AttributeConfiguration(name='access', supports_json=(False, True)), 
        AttributeConfiguration(name='enable', supports_json=True), 
        AttributeConfiguration(name='groups', supports_json=(False, True)), 
    ]

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(256), nullable=False, unique=True)
    access = Column(Boolean, default=False)
    enable = Column(Boolean, default=True)
    groups = relationship('ModulesPermissions', cascade='all, delete-orphan')


class ModulesPermissions(DeclarativeBase, ApiModule):

    __tablename__ = 'modules_permissions'

    __serialization__ = [
        AttributeConfiguration(name='id', supports_json=(False, True)), 
        AttributeConfiguration(name='permission_level', supports_json=True), 
        AttributeConfiguration(name='group_id', supports_json=False), 
        AttributeConfiguration(name='module_id', supports_json=False), 
        AttributeConfiguration(name='group', supports_json=(False, True)), 
        AttributeConfiguration(name='module', supports_json=(False, True)), 
    ]

    id = Column(Integer, primary_key=True)
    permission_level = Column(Integer, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=False)
    group = column_property(select([(Groups.name)], group_id == Groups.id))
    module = column_property(select([(Modules.name)], module_id == Modules.id))

    
# Events

@listens_for(Modules, 'after_insert')
def insert_groups_permissions(mapper, connection, target):
    group_tab = Groups.__table__
    group_query = connection.execute(
        group_tab.select()
    )
    module_permissions_tab = ModulesPermissions.__table__
    module_id = target.id
    for group in group_query:
        connection.execute(
            module_permissions_tab.insert(), 
            permission_level=config.DefPermiss, 
            group_id=group['id'], 
            module_id=module_id
        )

@listens_for(Groups, 'after_insert')
def insert_modules_permissions(mapper, connection, target):
    module_tab = Modules.__table__
    module_query = connection.execute(
        module_tab.select()
    )
    module_permissions_tab = ModulesPermissions.__table__
    group_id = target.id
    for module in module_query:
        connection.execute(
            module_permissions_tab.insert(), 
            permission_level=config.DefPermiss, 
            group_id=group_id, 
            module_id=module['id']
        )
