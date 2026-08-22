import json
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    goals = Column(Text, default="{}")  # JSON: {face: 0.4, body: 0.3, skin: 0.3}
    lifestyle = Column(Text, default="{}")  # JSON: {sleep: 7, stress: 5, activity: 3}
    health = Column(Text, default="{}")  # JSON: {pregnancy: false, kidney_disease: false, ...}
    discipline_score = Column(Integer, default=50)

    user = relationship("User", backref="profile")

    def get_goals(self):
        return json.loads(self.goals)

    def set_goals(self, data: dict):
        self.goals = json.dumps(data)

    def get_lifestyle(self):
        return json.loads(self.lifestyle)

    def set_lifestyle(self, data: dict):
        self.lifestyle = json.dumps(data)

    def get_health(self):
        return json.loads(self.health)

    def set_health(self, data: dict):
        self.health = json.dumps(data)
