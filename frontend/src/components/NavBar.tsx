import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { clearToken, getCurrentUser } from "../auth/auth";

export default function NavBar() {
  const user = getCurrentUser();
  const showAuditLogs = user?.role === "Reviewer" || user?.role === "Admin";
  const navigate = useNavigate();

  function logout() {
    clearToken();
    navigate("/login");
  }

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "12px 16px",
        borderBottom: "1px solid #e5e7eb",
      }}
    >
      <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
        <div style={{ fontWeight: 700 }}>Mini Veeva Vault</div>
        <Link to="/dashboard" style={{ textDecoration: "none" }}>
          Dashboard
        </Link>
        {showAuditLogs ? (
          <Link to="/audit-logs" style={{ textDecoration: "none" }}>
            Audit Logs
          </Link>
        ) : null}
      </div>

      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        {user ? (
          <>
            <span style={{ fontSize: 13 }}>Role: {user.role}</span>
            <button onClick={logout}>Logout</button>
          </>
        ) : null}
      </div>
    </div>
  );
}

