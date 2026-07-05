import React from "react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await login(form, mode);
      navigate("/search");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-bg">
      <div className="auth-orb orb-a" aria-hidden="true" />
      <div className="auth-orb orb-b" aria-hidden="true" />
      <div className="auth-orb orb-c" aria-hidden="true" />
      <div className="auth-shell glass-card">
        <aside className="brand-pane">
          <p className="brand-pill">MITHILA MEDICAL SYSTEM</p>
          <h1>Care-Driven Pharmacy Operations with Smart Intelligence</h1>
          <p>
            Unified workflows for inventory, orders, and analytics designed for medical teams that value speed,
            accuracy, and trust.
          </p>
          <div className="brand-stats">
            <div>
              <strong>24x7</strong>
              <span>Operational Visibility</span>
            </div>
            <div>
              <strong>Live</strong>
              <span>Stock + Sales Signals</span>
            </div>
            <div>
              <strong>Secure</strong>
              <span>Role-based Access</span>
            </div>
          </div>
          <div className="brand-grid">
            <div className="brand-chip">
              <strong>Realtime Stock</strong>
              <span>Track low inventory before shortages happen.</span>
            </div>
            <div className="brand-chip">
              <strong>Sales Intelligence</strong>
              <span>Use analytics chat for revenue and demand insights.</span>
            </div>
            <div className="brand-chip">
              <strong>Secure Access</strong>
              <span>Role-based login for customer and admin workflows.</span>
            </div>
          </div>
          <div className="brand-ribbon" aria-hidden="true">
            <span>Inventory</span>
            <span>Sales</span>
            <span>Revenue</span>
            <span>Insights</span>
          </div>
        </aside>

        <section className="auth-card">
          <p className="auth-overline">MITHILA ACCESS PORTAL</p>
          <h2>{mode === "login" ? "Welcome Back" : "Create Your Account"}</h2>
          <p>Sign in to continue seamless operations at Mithila Medical.</p>
          <div className="mode-toggle">
            <button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Login</button>
            <button type="button" className={mode === "signup" ? "active" : ""} onClick={() => setMode("signup")}>Signup</button>
          </div>
          <form onSubmit={onSubmit}>
            {mode === "signup" ? (
              <input placeholder="Full name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
            ) : null}
            <input placeholder="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <input placeholder="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            {error ? <p className="error-text">{error}</p> : null}
            <button type="submit" className="primary-btn auth-submit">{mode === "login" ? "Sign In" : "Create Account"}</button>
          </form>
          <div className="auth-note">
            <span className="auth-dot" />
            <p>Need admin access? Use backend-generated credentials managed by the system administrator.</p>
          </div>
        </section>
      </div>
    </div>
  );
}
