# -*- coding: utf-8 -*-

"""
***********************************
tests._fixtures
***********************************

Fixtures used by the SQLAthanor test suite.

"""
import os
import sqlite3
import datetime

import pytest

from sqlathanor import BaseModel as Base
from sqlathanor import Column, relationship, AttributeConfiguration

from sqlalchemy import Integer, String, Interval, ForeignKey, create_engine, MetaData, Table
from sqlalchemy.orm import clear_mappers, Session, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects import sqlite

from flask import Flask

from validator_collection import validators, checkers

class State(object):
    """Class to hold incremental test state."""
    # pylint: disable=too-few-public-methods
    pass


def return_serialized(value):
    return "serialized"

def return_deserialized(value):
    return "deserialized"

@pytest.fixture
def flask_app(request):
    app = Flask("test_flask_app")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

    return app

@pytest.fixture
def state(request):
    """Return the :class:`State` object that holds incremental test state."""
    # pylint: disable=W0108
    return request.cached_setup(
        setup = lambda: State(),
        scope = "session"
    )

@pytest.fixture(scope = "session")
def db_engine(request):
    engine = create_engine('sqlite://')

    return engine

@pytest.yield_fixture(scope = 'session')
def tables(request, db_engine):
    BaseModel = declarative_base(cls = Base, metadata = MetaData())

    class User(BaseModel):
        """Mocked class with a single primary key."""

        __tablename__ = 'users'

        id = Column('id',
                    Integer,
                    primary_key = True)
        name = Column('username',
                      String(50))
        addresses = relationship('Address', backref = 'user')

        _hybrid = 1

        @hybrid_property
        def hybrid(self):
            return self._hybrid

        @hybrid.setter
        def hybrid(self, value):
            self._hybrid = value

        @hybrid_property
        def hybrid_differentiated(self):
            return self._hybrid

        @hybrid_differentiated.setter
        def hybrid_differentiated(self, value):
            self._hybrid = value

        keywords_basic = association_proxy('keywords_basic', 'keyword')

    class Address(BaseModel):
        """Mocked class with a single primary key."""

        __tablename__ = 'addresses'

        id = Column('id',
                    Integer,
                    primary_key = True)
        email = Column('email_address',
                       String(50))
        user_id = Column('user_id',
                         Integer,
                         ForeignKey('users.id'))

    class User2(BaseModel):
        """Mocked class with a single primary key."""

        __tablename__ = 'users_composite'

        id = Column('id',
                    Integer,
                    primary_key = True)
        id2 = Column('id2',
                     Integer,
                     primary_key = True)
        id3 = Column('id3',
                     Integer,
                     primary_key = True)
        name = Column('username',
                      String(50))
        addresses = relationship('Address2', backref = 'user')

        _hybrid = 1
        @hybrid_property
        def hybrid(self):
            return self._hybrid

        @hybrid_property
        def hybrid_differentiated(self):
            return self._hybrid

    class Address2(BaseModel):
        """Mocked class with a single primary key."""

        __tablename__ = 'addresses_composite'

        id = Column('id',
                    Integer,
                    primary_key = True)
        email = Column('email_address',
                       String(50))
        user_id = Column('user_id',
                         Integer,
                         ForeignKey('users_composite.id'))

    class User_Complex(BaseModel):
        """Mocked class with a single primary key with varied serialization support."""

        __tablename__ = 'users_complex'

        id = Column('id',
                    Integer,
                    primary_key = True,
                    supports_csv = True,
                    csv_sequence = 1,
                    supports_json = True,
                    supports_yaml = True,
                    supports_dict = True)
        name = Column('username',
                      String(50),
                      supports_csv = True,
                      csv_sequence = 2,
                      supports_json = True,
                      supports_yaml = True,
                      supports_dict = True)
        password = Column('password',
                          String(50),
                          supports_csv = (True, False),
                          csv_sequence = 3,
                          supports_json = (True, False),
                          supports_yaml = (True, False),
                          supports_dict = (True, False))
        hidden = Column('hidden_column',
                        String(50))

        addresses = relationship('Address_Complex',
                                 backref = 'user',
                                 supports_json = True,
                                 supports_yaml = (True, True),
                                 supports_dict = (True, False))

        _hybrid = 1

        @hybrid_property
        def hybrid(self):
            return self._hybrid

        @hybrid.setter
        def hybrid(self, value):
            self._hybrid = value

        @hybrid_property
        def hybrid_differentiated(self):
            return self._hybrid

        @hybrid_differentiated.setter
        def hybrid_differentiated(self, value):
            self._hybrid = value

        #keywords_basic = association_proxy('keywords_basic',
        #                                   'keyword')

    class UserKeyword(BaseModel):
        __tablename__ = 'user_keywords'

        user_id = Column('user_id',
                         Integer,
                         ForeignKey('users.id'),
                         primary_key = True)
        keyword_id = Column('keyword_id',
                            Integer,
                            ForeignKey('keywords.id'),
                            primary_key = True)
        special_key = Column('special_key', String(50))

        user = relationship(User,
                            backref = backref('keywords_basic',
                                              cascade = 'all, delete-orphan'))

        keyword = relationship('Keyword')

        def __init__(self, keyword = None, user = None, special_key = None):
            self.user = user
            self.keyword = keyword
            self.special_key = special_key

    class UserKeyword_Complex(BaseModel):
        __tablename__ = 'user_keywords_complex'

        user_id = Column('user_id',
                         Integer,
                         ForeignKey('users_complex.id'),
                         primary_key = True)
        keyword_id = Column('keyword_id',
                            Integer,
                            ForeignKey('keywords.id'),
                            primary_key = True)
        special_key = Column('special_key', String(50))

        user = relationship(User_Complex,
                            backref = backref('keywords_basic',
                                              cascade = 'all, delete-orphan'))
        keyword = relationship('Keyword')

        def __init__(self, keyword = None, user = None, special_key = None):
            self.user = user
            self.keyword = keyword
            self.special_key = special_key

    class Keyword(BaseModel):
        __tablename__ = 'keywords'

        id = Column('id',
                    Integer,
                    primary_key = True)
        keyword = Column('keyword',
                         String(50),
                         supports_csv = True)

        def __init__(self, id, keyword):
            self.id = id
            self.keyword = keyword

    class Address_Complex(BaseModel):
        """Mocked class with a single primary key."""

        __tablename__ = 'addresses_complex'

        id = Column('id',
                    Integer,
                    primary_key = True)
        email = Column('email_address',
                       String(50),
                       supports_csv = True,
                       supports_json = True,
                       supports_yaml = True,
                       supports_dict = True,
                       on_serialize = validators.email,
                       on_deserialize = validators.email)
        user_id = Column('user_id',
                         Integer,
                         ForeignKey('users_complex.id'))

    class User_Complex_Meta(BaseModel):
        """Mocked class with a single primary key."""

        __tablename__ = 'users_complex_meta'

        __serialization__ = [
            AttributeConfiguration(name = 'id',
                                   supports_csv = True,
                                   csv_sequence = 1,
                                   supports_json = True,
                                   supports_yaml = True,
                                   supports_dict = True),
            AttributeConfiguration(name = 'name',
                                   supports_csv = True,
                                   csv_sequence = 2,
                                   supports_json = True,
                                   supports_yaml = True,
                                   supports_dict = True,
                                   on_serialize = None,
                                   on_deserialize = None),
            AttributeConfiguration(name = 'addresses',
                                   supports_json = True,
                                   supports_yaml = (True, True),
                                   supports_dict = (True, False)),
            AttributeConfiguration(name = 'hybrid',
                                   supports_csv = True,
                                   supports_json = True,
                                   supports_yaml = True,
                                   supports_dict = True),
            AttributeConfiguration(name = 'password',
                                   supports_csv = (True, False),
                                   csv_sequence = 3,
                                   supports_json = (True, False),
                                   supports_yaml = (True, False),
                                   supports_dict = (True, False))
        ]

        id = Column('id',
                    Integer,
                    primary_key = True)
        name = Column('username',
                      String(50))
        addresses = relationship('Address_Complex_Meta', backref = 'user')

        password = Column('password',
                          String(50))
        hidden = Column('hidden_column',
                        String(50))

        _hybrid = 1

        @hybrid_property
        def hybrid(self):
            return self._hybrid

        @hybrid.setter
        def hybrid(self, value):
            self._hybrid = value

        @hybrid_property
        def hybrid_differentiated(self):
            return self._hybrid

        @hybrid_differentiated.setter
        def hybrid_differentiated(self, value):
            self._hybrid = value

        keywords_basic = association_proxy('keywords_basic', 'keyword')

    class Address_Complex_Meta(BaseModel):
        """Mocked class with a single primary key."""

        __tablename__ = 'addresses_complex_meta'

        id = Column('id',
                    Integer,
                    primary_key = True)
        email = Column('email_address',
                       String(50),
                       supports_csv = True,
                       supports_json = True,
                       supports_yaml = True,
                       supports_dict = True,
                       on_serialize = validators.email,
                       on_deserialize = validators.email)
        user_id = Column('user_id',
                         Integer,
                         ForeignKey('users_complex_meta.id'))


    class User_Complex_PostgreSQL(BaseModel):
        """Mocked class with a single primary key."""

        __tablename__ = 'users_complex_postgresql'

        __serialization__ = [
            AttributeConfiguration(name = 'id',
                                   supports_csv = True,
                                   csv_sequence = 1,
                                   supports_json = True,
                                   supports_yaml = True,
                                   supports_dict = True),
            AttributeConfiguration(name = 'name',
                                   supports_csv = True,
                                   csv_sequence = 2,
                                   supports_json = True,
                                   supports_yaml = True,
                                   supports_dict = True,
                                   on_serialize = return_serialized,
                                   on_deserialize = return_deserialized),
            AttributeConfiguration(name = 'addresses',
                                   supports_json = True,
                                   supports_yaml = (True, True),
                                   supports_dict = (True, False)),
            AttributeConfiguration(name = 'hybrid',
                                   supports_csv = True,
                                   supports_json = True,
                                   supports_yaml = True,
                                   supports_dict = True,
                                   display_name = 'hybrid_value'),
            AttributeConfiguration(name = 'password',
                                   supports_csv = (True, False),
                                   csv_sequence = 3,
                                   supports_json = (True, False),
                                   supports_yaml = (True, False),
                                   supports_dict = (True, False)),
            AttributeConfiguration(name = 'time_delta',
                                   supports_csv = True,
                                   supports_json = False,
                                   supports_yaml = False,
                                   supports_dict = False)
        ]

        id = Column('id',
                    Integer,
                    primary_key = True)
        name = Column('username',
                      String(50))
        addresses = relationship('Address_Complex_PostgreSQL', backref = 'user')

        password = Column('password',
                          String(50))
        hidden = Column('hidden_column',
                        String(50))

        smallint_column = Column('smallint_column',
                                 sqlite.SMALLINT,
                                 supports_csv = True,
                                 csv_sequence = 4)

        _hybrid = 1

        time_delta = Column('time_delta',
                            Interval)

        @hybrid_property
        def hybrid(self):
            return self._hybrid

        @hybrid.setter
        def hybrid(self, value):
            self._hybrid = value

        @hybrid_property
        def hybrid_differentiated(self):
            return self._hybrid

        @hybrid_differentiated.setter
        def hybrid_differentiated(self, value):
            self._hybrid = value

        keywords_basic = association_proxy('keywords_basic', 'keyword')

    class Address_Complex_PostgreSQL(BaseModel):
        """Mocked class with a single primary key."""

        __tablename__ = 'addresses_complex_postgresql'

        id = Column('id',
                    Integer,
                    primary_key = True)
        email = Column('email_address',
                       String(50),
                       supports_csv = True,
                       supports_json = True,
                       supports_yaml = True,
                       supports_dict = True,
                       on_serialize = validators.email,
                       on_deserialize = validators.email)
        user_id = Column('user_id',
                         Integer,
                         ForeignKey('users_complex_postgresql.id'))



    BaseModel.metadata.create_all(db_engine)

    yield {
        'base_model': BaseModel,
        'model_single_pk': (User, Address),
        'model_composite_pk': (User2, Address2),
        'model_complex': (User_Complex, Address_Complex),
        'model_complex_meta': (User_Complex_Meta, Address_Complex_Meta),
        'model_complex_postgresql': (User_Complex_PostgreSQL, Address_Complex_PostgreSQL)
    }

    clear_mappers()
    BaseModel.metadata.drop_all(db_engine)
    BaseModel.metadata.clear()

