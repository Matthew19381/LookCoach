"""Plan 5.5: Web Push reminders - subscription and settings."""
import os
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.push import PushSubscription
from ..services import reminders, webpush

router = APIRouter()
_HHMM = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class Keys(BaseModel):
    p256dh: str = Field(..., max_length=200)
    auth: str = Field(..., max_length=100)


class SubscriptionIn(BaseModel):
    endpoint: str = Field(..., max_length=2000)
    keys: Keys

    @field_validator("endpoint")
    @classmethod
    def https_only(cls, v: str) -> str:
        if not v.startswith("https://"):
            raise ValueError("endpoint must be https")
        return v


class SettingsIn(BaseModel):
    enabled: bool = True
    morning_time: str = "07:30"
    evening_time: str = "21:30"
    photo_reminders: bool = True

    @field_validator("morning_time", "evening_time")
    @classmethod
    def hhmm(cls, v: str) -> str:
        if not _HHMM.match(v):
            raise ValueError("HH:MM")
        return v


@router.get("/vapid-public-key")
def vapid_public_key():
    return {"key": os.getenv("VAPID_PUBLIC_KEY") or None}


@router.post("/subscribe", status_code=201)
def subscribe(body: SubscriptionIn, user_id: int = 1, db: Session = Depends(get_db)):
    row = db.query(PushSubscription).filter(PushSubscription.endpoint == body.endpoint).first()
    if not row:
        row = PushSubscription(endpoint=body.endpoint, user_id=user_id, p256dh="", auth="")
        db.add(row)
    row.user_id, row.p256dh, row.auth = user_id, body.keys.p256dh, body.keys.auth
    db.commit()
    return {"status": "subscribed"}


@router.post("/unsubscribe")
def unsubscribe(body: SubscriptionIn, db: Session = Depends(get_db)):
    n = db.query(PushSubscription).filter(PushSubscription.endpoint == body.endpoint).delete()
    db.commit()
    return {"removed": n}


def _settings_out(row) -> dict:
    return {"enabled": row.enabled, "morning_time": row.morning_time, "evening_time": row.evening_time,
            "photo_reminders": row.photo_reminders}


@router.get("/settings")
def get_settings(user_id: int = 1, db: Session = Depends(get_db)):
    subscribed = db.query(PushSubscription).filter(PushSubscription.user_id == user_id).count()
    return {**_settings_out(reminders.settings_for(db, user_id)), "subscriptions": subscribed,
            "configured": bool(os.getenv("VAPID_PRIVATE_KEY"))}


@router.put("/settings")
def put_settings(body: SettingsIn, user_id: int = 1, db: Session = Depends(get_db)):
    row = reminders.settings_for(db, user_id)
    row.enabled, row.morning_time, row.evening_time, row.photo_reminders = (
        body.enabled, body.morning_time, body.evening_time, body.photo_reminders)
    db.commit()
    return _settings_out(row)


@router.post("/test")
def test_notification(user_id: int = 1, db: Session = Depends(get_db)):
    private = os.getenv("VAPID_PRIVATE_KEY")
    if not private:
        raise HTTPException(503, "Brak kluczy VAPID w .env — uruchom scripts/generate_vapid_keys.py.")
    key = webpush.load_vapid_private(private)
    subject = os.getenv("VAPID_SUBJECT", "mailto:lookcoach@localhost")
    sent = 0
    for sub in db.query(PushSubscription).filter(PushSubscription.user_id == user_id).all():
        try:
            webpush.send({"endpoint": sub.endpoint, "keys": {"p256dh": sub.p256dh, "auth": sub.auth}},
                         {"title": "LookCoach", "body": "Powiadomienia działają.", "url": "/"}, key, subject)
            sent += 1
        except webpush.SubscriptionGone:
            db.delete(sub)
            db.commit()
    return {"sent": sent}
