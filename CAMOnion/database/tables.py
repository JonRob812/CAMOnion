from abc import ABC

from sqlalchemy import create_engine, select, Table, Column, Sequence, Integer, String, MetaData, ForeignKey, func, \
    exists, DECIMAL, and_, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from decimal import Decimal as D
import sqlalchemy.types as types

Base = declarative_base()


class SqliteNumeric(types.TypeDecorator):
    impl = types.String

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.VARCHAR(100))

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        return D(value)


# can overwrite the imported type name
# @note: the TypeDecorator does not guarantie the scale and precision.
# you can do this with separate checks
Numeric = SqliteNumeric


class Tool(Base):
    __tablename__ = 'tools'
    id = Column(Integer, primary_key=True)
    qb_id = Column(Integer, unique=True)
    tool_type_id = Column(Integer, ForeignKey('tool_types.id'))
    tool_number = Column(Integer)
    name = Column(String)
    diameter = Column(Numeric)
    number_of_flutes = Column(Integer)
    pitch = Column(Numeric)

    operations = relationship('Operation', back_populates='tool')



class Tool_Type(Base):
    __tablename__ = 'tool_types'
    id = Column(Integer, primary_key=True)
    tool_type = Column(String)


class Feature(Base):
    __tablename__ = 'features'
    name = Column(String, primary_key=True)
    id = Column(Integer, primary_key=True)
    description = Column(String)
    operations = relationship('Operation', back_populates='feature')


class Operation(Base):
    __tablename__ = 'operations'
    id = Column(Integer, primary_key=True)

    feature_id = Column(Integer, ForeignKey('features.id'))
    feature = relationship('Feature', back_populates='operations')

    tool_id = Column(Integer, ForeignKey('tools.id'))
    tool = relationship('Tool', back_populates='operations')

    camo_op_id = Column(Integer, ForeignKey('camo_ops.id'))
    camo_op = relationship('CamoOp', back_populates='operations')

    peck = Column(DECIMAL)
    feed = Column(DECIMAL)
    speed = Column(DECIMAL)


class CamoOp(Base):
    __tablename__ = 'camo_ops'
    id = Column(Integer, primary_key=True)
    op_type = Column(String)
    function = Column(String)
    priority = Column(DECIMAL)
    operations = relationship('Operation', back_populates='camo_op')


class Machine(Base):
    __tablename__ = 'machines'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    max_rpm = Column(Integer)
    spot = Column(String)
    drill = Column(String)
    tap = Column(String)
    peck = Column(String)
    ream = Column(String)
    drill_format = Column(String)
    tap_format = Column(String)
    program_start = Column(String)
    program_end = Column(String)
    tool_start = Column(String)
    tool_end = Column(String)
    op_start = Column(String)
    op_end = Column(String)