@pytest.yield_fixture(scope = 'session')
def base_model(request, tables):
    BaseModel = tables['base_model']

    yield BaseModel


@pytest.yield_fixture
def db_session(request, db_engine, base_model):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind = connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture()
def model_single_pk(request, tables):
    User = tables['model_single_pk'][0]
    Address = tables['model_single_pk'][1]

    return (User, Address)


@pytest.fixture()
def model_reflected_tables(request, db_engine, tables):
    BaseModel = tables['base_model']

    class User_Complex_Reflected(BaseModel):
        __table__ = Table('users_complex',
                          BaseModel.metadata,
                          autoload = True,
                          autoload_with = db_engine)

    class User_Complex_Meta_Reflected(BaseModel):
        __table__ = Table('users_complex_meta',
                          BaseModel.metadata,
                          autoload = True,
                          autoload_with = db_engine)

    class User_Complex_Meta_Reflected_Meta(BaseModel):
        __serialization__ = tables['model_complex_meta'][0].__serialization__

        __table__ = Table('users_complex_meta',
                          BaseModel.metadata,
                          autoload = True,
                          autoload_with = db_engine)

    return (User_Complex_Reflected,
            User_Complex_Meta_Reflected,
            User_Complex_Meta_Reflected_Meta)


@pytest.fixture()
def instance_single_pk(request, model_single_pk):
    instance_values = {
        'id': 1,
        'name': 'Test Name'
    }
    user = model_single_pk[0]

    instance = user(**instance_values)

    return (instance, instance_values)


