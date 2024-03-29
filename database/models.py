from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.sql import func

Base = declarative_base()

class City(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    city_name = Column(CITEXT, nullable=False)
    score = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())