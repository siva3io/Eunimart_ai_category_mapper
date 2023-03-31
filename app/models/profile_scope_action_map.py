from .db_base import MySqlBase
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey

from .service import Service
from .scopes import Scopes
from .profiles import Profiles


class ProfileScopeActionMap(MySqlBase):

    __tablename__ = 'profile_scope_action_map'
    
    profile_id = Column(String, ForeignKey('profiles.id'), primary_key=True)
    service_id = Column(String, ForeignKey('service.id'), primary_key=True)
    scope_id = Column(String, ForeignKey('scopes.id'), primary_key=True)
    permission_level = Column(Integer)
    updated_by = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    services = relationship(Service, lazy=True)
    scopes = relationship(Scopes)
    profile = relationship(Profiles)    