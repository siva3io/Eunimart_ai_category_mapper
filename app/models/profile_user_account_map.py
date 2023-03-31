from .db_base import MySqlBase
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey

from .profiles import Profiles


class ProfileUserAccountMap(MySqlBase):

    __tablename__ = 'profile_user_account_map'
    profile_id = Column(String, ForeignKey('profiles.id'), primary_key=True)
    account_id = Column(String,  primary_key=True)
    user_id = Column(String, primary_key=True)
    updated_by = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    profile = relationship(Profiles)    