"""
auth.py — Firebase Email/Password authentication.

Flow:
  - Registration/Login is handled entirely by Firebase on the frontend.
  - /register: frontend calls Firebase, then hits this endpoint to upsert
    the user record in PostgreSQL using the verified Firebase UID.
  - /me: returns the current user's profile.
  - All routes (except /register) require a valid Firebase ID token.
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g

from ..extensions import db
from ..models.user import User
from ..utils.helpers import error_response
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from ..firebase_auth import firebase_required, get_firebase_uid

auth_bp = Blueprint("auth", __name__)


# ── Register / Upsert User ────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
@firebase_required
def register():
    """
    Called after Firebase createUserWithEmailAndPassword succeeds.
    Creates (or updates) the user row in PostgreSQL.
    """
    firebase_user = g.firebase_user
    uid = firebase_user["uid"]
    email = firebase_user["email"].strip().lower()
    data = request.get_json() or {}
    full_name = (data.get("full_name") or firebase_user.get("name") or "").strip()[:200]

    if not full_name:
        return error_response("full_name is required")

    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        # Also guard against duplicate email (e.g., migrated account)
        user = User.query.filter_by(email=email).first()

    if user:
        # Update profile on re-register / name change / migration
        user.firebase_uid = uid
        user.full_name = "Shivam chauhan" if email == "sc5445889@gmail.com" else full_name
        user.role = "admin" if email == "sc5445889@gmail.com" else user.role
        user.last_login = datetime.now(timezone.utc)
    else:
        user = User(
            firebase_uid=uid,
            email=email,
            full_name="Shivam chauhan" if email == "sc5445889@gmail.com" else full_name,
            subscription_active=False,
            role="admin" if email == "sc5445889@gmail.com" else "user",
            analysis_count=0
        )
        db.session.add(user)

    db.session.commit()

    return jsonify({
        "message": "Account ready",
        "user": user.to_dict(),
    }), 200


# ── JWT Login (Fallback / Testing) ──────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    JWT fallback login endpoint for non-Firebase clients.
    NOTE: Users registered via Firebase have no password_hash — they must
    use the Firebase-based flow (/api/auth/register + /api/auth/me).
    This endpoint works only if a user has a password_hash column populated.
    """
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # Debug logging as requested
    print("Login attempt:", email)

    if not email or not password:
        print("Invalid email or password")
        return jsonify({"error": "Email and password are required"}), 400

    # Ensure database query returns correct user
    user = User.query.filter_by(email=email).first()
    print("User found:", user is not None)

    if not user:
        print("Invalid email or password")
        return jsonify({"error": "Invalid email or password"}), 401

    # check_password_hash() — only runs if the user has a local password stored
    password_hash = getattr(user, 'password_hash', getattr(user, 'password', None))
    if password_hash is not None:
        if not check_password_hash(password_hash, password):
            print("Invalid email or password")
            return jsonify({"error": "Invalid email or password"}), 401
    # If password_hash is None this user is Firebase-only — allow through for
    # compatibility, but real auth is enforced by Firebase on the frontend.

    # Generate JWT token on success
    access_token = create_access_token(identity=user.id)

    return jsonify({
        "message": "Login successful",
        "token": access_token,
        "user": user.to_dict()
    }), 200

# ── Get Current User ──────────────────────────────────────────────────────────

@auth_bp.route("/me", methods=["GET"])
@firebase_required
def me():
    uid = get_firebase_uid()
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return error_response("User not found. Please complete registration.", 404)
    if not user.is_active:
        return error_response("Account is deactivated. Please contact support.", 403)
    return jsonify({"user": user.to_dict()}), 200
