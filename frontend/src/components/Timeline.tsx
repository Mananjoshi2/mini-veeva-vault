import React from "react";
import { DocumentHistoryEvent } from "../api/documents";
import { formatActionLabel, shortUserLabel } from "../formatters";

export default function Timeline({ events }: { events: DocumentHistoryEvent[] }) {
  if (!events.length) return <div>No history yet.</div>;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {events.map((e) => (
        <div
          key={e.id}
          style={{
            border: "1px solid #e5e7eb",
            borderRadius: 10,
            padding: 12,
            background: "#ffffff",
          }}
        >
          <div style={{ fontWeight: 700, marginBottom: 6 }}>
            {formatActionLabel(e.action)} ({e.from_status ?? "N/A"} {'->'} {e.to_status})
          </div>
          <div style={{ fontSize: 12, color: "#6b7280" }}>
            {new Date(e.created_at).toLocaleString()} by {shortUserLabel(e.actor_user_id)}
          </div>
          {e.comment ? <div style={{ marginTop: 8, fontSize: 13 }}>Comment: {e.comment}</div> : null}
        </div>
      ))}
    </div>
  );
}