@pytest.fixture(scope = 'session')
def model_composite_pk(request, tables):
    User2 = tables['model_composite_pk'][0]
    Address2 = tables['model_composite_pk'][1]

    return (User2, Address2)


@pytest.fixture
def instance_composite_pk(request, model_composite_pk):
    instance_values = {
        'id': 1,
        'id2': 2,
        'id3': 3,
        'name': 'Test Name'
    }
    user = model_composite_pk[0]

    instance = user(**instance_values)

    return (instance, instance_values)


@pytest.fixture(scope = 'session')
def model_complex(request, tables):
    User = tables['model_complex'][0]
    Address = tables['model_complex'][1]

    return (User, Address)

@pytest.fixture(scope = 'session')
def model_complex_meta(request, tables):
    User = tables['model_complex_meta'][0]
    Address = tables['model_complex_meta'][1]

    return (User, Address)


@pytest.fixture(scope = 'session')
def model_complex_postgresql(request, tables):
    User2 = tables['model_complex_postgresql'][0]
    Address2 = tables['model_complex_postgresql'][1]

    return (User2, Address2)


@pytest.fixture
def instance_complex(request, model_complex):
    user_instance_values = {
        'id': 1,
        'name': 'test_username',
        'password': 'test_password',
        'hidden': 'hidden value'
    }
    address_instance_values = {
        'id': 1,
        'email': 'test@domain.com',
        'user_id': 1
    }
    user = model_complex[0]
    address = model_complex[1]

    user_instance = user(**user_instance_values)
    address_instance = address(**address_instance_values)

    instances = (user_instance, address_instance)
    instance_values = (user_instance_values, address_instance_values)

    return (instances, instance_values)


