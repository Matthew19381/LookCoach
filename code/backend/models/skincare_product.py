from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from .base import Base


class SkincareProduct(Base):
    """A product the user owns - from a label photo or pasted INCI list."""

    __tablename__ = "skincare_products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True, default=1)
    name = Column(String, nullable=False)
    ingredients_json = Column(Text, nullable=False, default="[]")  # INCI list in label order
    actives_json = Column(Text, nullable=False, default="[]")  # catalogue names found
    slot = Column(String, nullable=True)  # morning | evening | both | None
    in_routine = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class IngredientUsage(Base):
    """One active ingredient used on a day (logged via "Użyłem dziś") - feeds rotation."""

    __tablename__ = "ingredient_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True, default=1)
    ingredient = Column(String, nullable=False, index=True)  # catalogue name
    product_id = Column(Integer, nullable=True)
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
