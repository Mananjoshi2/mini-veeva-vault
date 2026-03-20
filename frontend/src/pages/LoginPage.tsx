import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, signup } from "../api/auth";
import { UserRole } from "../auth/auth";

export default function LoginPage() {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("Researcher");
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await signup(email, password, role);
      }
      navigate("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? err?.message ?? "Request failed");
    }
  }

  return (
    <div style={{ maxWidth: 520, margin: "40px auto", padding: 20 }}>
      <h2 style={{ marginBottom: 8 }}>Mini Veeva Vault</h2>
      <div style={{ color: "#6b7280", marginBottom: 20 }}>Clinical trial + document management demo.</div>

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <button onClick={() => setMode("login")} disabled={mode === "login"}>
          Login
        </button>
        <button onClick={() => setMode("signup")} disabled={mode === "signup"}>
          Signup
        </button>
      </div>

      <form onSubmit={onSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>

        {mode === "signup" ? (
          <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            Role (may be restricted by backend)
            <select value={role} onChange={(e) => setRole(e.target.value as UserRole)}>
              <option value="Researcher">Researcher</option>
              <option value="Reviewer">Reviewer</option>
              <option value="Admin">Admin</option>
            </select>
          </label>
        ) : null}

        {error ? <div style={{ color: "#b91c1c" }}>{error}</div> : null}

        <button type="submit" style={{ padding: "10px 14px" }}>
          {mode === "login" ? "Login" : "Create account"}
        </button>
      </form>

      <div style={{ marginTop: 18, color: "#6b7280", fontSize: 13 }}>
        Use an existing account or sign up to continue.
      </div>
    </div>
  );
}