@pytest.fixture
def instance_complex_meta(request, model_complex_meta):
    user_instance_values = {
        'id': 1,
        'name': 'test_username',
        'password': 'test_password',
        'hidden': 'hidden value'
    }
    address_instance_values = {
        'id': 1,
        'email': 'test@domain.com',
        'user_id': 1
    }
    user = model_complex_meta[0]
    address = model_complex_meta[1]

    user_instance = user(**user_instance_values)
    address_instance = address(**address_instance_values)

    instances = (user_instance, address_instance)
    instance_values = (user_instance_values, address_instance_values)

    return (instances, instance_values)


@pytest.fixture
def instance_postgresql(request, model_complex_postgresql):
    user_instance_values = {
        'id': 1,
        'name': 'test_username',
        'password': 'test_password',
        'hidden': 'hidden value',
        'smallint_column': 2,
        'time_delta': datetime.timedelta(1)
    }
    address_instance_values = {
        'id': 1,
        'email': 'test@domain.com',
        'user_id': 1
    }
    user = model_complex_postgresql[0]
    address = model_complex_postgresql[1]

    user_instance = user(**user_instance_values)
    address_instance = address(**address_instance_values)

    instances = (user_instance, address_instance)
    instance_values = (user_instance_values, address_instance_values)

    return (instances, instance_values)


