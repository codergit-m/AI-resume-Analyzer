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

    # Check if shivam admin already exists
    existing = User.query.filter_by(email="sc5445889@gmail.com").first()
    if existing:
        print("Admin user already exists:", existing.email)
        existing.full_name = "Shivam chauhan"
        existing.role = "admin"
        if not existing.firebase_uid:
            existing.firebase_uid = "mock-admin-uid"
        db.session.commit()
    else:
        admin = User(
            email="sc5445889@gmail.com",
            firebase_uid="mock-admin-uid",
            full_name="Shivam chauhan",
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
        print("[OK] Admin created!")
        print("   Email:    sc5445889@gmail.com")
        print("   Name:     Shivam chauhan")
        print("   [!] Make sure to sign up with this email on the frontend/Firebase to link your account!")
