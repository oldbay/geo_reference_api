from sqlathanor import Column, relationship, AttributeConfiguration

from sqlalchemy import Integer, ForeignKey, Unicode

from geo_ref_api import DeclarativeBase, ApiModuleConstructor, get_tables_dict, config

class ApiModule(ApiModuleConstructor):
    __module_name__ = 'test01'
    __module_depends__ = []
    __tables_dict__ = get_tables_dict()
    

class Table01(DeclarativeBase, ApiModule):
    """
    test 01 table
    """

    __tablename__ = 'table01'

    __serialization__ = [
        AttributeConfiguration(name='id', supports_json=(False, True)), 
        AttributeConfiguration(name='name', supports_json=True), 
    ]

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(256), nullable=False, unique=True)