@pytest.fixture
def original_hybrid_config(request):
    config  = AttributeConfiguration(name = 'hybrid',
                                     supports_csv = True,
                                     csv_sequence = None,
                                     supports_json = True,
                                     supports_yaml = True,
                                     supports_dict = True,
                                     on_serialize = None,
                                     on_deserialize = None)
    return config


@pytest.fixture
def original_config_set(request):
    """Original serialization configuration applied to the complex model class.

    Dictionary key ``True`` indicates that it applies to ``complex_meta``, while
    ``False`` indicates that it applies to just ``complex`` (non-meta).
    """
    config_set = {
        True: [
            AttributeConfiguration(name = 'id',
                                   supports_csv = True,
                                   csv_sequence = 1,
                                   supports_json = True,
                                   supports_yaml = True,
                                   supports_dict = True),
            AttributeConfiguration(name = 'name',
                                   supports_csv = True,
                                   csv_sequence = 2,
                                   supports_json = True,
                                   supports_yaml = True,
                                   supports_dict = True,
                                   on_serialize = None,
                                   on_deserialize = None),
            AttributeConfiguration(name = 'addresses',
                                   supports_json = True,
                                   supports_yaml = (True, True),
                                   supports_dict = (True, False)),
            AttributeConfiguration(name = 'hybrid',
                                   supports_csv = True,
                                   supports_json = True,
                                   supports_yaml = True,
                                   supports_dict = True),
            AttributeConfiguration(name = 'password',
                                   supports_csv = (True, False),
                                   csv_sequence = 3,
                                   supports_json = (True, False),
                                   supports_yaml = (True, False),
                                   supports_dict = (True, False))
        ],
        False: [
            AttributeConfiguration(name = 'id',
                                   supports_csv = True,
                                   csv_sequence = 1,
                                   supports_json = True,
                                   supports_yaml = True,
                                   supports_dict = True),
            AttributeConfiguration(name = 'name',
                                   supports_csv = True,
                                   csv_sequence = 2,
                                   supports_json = True,
                                   supports_yaml = True,
                                   supports_dict = True),
            AttributeConfiguration(name = 'password',
                                   supports_csv = (True, False),
                                   csv_sequence = 3,
                                   supports_json = (True, False),
                                   supports_yaml = (True, False),
                                   supports_dict = (True, False)),
            AttributeConfiguration(name = 'addresses',
                                   supports_json = True,
                                   supports_yaml = (True, True),
                                   supports_dict = (True, False))
        ]
    }

    return config_set


