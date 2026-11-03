"""Generate VAPID keys for push reminders (plan 5.5). Run from code/:

    python -m backend.scripts.generate_vapid_keys

and paste the printed lines into the project's root .env (never commit it).
"""
from backend.services.webpush import generate_vapid_keys

if __name__ == "__main__":
    for name, value in generate_vapid_keys().items():
        print(f"{name}={value}")
    print("VAPID_SUBJECT=mailto:twoj-adres@example.com")
