import ast
from sqlathanor import Column, relationship, AttributeConfiguration
from sqlalchemy import (
    Integer,
    ForeignKey,
    Unicode,
    Boolean,
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
from .geo_module import GeoTable

# for Sqlite ForeignKey Event
from sqlalchemy.engine import Engine
try:
    from sqlite3 import Connection as SQLite3Connection
except ImportError:
    SQLite3Connection = type('null_connect', (object, ), {})


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
        AttributeConfiguration(name='layers', supports_json=(False, True)), 
    )

    name = Column(Unicode(256), nullable=False, unique=True)
    properties = Column(JsonType())
    layers = relationship('Layers', cascade='all, delete-orphan')


class Layers(DeclarativeBase, ApiModule):
    """
    Resource Reference of Layers
    """

    __tablename__ = 'layers'

    __serialization__ = get_serialization(
        AttributeConfiguration(name='name', supports_json=True), 
        AttributeConfiguration(name='symbol', supports_json=True), 
        AttributeConfiguration(name='properties', supports_json=True), 
        AttributeConfiguration(name='all_properties', supports_json=(False, True)), 
        AttributeConfiguration(name='geom_id', supports_json=(True, False)), 
    )

    name = Column(Unicode(256), nullable=False, unique=True)
    symbol = Column(Unicode())
    properties = Column(JsonType())
    all_properties = Column(JsonType())
    geom_id = Column(Integer, ForeignKey('geoms.id'), nullable=False)


# Events

# Triggers
def geo_compare(layer_create, mapper, connection, target):
    if target.__tablename__ == 'geoms':
        geom_obj = target
        layer_tab = Layers.__table__
        layer_query = connection.execute(
            layer_tab.select().where(layer_tab.c.geom_id==geom_obj.id)
        )
        layers_obj = []
        for obj in layer_query:
            layers_obj.append(obj)
    elif target.__tablename__ == 'layers':
        layer_obj = target
        geom_tab = Geoms.__table__
        geom_query = connection.execute(
            geom_tab.select().where(geom_tab.c.id==layer_obj.geom_id)
        )
        layers_obj = [layer_obj]
        for obj in geom_query:
            geom_obj = obj

    for layer_obj in layers_obj:
        # create all properties 
        if geom_obj.properties:
            geom_props = ast.literal_eval(geom_obj.properties)
        else:
            geom_props = {}
       
        if layer_obj.properties:
            layer_props = ast.literal_eval(layer_obj.properties)
        else:
            layer_props = {}

        if layer_obj.all_properties:
            all_layer_props = ast.literal_eval(layer_obj.all_properties)
        else:
            all_layer_props = {}
        
        new_all_layer_props = {}
        new_all_layer_props.update(layer_props)
        new_all_layer_props.update(geom_props)
      
        # test update properties 
        if new_all_layer_props != all_layer_props:
            
            if not layer_create:
                # test & alter old layer table
                gt = GeoTable(layer_obj.name)
                out = gt.upate_table(new_all_layer_props)
                if not out[0]:
                    print(out[-1])
                    # find old_properties = all_properties - geom.properties
                    # update propperties to old_properties
                else:
                    # update all_properties for layer
                    layer_tab = Layers.__table__
                    connection.execute(
                        layer_tab.update().
                        values(all_properties=str(new_all_layer_props)).
                        where(layer_tab.c.id==layer_obj.id), 
                    )

        if layer_create:
            # test & create new later table
            gt = GeoTable(layer_obj.name)
            out = gt.create_table(geom_obj.name, new_all_layer_props)
            if not out[0]:
                print(out[-1])
                # delete row for layer_obj.id
        
@listens_for(Layers, 'after_insert')
def ins_layer(*args, **kwargs):
    layer_create = True
    return geo_compare(layer_create, *args, **kwargs)

@listens_for(Geoms, 'after_update')
def upd_geom(*args, **kwargs):
    layer_create = False
    return geo_compare(layer_create, *args, **kwargs)

@listens_for(Layers, 'after_update')
def upd_layer(*args, **kwargs):
    layer_create = False
    return geo_compare(layer_create, *args, **kwargs)

#@listens_for(Layers, 'after_delete')
#def ins_geom(mapper, connection, target):
    #delete or archive geo layer


# for Sqlite ForeignKey Event
@listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()