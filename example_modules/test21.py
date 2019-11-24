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
    __module_name__ = 'test21'
    __module_depends__, __tables_dict__ = get_tables_dict(
        'test11',
        'test12', 
    )
    

class Table21(DeclarativeBase, ApiModule):
    """
    test 21 table
    """

    __tablename__ = 'table21'

    __serialization__ = [
        AttributeConfiguration(name='id', supports_json=(False, True)), 
        AttributeConfiguration(name='name', supports_json=True), 
        AttributeConfiguration(name='table11_id', supports_json=(True, False)), 
        AttributeConfiguration(name='table11nams', supports_json=(False, True)), 
        AttributeConfiguration(name='table12_id', supports_json=(True, False)), 
        AttributeConfiguration(name='table12nams', supports_json=(False, True)), 
    ]

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(256), nullable=False, unique=True)

    table11_id = Column(Integer, ForeignKey('table11.id'))
    Table11 = get_table_cls(ApiModule, 'table11')
    Table11.__serialization__.append(
        AttributeConfiguration(name='table21s', supports_json=(False, True)), 
    )
    Table11.table21s = relationship('Table21')
    table11nams = column_property(select([(Table11.name)], table11_id == Table11.id))
    
    table12_id = Column(Integer, ForeignKey('table12.id'))
    Table12 = get_table_cls(ApiModule, 'table12')
    Table12.__serialization__.append(
        AttributeConfiguration(name='table21s', supports_json=(False, True)), 
    )
    Table12.table21s = relationship('Table21')
    table12nams = column_property(select([(Table12.name)], table12_id == Table12.id))