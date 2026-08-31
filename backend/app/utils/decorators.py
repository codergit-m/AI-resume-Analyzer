"""
decorators.py — Route-level access decorators using Firebase Auth.

admin_required: verifies Firebase token AND checks DB for admin role.
active_user_required: verifies Firebase token AND checks account is active.
"""

from functools import wraps
from flask import jsonify, g
from ..firebase_auth import firebase_required, get_firebase_uid
from ..extensions import db
from ..models.user import User


def admin_required(fn):
    """
    Requires a valid Firebase ID token from a user with role='admin'.
    Applies firebase_required first to populate g.firebase_user.
    """
    @wraps(fn)
    @firebase_required
    def wrapper(*args, **kwargs):
        uid = get_firebase_uid()
        user = User.query.filter_by(firebase_uid=uid).first()
        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


def active_user_required(fn):
    """Requires valid Firebase token AND an active account."""
    @wraps(fn)
    @firebase_required
    def wrapper(*args, **kwargs):
        uid = get_firebase_uid()
        user = User.query.filter_by(firebase_uid=uid).first()
        if not user or not user.is_active:
            return jsonify({"error": "Account is inactive or not found"}), 403
        return fn(*args, **kwargs)
    return wrapper
