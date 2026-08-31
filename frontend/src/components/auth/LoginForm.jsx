import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-hot-toast";
import { Mail, Lock, Eye, EyeOff, ArrowRight } from "lucide-react";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../../firebase";
import { authAPI } from "../../services/api";
import { useAuthStore } from "../../store/authStore";

const FIREBASE_ERRORS = {
  "auth/user-not-found": "No account found with this email.",
  "auth/wrong-password": "Incorrect password. Please try again.",
  "auth/invalid-credential": "Invalid email or password.",
  "auth/invalid-email": "Please enter a valid email address.",
  "auth/user-disabled": "This account has been disabled. Contact support.",
  "auth/too-many-requests": "Too many failed attempts. Please try again later.",
  "auth/network-request-failed": "Network error. Please check your connection.",
};

export default function LoginForm() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [form, setForm] = useState({ email: "", password: "" });
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!form.email || !form.password) {
      setError("Email and password are required.");
      return;
    }

    setLoading(true);
    try {
      console.log("Login attempt:", form.email);

      // Step 1: Authenticate with Firebase (password lives in Firebase, not our DB)
      const credential = await signInWithEmailAndPassword(auth, form.email, form.password);
      const firebaseUser = credential.user;
      console.log("Firebase login success, uid:", firebaseUser.uid);

      // Step 2: Upsert user row in our DB using the verified Firebase token
      await authAPI.register({
        full_name: firebaseUser.displayName || "User",
        email: firebaseUser.email,
        firebase_uid: firebaseUser.uid,
      });

      // Step 3: Fetch the full DB user profile
      const res = await authAPI.me();
      console.log("User found:", res.data.user !== null);
      setAuth(firebaseUser, res.data.user);

      toast.success(`Welcome back, ${res.data.user.full_name}!`);
      navigate("/dashboard");
    } catch (err) {
      // Map Firebase error codes to friendly messages
      const code = err?.code || "";
      const msg = FIREBASE_ERRORS[code] || err?.response?.data?.error || "Login failed. Please try again.";
      console.error("Login error:", code, err.message);
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      <div className="form-group">
        <label className="form-label">Email</label>
        <div style={{ position: "relative" }}>
          <Mail size={15} style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
          <input
            id="login-email"
            className="form-input"
            type="email"
            placeholder="you@example.com"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            style={{ paddingLeft: 36 }}
            autoComplete="email"
          />
        </div>
      </div>
      <div className="form-group">
        <label className="form-label">Password</label>
        <div style={{ position: "relative" }}>
          <Lock size={15} style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
          <input
            id="login-password"
            className="form-input"
            type={showPw ? "text" : "password"}
            placeholder="Your password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            style={{ paddingLeft: 36, paddingRight: 40 }}
            autoComplete="current-password"
          />
          <button
            type="button"
            onClick={() => setShowPw(!showPw)}
            style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)" }}
            aria-label={showPw ? "Hide password" : "Show password"}
          >
            {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
          </button>
        </div>
      </div>
      {error && <p className="form-error">{error}</p>}
      <button id="login-submit" type="submit" className="btn btn-primary btn-lg" disabled={loading} style={{ marginTop: 4 }}>
        {loading ? <span className="spinner" /> : <>Sign In <ArrowRight size={16} /></>}
      </button>
      <p style={{ textAlign: "center", fontSize: 13, color: "var(--text-muted)" }}>
        Don't have an account? <Link to="/register" style={{ color: "var(--primary-light)", fontWeight: 600 }}>Sign up free</Link>
      </p>
    </form>
  );
}
