import json
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=False)
    face_data = Column(Text)  # JSON: proportions, swelling, muscle_tension, skin_quality
    body_data = Column(Text)  # JSON: proportions, asymmetries, missing_muscles
    skin_data = Column(Text)  # JSON: skin_type, problems, changes
    hair_data = Column(Text)  # JSON: density, hairline, recommendations
    overall_score = Column(Float, default=0.0)  # LookScore
    attractiveness_lever = Column(Text)  # JSON: primary_lever, secondary_levers
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    photo = relationship("Photo", backref="analysis")

    def get_face_data(self):
        return json.loads(self.face_data) if self.face_data else {}

    def set_face_data(self, data: dict):
        self.face_data = json.dumps(data)

    def get_body_data(self):
        return json.loads(self.body_data) if self.body_data else {}

    def set_body_data(self, data: dict):
        self.body_data = json.dumps(data)

    def get_skin_data(self):
        return json.loads(self.skin_data) if self.skin_data else {}

    def set_skin_data(self, data: dict):
        self.skin_data = json.dumps(data)

    def get_hair_data(self):
        return json.loads(self.hair_data) if self.hair_data else {}

    def set_hair_data(self, data: dict):
        self.hair_data = json.dumps(data)
