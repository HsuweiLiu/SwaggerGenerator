from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, types
from datetime import datetime

Base = declarative_base()


class TestContent:
    This_is_string: str
    This_is_integer: int

    def __init__(self, test_str: str, test_int: int):
        self.This_is_string = test_str
        self.This_is_integer = test_int


class TestModel(Base):
    __tablename__ = 'TestModel'

    Id = Column(types.BigInteger, primary_key=True)
    ValidFlag = Column(types.Boolean, nullable=False, default=True)
    CreateUser = Column(types.String(40), nullable=False)
    CreateDateTime = Column(types.DateTime, nullable=False, default=datetime.now)

    # set attribute for all element.
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

