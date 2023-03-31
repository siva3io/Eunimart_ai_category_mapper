from .db_base import MySqlBase
from sqlalchemy import Column, String, TIMESTAMP


class Profiles(MySqlBase):

    __tablename__ = 'profiles'
    id = Column(String, primary_key=True)
    profile_name = Column(String)
    description = Column(String)
    updated_by = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)