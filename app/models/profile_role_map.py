from .db_base import MySqlBase
from sqlalchemy import Column, String, Integer, TIMESTAMP


class ProfilesRoleMap(MySqlBase):

    __tablename__ = 'profile_role_map'
    id = Column(Integer, primary_key=True)
    profile_id = Column(String)
    role_id = Column(Integer)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)