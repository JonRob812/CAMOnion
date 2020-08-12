from CAMOnion.database.tables import *

from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import InterfaceError


def get_engine(url):
    return create_engine(url)


def get_session(url):
    engine = get_engine(url)
    s = sessionmaker(bind=engine)
    return s()


def setup_sql(url):
    engine = get_engine(url)
    connection = engine.connect()
    session_maker = sessionmaker(bind=engine)
    return engine, connection, session_maker()
