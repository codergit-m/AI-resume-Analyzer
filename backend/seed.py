"""
Seed script — creates an admin user in the database.
Run once after setting up the DB:
    python seed.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User

app = create_app()

with app.app_context():
    db.create_all()

    admin_email = app.config["ADMIN_EMAIL"]
    admin_name = app.config["ADMIN_NAME"]

    # Clean up old default admin user to avoid UNIQUE constraint conflicts
    old_admin_by_email = User.query.filter_by(email="admin@resumai.local").first()
    if old_admin_by_email:
        db.session.delete(old_admin_by_email)
        db.session.commit()
        print("Removed old default admin email: admin@resumai.local")

    old_admin_by_uid = User.query.filter_by(firebase_uid="mock-admin-uid").first()
    if old_admin_by_uid:
        db.session.delete(old_admin_by_uid)
        db.session.commit()
        print("Removed old default admin UID: mock-admin-uid")

    # There must be exactly one database admin: the designated owner.
    User.query.filter(User.role == "admin", User.email != admin_email).update(
        {User.role: "user"}, synchronize_session=False
    )

    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        print("Admin user already exists:", existing.email)
        existing.full_name = admin_name
        existing.role = "admin"
        db.session.commit()
    else:
        admin = User(
            email=admin_email,
            full_name=admin_name,
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
        print("[OK] Admin created!")
        print("   Email:    ", admin_email)
        print("   Name:     ", admin_name)
        print("   [!] Make sure to sign up with this email on the frontend/Firebase to link your account!")
