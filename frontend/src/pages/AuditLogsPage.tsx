import React, { useEffect, useState } from "react";
import { listAuditLogs } from "../api/audit";
import { getCurrentUser } from "../auth/auth";
import { shortUserLabel } from "../formatters";

export default function AuditLogsPage() {
  const user = getCurrentUser();
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState("");
  const [entityTypeFilter, setEntityTypeFilter] = useState("");

  async function refresh() {
    if (!user || user.role !== "Admin") return;
    setLoading(true);
    try {
      const data = await listAuditLogs({
        action: actionFilter || undefined,
        entity_type: entityTypeFilter || undefined,
        limit: 200,
      });
      setRows(data);
    } catch {
      setRows([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!user) return null;

  return (
    <div style={{ padding: 16, maxWidth: 1100, margin: "0 auto" }}>
      <h2 style={{ marginTop: 0 }}>Audit Logs</h2>
      {user.role !== "Admin" ? (
        <div style={{ color: "#6b7280" }}>Audit logs are restricted to Admin.</div>
      ) : null}

      <div style={{ display: "flex", gap: 12, marginBottom: 14, alignItems: "end" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <div style={{ fontSize: 13, color: "#6b7280" }}>Action contains</div>
          <input value={actionFilter} onChange={(e) => setActionFilter(e.target.value)} />
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <div style={{ fontSize: 13, color: "#6b7280" }}>Entity Type</div>
          <input value={entityTypeFilter} onChange={(e) => setEntityTypeFilter(e.target.value)} />
        </div>
        <button onClick={refresh} style={{ padding: "10px 12px" }}>
          Refresh
        </button>
      </div>

      {loading ? <div>Loading...</div> : null}
      <div style={{ overflowX: "auto", opacity: user.role !== "Admin" ? 0.6 : 1 }}>
        <table style={{ width: "100%", borderCollapse: "collapse", background: "#fff" }}>
          <thead>
            <tr>
              <th style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb", padding: 8 }}>Timestamp</th>
              <th style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb", padding: 8 }}>User</th>
              <th style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb", padding: 8 }}>Action</th>
              <th style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb", padding: 8 }}>Entity</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td style={{ padding: 8, borderBottom: "1px solid #f3f4f6", fontSize: 12 }}>
                  {new Date(r.timestamp).toLocaleString()}
                </td>
                <td style={{ padding: 8, borderBottom: "1px solid #f3f4f6", fontFamily: "monospace", fontSize: 12 }}>
                  {shortUserLabel(r.user_id)}
                </td>
                <td style={{ padding: 8, borderBottom: "1px solid #f3f4f6" }}>{r.action}</td>
                <td style={{ padding: 8, borderBottom: "1px solid #f3f4f6", fontSize: 12 }}>
                  {r.entity_type ?? "—"} {r.entity_id ? `(${r.entity_id})` : ""}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

