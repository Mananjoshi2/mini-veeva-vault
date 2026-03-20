import React from "react";
import { DocumentStatus } from "../api/documents";

export default function StatusBadge({ status }: { status: DocumentStatus }) {
  const color =
    status === "Approved"
      ? "#15803d"
      : status === "Rejected"
        ? "#b91c1c"
        : status === "Submitted"
          ? "#1d4ed8"
          : "#6b7280";

  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 10px",
        borderRadius: 999,
        background: `${color}1f`,
        border: `1px solid ${color}55`,
        color,
        fontSize: 12,
      }}
    >
      {status}
    </span>
  );
}

