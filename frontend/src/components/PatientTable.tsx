import React from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import type { ChartData } from "chart.js";
import type { Patient } from "../pages/DashboardPage";

// Needed for Chart.js v4
ChartJS.register(ArcElement, Tooltip, Legend);

export default function PatientTable({ patients }: { patients: Patient[] }) {
  const outcomes = Object.entries(
    patients.reduce<Record<string, number>>((acc, p) => {
      acc[p.outcome] = (acc[p.outcome] ?? 0) + 1;
      return acc;
    }, {}),
  );

  const chartData: ChartData<"pie"> = {
    labels: outcomes.map(([k]) => k),
    datasets: [
      {
        data: outcomes.map(([, v]) => v),
        backgroundColor: ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0ea5e9"],
      },
    ],
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <div style={{ width: 360, maxWidth: "100%" }}>
        <Pie data={chartData} />
      </div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb", padding: 8 }}>Patient ID</th>
              <th style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb", padding: 8 }}>Treatment</th>
              <th style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb", padding: 8 }}>Outcome</th>
              <th style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb", padding: 8 }}>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {patients.map((p) => (
              <tr key={p.patient_id}>
                <td style={{ padding: 8, borderBottom: "1px solid #f3f4f6", fontFamily: "monospace", fontSize: 12 }}>
                  {p.patient_id}
                </td>
                <td style={{ padding: 8, borderBottom: "1px solid #f3f4f6" }}>{p.treatment}</td>
                <td style={{ padding: 8, borderBottom: "1px solid #f3f4f6" }}>{p.outcome}</td>
                <td style={{ padding: 8, borderBottom: "1px solid #f3f4f6", fontSize: 12 }}>
                  {new Date(p.timestamp).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

