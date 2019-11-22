from sqlathanor import Column, relationship, AttributeConfiguration

from sqlalchemy import Integer, ForeignKey, Unicode
from sqlalchemy.orm import column_property
from sqlalchemy import select

from geo_ref_api import (
    DeclarativeBase, 
    ApiModuleConstructor, 
    get_tables_dict, 
    get_table_cls, 
    config
)

class ApiModule(ApiModuleConstructor):
    __module_name__ = 'test11'
    __module_depends__ = ['test01']
    __tables_dict__ = get_tables_dict()
    

class Table11(DeclarativeBase, ApiModule):
    """
    test 11 table
    """

    __tablename__ = 'table11'

    __serialization__ = [
        AttributeConfiguration(name='id', supports_json=(False, True)), 
        AttributeConfiguration(name='name', supports_json=True), 
        AttributeConfiguration(name='table01_id', supports_json=(True, False)), 
        AttributeConfiguration(name='table01nams', supports_json=(False, True)), 
    ]

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(256), nullable=False, unique=True)
    table01_id = Column(Integer, ForeignKey('table01.id'))
    
    Table01 = get_table_cls(ApiModule, 'table01')
    #Table01.__serialization__.append(
        #AttributeConfiguration(name='table11s', supports_json=(False, True)), 
    #)
    #Table01.table11s = relationship('table11')
    table01nams = column_property(select([(Table01.name)], table01_id == Table01.id))
