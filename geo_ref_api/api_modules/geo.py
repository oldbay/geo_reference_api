from sqlathanor import Column, relationship, AttributeConfiguration

from sqlalchemy import (
    Integer,
    ForeignKey,
    Unicode,
    Boolean,
    Binary, 
)
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
from geo_ref_api.custom_types import JsonType


class ApiModule(ApiModuleConstructor):
    """
    Module Geo
    """
    
    __module_name__ = 'geo'
    __module_doc__ = __doc__
    __module_depends__, __tables_dict__ = get_tables_dict()


class Geoms(DeclarativeBase, ApiModule):
    """
    Resource Reference of Geoms
    """

    __tablename__ = 'geoms'

    __serialization__ = get_serialization(
        AttributeConfiguration(name='name', supports_json=True), 
        AttributeConfiguration(name='properties', supports_json=True), 
    )

    name = Column(Unicode(256), nullable=False, unique=True)
    properties = Column(JsonType())


class Layers(DeclarativeBase, ApiModule):
    """
    Resource Reference of Layers
    """

    __tablename__ = 'layers'

    __serialization__ = get_serialization(
        AttributeConfiguration(name='name', supports_json=True), 
        AttributeConfiguration(name='symbol', supports_json=True), 
        AttributeConfiguration(name='properties', supports_json=True), 
    )

    name = Column(Unicode(256), nullable=False, unique=True)
    symbol = Column(Binary())
    properties = Column(JsonType())
