import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import { onAuthStateChanged } from "firebase/auth";
import { Toaster } from "react-hot-toast";
import { auth } from "./firebase";
import { useAuthStore } from "./store/authStore";
import { useThemeStore } from "./store/themeStore";
import { authAPI } from "./services/api";
import App from "./App";
import "./styles/global.css";

/**
 * ThemeInitializer
 * Applies the saved theme to <html data-theme="..."> before first render.
 * This prevents a flash of wrong theme color on load.
 */
function ThemeInitializer() {
  const initTheme = useThemeStore((s) => s.initTheme);
  useEffect(() => {
    initTheme();
  }, [initTheme]);
  return null;
}

/**
 * AuthBootstrap
 * Listens to Firebase auth state changes and syncs them to the Zustand store.
 * Shows a loading spinner until Firebase resolves the initial auth state.
 */
function AuthBootstrap({ children }) {
  const [checking, setChecking] = useState(true);
  const { setAuth, logout } = useAuthStore();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          const res = await authAPI.me();
          setAuth(firebaseUser, res.data.user);
        } catch {
          // DB user not found (e.g., account not registered yet) — clear state
          logout();
        }
      } else {
        logout();
      }
      setChecking(false);
    });
    return () => unsubscribe();
  }, []);

  if (checking) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <span className="spinner" style={{ width: 40, height: 40 }} />
      </div>
    );
  }

  return children;
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ThemeInitializer />
    <AuthBootstrap>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "var(--bg-elevated)",
            color: "var(--text-primary)",
            border: "1px solid var(--border-strong)",
            backdropFilter: "blur(12px)",
            fontFamily: "var(--font-body)",
            fontSize: "14px",
          },
          success: {
            iconTheme: { primary: "#10B981", secondary: "#fff" },
          },
          error: {
            iconTheme: { primary: "#EF4444", secondary: "#fff" },
          },
        }}
      />
    </AuthBootstrap>
  </React.StrictMode>
);
