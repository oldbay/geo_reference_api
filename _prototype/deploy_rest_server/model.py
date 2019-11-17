import os
import imp
import constant
from sqlalchemy import Column, create_engine
from sqlalchemy import Integer, ForeignKey, Unicode, PickleType, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

conf = imp.load_source("conf", os.path.dirname(constant.__file__)+"/service.conf")

if conf.DBPath:
    DBPath = conf.DBPath
else:
    DBPath = 'sqlite:///'+os.path.dirname(constant.__file__)+'/db/data.sqlite'

engine = create_engine(DBPath, echo=conf.DBEcho)
DeclarativeBase = declarative_base(engine)
metadata = DeclarativeBase.metadata


class Que(DeclarativeBase):

    """ Que """

    __tablename__ = 'que'

    id = Column(Integer, primary_key=True, autoincrement=True)
    qtime = Column(DateTime, nullable=False)
    obj = Column(PickleType)
    stat = Column(Boolean, default=False)
    queue_id = Column(Integer, ForeignKey('queue.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('job.id'))


class Queue(DeclarativeBase):

    """ Queue """

    __tablename__ = 'queue'

    id = Column(Integer, primary_key=True, autoincrement=True)
    qkey = Column(Unicode(256), nullable=False)
    ques = relationship('Que')


class User(DeclarativeBase):

    """ user """

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(256), nullable=False, unique=True)
    key = Column(Unicode(512))
    jobs = relationship('Job')


class Job(DeclarativeBase):

    """ job """

    __tablename__ = 'job'

    id = Column(Integer, primary_key=True, autoincrement=True)
    num = Column(Integer, nullable=False, unique=True)
    cmd = Column(Unicode(512))
    log = Column(Unicode(1024))
    const_state = Column(Unicode(128), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    progs = relationship('Prog')
    files = relationship('File')
    ques = relationship('Que')


class Prog(DeclarativeBase):

    """ prog """

    __tablename__ = 'prog'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(256), nullable=False, unique=True)
    job_id = Column(Integer, ForeignKey('job.id'), nullable=False)
    files = relationship('Ver')


class Ver(DeclarativeBase):

    """ ver """

    __tablename__ = 'ver'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(256), nullable=False)
    prog_id = Column(Integer, ForeignKey('prog.id'), nullable=False)
    files = relationship('File')


class File(DeclarativeBase):

    """ file """

    __tablename__ = 'file'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(256), nullable=False)
    ver_id = Column(Integer, ForeignKey('ver.id'), nullable=False)
    const_arch = Column(Unicode(256), nullable=False)
    const_type = Column(Unicode(256), nullable=False)
    job_id = Column(Integer, ForeignKey('job.id'), nullable=False)


# Calculated Column
from sqlalchemy.orm import column_property
from sqlalchemy import select

Que.queue_key = column_property(select([(Queue.qkey)], Que.queue_id == Queue.id))
Que.job_num = column_property(select([(Job.num)], Que.job_id == Job.id))
Job.user_nam = column_property(select([(User.name)], Job.user_id == User.id))
Ver.prog_nam = column_property(select([(Prog.name)], Ver.prog_id == Prog.id))
Prog.job_num = column_property(select([(Job.num)], Prog.job_id == Job.id))
File.ver_nam = column_property(select([(Ver.name)], File.ver_id == Ver.id))
File.prog_nam = column_property(select([(Ver.prog_nam)], File.ver_id == Ver.id))
File.job_num = column_property(select([(Job.num)], File.job_id == Job.id))

# Create Database
metadata.create_all()
