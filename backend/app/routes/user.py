"""
user.py — User profile route (subscription status).

Auth: Firebase ID token (same as all other protected routes).
"""
from flask import Blueprint, jsonify
from ..firebase_auth import firebase_required, get_firebase_uid
from ..models.user import User

user_bp = Blueprint("user", __name__)


@user_bp.route("/me", methods=["GET"])
@firebase_required
def get_user_me():
    """Return the current user's subscription status and analysis count."""
    firebase_uid = get_firebase_uid()
    user = User.query.filter_by(firebase_uid=firebase_uid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "subscription_active": bool(user.subscription_active),
        "analysis_count": user.analysis_count or 0,
    }), 200
