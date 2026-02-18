"""
seed_demo_users.py
------------------
Creates one demo account for every role in Smart Shield.
Run from the backend/ directory:
    python seed_demo_users.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database.database import SessionLocal, Base, engine
from database.models import User, RiderProfile, DriverProfile
from api.services.security import get_password_hash
from loguru import logger

# ── Demo accounts ─────────────────────────────────────────────────────────────
DEMO_USERS = [
    {
        "username":    "admin@smartshield.com",
        "email":       "admin@smartshield.com",
        "password":    "Admin@123",
        "role":        "admin",
        "full_name":   "Arjun Sharma",
        "status":      "active",
    },
    {
        "username":    "dispatcher@smartshield.com",
        "email":       "dispatcher@smartshield.com",
        "password":    "Dispatch@123",
        "role":        "dispatcher",
        "full_name":   "Meena Pillai",
        "status":      "active",
    },
    {
        "username":    "driver@smartshield.com",
        "email":       "driver@smartshield.com",
        "password":    "Driver@123",
        "role":        "driver",
        "full_name":   "Karan Singh",
        "status":      "active",          # normally pending_approval; set active for demo
        "vehicle_type":   "bike",
        "vehicle_number": "TN-01-CD-5678",
        "license_number": "TN2024DL9999",
    },
    {
        "username":    "rider@smartshield.com",
        "email":       "rider@smartshield.com",
        "password":    "Rider@123",
        "role":        "rider",
        "full_name":   "Priya Kumar",
        "status":      "active",
        "vehicle_type":   "bike",
        "license_number": "TN2024RL1234",
    },
    {
        "username":    "customer@smartshield.com",
        "email":       "customer@smartshield.com",
        "password":    "Customer@123",
        "role":        "customer",
        "full_name":   "Suresh Babu",
        "status":      "active",
    },
]

def seed():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    created, skipped = 0, 0

    try:
        for u in DEMO_USERS:
            existing = db.query(User).filter(User.username == u["username"]).first()
            if existing:
                logger.info(f"[SKIP]  {u['username']} already exists")
                skipped += 1
                continue

            new_user = User(
                username=u["username"],
                email=u["email"],
                hashed_password=get_password_hash(u["password"]),
                role=u["role"],
                full_name=u["full_name"],
                status=u["status"],
                emergency_contacts=[],
            )
            db.add(new_user)
            db.flush()   # get new_user.id before commit

            # Role-specific profiles
            if u["role"] == "rider":
                db.add(RiderProfile(
                    user_id=new_user.id,
                    vehicle_type=u.get("vehicle_type", "bike"),
                    license_number=u.get("license_number", ""),
                    preferences={"location_sharing": True, "notifications": True},
                ))
            elif u["role"] == "driver":
                db.add(DriverProfile(
                    user_id=new_user.id,
                    vehicle_type=u.get("vehicle_type", "bike"),
                    vehicle_number=u.get("vehicle_number", ""),
                    license_number=u.get("license_number", ""),
                    documents={},
                ))

            db.commit()
            logger.success(f"[OK]    Created {u['role']:12s} → {u['username']}")
            created += 1

    except Exception as e:
        db.rollback()
        logger.error(f"Seed failed: {e}")
        raise
    finally:
        db.close()

    print(f"\n✅  Done — {created} created, {skipped} skipped.\n")
    print("=" * 60)
    print(f"{'ROLE':<14} {'EMAIL':<35} {'PASSWORD'}")
    print("-" * 60)
    for u in DEMO_USERS:
        print(f"{u['role']:<14} {u['username']:<35} {u['password']}")
    print("=" * 60)

if __name__ == "__main__":
    seed()
