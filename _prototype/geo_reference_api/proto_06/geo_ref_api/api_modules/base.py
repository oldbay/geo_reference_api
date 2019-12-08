from sqlathanor import Column, relationship, AttributeConfiguration

from sqlalchemy import Integer, ForeignKey, Unicode, PickleType, DateTime, Boolean
from sqlalchemy.orm import column_property
from sqlalchemy import select
from sqlalchemy.event import listens_for

from geo_ref_api import (
    DeclarativeBase,
    ApiModuleConstructor, 
    get_tables_dict,
    get_serialization, 
    get_table_cls, 
    config, 
)

class ApiModule(ApiModuleConstructor):
    """
    Module Base
    """
    
    __module_name__ = 'base'
    __module_doc__ = __doc__
    __module_depends__, __tables_dict__ = get_tables_dict()
   

class Groups(DeclarativeBase, ApiModule):
    """
    Resource Groups
    """

    __tablename__ = 'groups'

    __serialization__ = get_serialization(
        AttributeConfiguration(name='name', supports_json=True), 
        AttributeConfiguration(name='users', supports_json=(False, True)), 
        AttributeConfiguration(name='modules', supports_json=(False, True)), 
    )

    name = Column(Unicode(256), nullable=False, unique=True)
    users = relationship('Users', cascade='all, delete-orphan')
    modules = relationship('ModulesPermissions', cascade='all, delete-orphan')


class Users(DeclarativeBase, ApiModule):
    """
    Resource Users
    """

    __tablename__ = 'users'
    
    __serialization__ = get_serialization(
        AttributeConfiguration(name='name', supports_json=True), 
        AttributeConfiguration(name='key', supports_json=(True, False)), 
        AttributeConfiguration(name='group_id', supports_json=(True, False)), 
        AttributeConfiguration(name='group', supports_json=(False, True)), 
    )
    
    name = Column(Unicode(256), nullable=False, unique=True)
    key = Column(Unicode(512))
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    group = column_property(select([(Groups.name)], group_id == Groups.id))


class Modules(DeclarativeBase, ApiModule):
    """
    Resource Modules
    """

    __tablename__ = 'modules'
    
    __http__ = ['GET', 'PUT']

    __serialization__ = get_serialization(
        AttributeConfiguration(name='name', supports_json=(False, True)), 
        AttributeConfiguration(name='access', supports_json=(False, True)), 
        AttributeConfiguration(name='enable', supports_json=True), 
        AttributeConfiguration(name='delete', supports_json=True), 
        AttributeConfiguration(name='groups', supports_json=(False, True)), 
    )

    name = Column(Unicode(256), nullable=False, unique=True)
    access = Column(Boolean, default=False)
    enable = Column(Boolean, default=True)
    delete = Column(Boolean, default=False)
    groups = relationship('ModulesPermissions', cascade='all, delete-orphan')


class ModulesPermissions(DeclarativeBase, ApiModule):
    """
    Resource Modules Permissions
    """

    __tablename__ = 'modules_permissions'

    __http__ = ['GET', 'PUT']

    __serialization__ = get_serialization(
        AttributeConfiguration(name='permission_level', supports_json=True), 
        AttributeConfiguration(name='group_id', supports_json=False), 
        AttributeConfiguration(name='module_id', supports_json=False), 
        AttributeConfiguration(name='group', supports_json=(False, True)), 
        AttributeConfiguration(name='module', supports_json=(False, True)), 
    )

    permission_level = Column(Integer, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=False)
    group = column_property(select([(Groups.name)], group_id == Groups.id))
    module = column_property(select([(Modules.name)], module_id == Modules.id))

    
# Events

# Create initial Data
@listens_for(Groups.__table__, 'after_create')
def insert_def_group(target, connection, **kw):
    connection.execute(
        target.insert(), 
        name=config.BaseAdminGroup, 
    )

@listens_for(Users.__table__, 'after_create')
def insert_def_user(target, connection, **kw):
    group_tab = Groups.__table__
    group_query = connection.execute(
        group_tab.select().where(group_tab.c.name==config.BaseAdminGroup)
    )
    connection.execute(
        target.insert(), 
        name=config.BaseAdminUser,
        group_id=list(group_query)[0]['id']
    )
    
@listens_for(Modules.__table__, 'after_create')
def insert_def_group(target, connection, **kw):
    connection.execute(
        target.insert(), 
        name=ApiModule.__module_name__,
        #access=True, 
    )

@listens_for(ModulesPermissions.__table__, 'after_create')
def insert_def_groups_permissions(target, connection, **kw):
    group_tab = Groups.__table__
    group_query = connection.execute(
        group_tab.select().where(group_tab.c.name==config.BaseAdminGroup)
    )
    module_tab = Modules.__table__
    module_query = connection.execute(
        module_tab.select().where(module_tab.c.name==ApiModule.__module_name__)
    )
    for group in group_query:
        for module in module_query:
            connection.execute(
                target.insert(), 
                permission_level=config.MaxPermiss, 
                group_id=group['id'], 
                module_id=module['id'], 
            )


#Triggers
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