@pytest.fixture
def new_config_set(request):
    config_set = [
        AttributeConfiguration(name = 'id',
                               supports_csv = True,
                               csv_sequence = 1,
                               supports_json = True,
                               supports_yaml = True,
                               supports_dict = True),
        AttributeConfiguration(name = 'name',
                               supports_csv = True,
                               csv_sequence = 2,
                               supports_json = True,
                               supports_yaml = True,
                               supports_dict = True,
                               on_serialize = None,
                               on_deserialize = None),
        AttributeConfiguration(name = 'addresses',
                               supports_json = True,
                               supports_yaml = (True, True),
                               supports_dict = (True, False)),
        AttributeConfiguration(name = 'hybrid',
                               supports_csv = True,
                               supports_json = True,
                               supports_yaml = True,
                               supports_dict = True),
        AttributeConfiguration(name = 'password',
                               supports_csv = False,
                               supports_json = False,
                               supports_yaml = False,
                               supports_dict = False)
    ]

    dict_representation = {
        'id': {
            'supports_csv': (True, True),
            'csv_sequence': 1,
            'supports_json': (True, True),
            'supports_yaml': (True, True),
            'supports_dict': (True, True),
            'on_serialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            },
            'on_deserialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            }
        },
        'name': {
            'supports_csv': (True, True),
            'csv_sequence': 2,
            'supports_json': (True, True),
            'supports_yaml': (True, True),
            'supports_dict': (True, True),
            'on_serialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            },
            'on_deserialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            }
        },
        'addresses': {
            'supports_csv': (False, False),
            'csv_sequence': None,
            'supports_json': (True, True),
            'supports_yaml': (True, True),
            'supports_dict': (True, False),
            'on_serialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            },
            'on_deserialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            }
        },
        'hybrid': {
            'supports_csv': (True, True),
            'csv_sequence': None,
            'supports_json': (True, True),
            'supports_yaml': (True, True),
            'supports_dict': (True, True),
            'on_serialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            },
            'on_deserialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            }
        },
        'password': {
            'supports_csv': (False, False),
            'csv_sequence': None,
            'supports_json': (False, False),
            'supports_yaml': (False, False),
            'supports_dict': (False, False),
            'on_serialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            },
            'on_deserialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            }
        }
    }

    return config_set, dict_representation

@pytest.fixture
def new_argument_set(request):
    attribute_set = {
        'attributes': ['id',
                       'name',
                       'hybrid'],
        'supports_csv': True,
        'supports_json': True,
        'supports_yaml': True,
        'supports_dict': False
    }

    dict_representation = {
        'id': {
            'supports_csv': (True, True),
            'csv_sequence': None,
            'supports_json': (True, True),
            'supports_yaml': (True, True),
            'supports_dict': (False, False),
            'on_serialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            },
            'on_deserialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            }
        },
        'name': {
            'supports_csv': (True, True),
            'csv_sequence': None,
            'supports_json': (True, True),
            'supports_yaml': (True, True),
            'supports_dict': (False, False),
            'on_serialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            },
            'on_deserialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            }
        },
        'hybrid': {
            'supports_csv': (True, True),
            'csv_sequence': None,
            'supports_json': (True, True),
            'supports_yaml': (True, True),
            'supports_dict': (False, False),
            'on_serialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            },
            'on_deserialize': {
                'csv': None,
                'json': None,
                'yaml': None,
                'dict': None
            }
        }
    }

    return attribute_set, dict_representation


@pytest.fixture(scope = 'session')
def existing_db(request, tmpdir_factory):
    db_filename = str(tmpdir_factory.mktemp('db').join('temporary.db'))
    connection = sqlite3.connect(db_filename)

    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE users
                   (id INT PRIMARY KEY, col1 TEXT, col2 TEXT, col3 TEXT)'''
                  )
    cursor.execute('''CREATE TABLE addresses
                   (id INT PRIMARY KEY, col1 TEXT, col2 TEXT)'''
                  )

    connection.commit()

    users = [(1, 'row1test1', 'row1test2', 'row1test3'),
             (2, 'row2test1', 'row1test2', 'row2test3')]
    addresses = [(1, 'row1test1', 'row1test2'),
                 (2, 'row2test1', 'row2test2')]

    cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?)', users)
    cursor.executemany('INSERT INTO addresses VALUES (?, ?, ?)', addresses)

    connection.commit()
    connection.close()

    return db_filename


@pytest.fixture
def input_files(request):
    """Return the ``--inputs`` command-line option."""
    return request.config.getoption("--inputs")


def check_input_file(input_directory, input_value):
    inputs = os.path.abspath(input_directory)
    if not os.path.exists(input_directory):
        raise AssertionError('input directory (%s) does not exist' % inputs)
    elif not os.path.isdir(input_directory):
        raise AssertionError('input directory (%s) is not a directory' % inputs)

    try:
        input_file = os.path.join(input_directory, input_value)
    except (TypeError, AttributeError):
        input_file = None

    if input_file is not None and checkers.is_file(input_file):
        input_value = input_file

    return input_value
