import React, { useEffect, useMemo, useState } from "react";
import { listDocuments, listDocuments as _listDocuments, getApprovalQueue, createDocument, submitDocument, reviewDocument, getDocumentHistory, createNewVersion, DocumentListItem, DocumentHistoryEvent, DocumentStatus } from "../api/documents";
import { listPatients } from "../api/patients";
import { getCurrentUser, UserRole } from "../auth/auth";
import { formatActionLabel, shortUserLabel } from "../formatters";
import PatientTable from "../components/PatientTable";
import StatusBadge from "../components/StatusBadge";

export type Patient = {
  patient_id: string;
  treatment: string;
  outcome: string;
  timestamp: string;
};

type SelectedHistoryState = {
  loading: boolean;
  events: DocumentHistoryEvent[];
};

export default function DashboardPage() {
  const user = getCurrentUser();
  const role = user?.role as UserRole | undefined;

  const [patients, setPatients] = useState<Patient[]>([]);
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [queue, setQueue] = useState<DocumentListItem[]>([]);
  const [loading, setLoading] = useState(true);

  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [history, setHistory] = useState<SelectedHistoryState>({ loading: false, events: [] });

  // Create document form (researcher)
  const [docTitle, setDocTitle] = useState("Regulatory Submission Package");
  const [docReviewerEmail, setDocReviewerEmail] = useState("");
  const [docDescription, setDocDescription] = useState("Demo upload for review workflow.");
  const [docFile, setDocFile] = useState<File | null>(null);

  // New version form (selected document)
  const [newVersionFile, setNewVersionFile] = useState<File | null>(null);
  const [newVersionDescription, setNewVersionDescription] = useState<string | null>(null);

  const selectedDoc = useMemo(() => documents.find((d) => d.id === selectedDocId) ?? null, [documents, selectedDocId]);

  async function refreshAll() {
    setLoading(true);
    try {
      const patRes = await listPatients();
      setPatients(Array.isArray(patRes) ? (patRes as Patient[]) : ((patRes as any).items ?? []));

      const docs = await listDocuments();
      setDocuments(docs);

      if (role === "Reviewer") {
        const q = await getApprovalQueue();
        setQueue(q);
      } else {
        setQueue([]);
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    async function loadHistory() {
      if (!selectedDocId) {
        setHistory({ loading: false, events: [] });
        return;
      }
      setHistory({ loading: true, events: [] });
      try {
        const events = await getDocumentHistory(selectedDocId);
        setHistory({ loading: false, events });
      } catch {
        setHistory({ loading: false, events: [] });
      }
    }
    loadHistory();
  }, [selectedDocId]);

  async function onCreateDocument() {
    if (!docFile) {
      alert("Select a document file");
      return;
    }
    await createDocument({
      title: docTitle,
      reviewer_email: docReviewerEmail,
      description: docDescription,
      file: docFile,
    });
    setDocFile(null);
    await refreshAll();
  }

  async function onSubmitSelected() {
    if (!selectedDoc) return;
    await submitDocument(selectedDoc.id, "Submitted by researcher.");
    await refreshAll();
  }

  async function onCreateNewVersionSelected() {
    if (!selectedDoc) return;
    if (!newVersionFile) {
      alert("Select a file for the new version");
      return;
    }
    await createNewVersion({ documentId: selectedDoc.id, file: newVersionFile, description: newVersionDescription });
    setNewVersionFile(null);
    setNewVersionDescription(null);
    await refreshAll();
  }

  async function onApprove(docId: string) {
    await reviewDocument(docId, { decision: "Approved", comment: "Looks good." });
    await refreshAll();
  }

  async function onReject(docId: string) {
    await reviewDocument(docId, { decision: "Rejected", comment: "Needs additional information." });
    await refreshAll();
  }

  return (
    <div style={{ padding: 16, maxWidth: 1200, margin: "0 auto" }}>
      <h2 style={{ marginTop: 0 }}>Dashboard</h2>

      {loading ? <div>Loading...</div> : null}

      <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: 16, alignItems: "start" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 14, background: "#fff" }}>
            <h3 style={{ marginTop: 0 }}>Patient Records</h3>
            <PatientTable patients={patients} />
          </div>

          <div style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 14, background: "#fff" }}>
            <h3 style={{ marginTop: 0 }}>Document Management</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr>
                      <th style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb", padding: 8 }}>Title</th>
                      <th style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb", padding: 8 }}>Version</th>
                      <th style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb", padding: 8 }}>Status</th>
                      <th style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb", padding: 8 }}>Owner</th>
                      <th style={{ textAlign: "left", borderBottom: "1px solid #e5e7eb", padding: 8 }}>Select</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((d) => (
                      <tr key={d.id}>
                        <td style={{ padding: 8, borderBottom: "1px solid #f3f4f6" }}>{d.title}</td>
                        <td style={{ padding: 8, borderBottom: "1px solid #f3f4f6" }}>{d.current_version_number}</td>
                        <td style={{ padding: 8, borderBottom: "1px solid #f3f4f6" }}>
                          <StatusBadge status={d.current_status as DocumentStatus} />
                        </td>
                        <td style={{ padding: 8, borderBottom: "1px solid #f3f4f6", fontFamily: "monospace", fontSize: 12 }}>
                          {shortUserLabel(d.owner_id)}
                        </td>
                        <td style={{ padding: 8, borderBottom: "1px solid #f3f4f6" }}>
                          <button onClick={() => setSelectedDocId(d.id)}>{selectedDocId === d.id ? "Selected" : "Open"}</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {selectedDoc ? (
                <div style={{ marginTop: 10 }}>
                  <h4 style={{ marginBottom: 8 }}>History Timeline</h4>
                  {history.loading ? <div>Loading history...</div> : <div style={{ marginBottom: 16 }}>
                    <div style={{ marginBottom: 12 }}>
                      <strong>{selectedDoc.title}</strong> <StatusBadge status={selectedDoc.current_status as DocumentStatus} />
                    </div>
                    {history.events.length ? (
                      <div style={{ marginBottom: 14 }}>
                        {history.events.map((e) => (
                          <div key={e.id} style={{ border: "1px solid #e5e7eb", borderRadius: 10, padding: 12, marginBottom: 10, background: "#fff" }}>
                          <div style={{ fontWeight: 700 }}>
                            {formatActionLabel(e.action)}
                          </div>

                          <div style={{ fontSize: 12, opacity: 0.8 }}>
                            ({e.from_status ?? "N/A"} {'->'} {e.to_status})
                          </div>
                            <div style={{ fontSize: 12, opacity: 0.8 }}>
                              {new Date(e.created_at).toLocaleString()} by {shortUserLabel(e.actor_user_id)}
                            </div>
                            {e.comment ? <div style={{ marginTop: 8, fontSize: 13 }}>Comment: {e.comment}</div> : null}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div>No events yet.</div>
                    )}
                  </div>}

                  {user?.role === "Researcher" || user?.role === "Admin" ? (
                    <div style={{ borderTop: "1px solid #e5e7eb", paddingTop: 14 }}>
                      {selectedDoc.current_status === "Draft" && selectedDoc.owner_id === user.id ? (
                        <button onClick={onSubmitSelected} style={{ padding: "10px 12px" }}>Submit for review</button>
                      ) : null}

                      {selectedDoc.owner_id === user.id ? (
                        <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 8 }}>
                          <div style={{ fontSize: 13, color: "#6b7280" }}>Create a new version (Draft)</div>
                          <input type="file" onChange={(e) => setNewVersionFile(e.target.files?.[0] ?? null)} />
                          <input
                            placeholder="New version description (optional)"
                            value={newVersionDescription ?? ""}
                            onChange={(e) => setNewVersionDescription(e.target.value || null)}
                          />
                          <button onClick={onCreateNewVersionSelected} style={{ padding: "10px 12px" }}>Create new version</button>
                        </div>
                      ) : null}
                    </div>
                  ) : null}
                </div>
              ) : (
                <div style={{ marginTop: 16, color: "#6b7280" }}>Select a document to view its history.</div>
              )}
            </div>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 14, background: "#fff" }}>
            <h3 style={{ marginTop: 0 }}>Approval Queue</h3>
            {role === "Reviewer" ? (
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {queue.length ? (
                  queue.map((d) => (
                    <div key={d.id} style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 12 }}>
                      <div style={{ fontWeight: 700, marginBottom: 6 }}>{d.title}</div>
                      <div style={{ marginBottom: 10 }}>
                        Version {d.current_version_number} <StatusBadge status={d.current_status as DocumentStatus} />
                      </div>
                      <div style={{ display: "flex", gap: 8 }}>
                        <button onClick={() => onApprove(d.id)}>Approve</button>
                        <button onClick={() => onReject(d.id)} style={{ background: "#b91c1c", color: "#fff" }}>
                          Reject
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <div style={{ color: "#6b7280" }}>No items awaiting your review.</div>
                )}
              </div>
            ) : (
              <div style={{ color: "#6b7280" }}>Only reviewers see the approval queue.</div>
            )}
          </div>

          <div style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 14, background: "#fff" }}>
            <h3 style={{ marginTop: 0 }}>Create Document</h3>
            {user?.role === "Researcher" || user?.role === "Admin" ? (
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                <input value={docTitle} onChange={(e) => setDocTitle(e.target.value)} placeholder="Document title" />
                <input
                  value={docReviewerEmail}
                  onChange={(e) => setDocReviewerEmail(e.target.value)}
                  placeholder="Reviewer email"
                />
                <input value={docDescription} onChange={(e) => setDocDescription(e.target.value)} placeholder="Description" />
                <input type="file" onChange={(e) => setDocFile(e.target.files?.[0] ?? null)} />
                <button onClick={onCreateDocument} disabled={!docFile} style={{ padding: "10px 12px" }}>
                  Upload + create Draft
                </button>
                <div style={{ color: "#6b7280", fontSize: 13 }}>
                  Files are not stored (metadata only). Use the upload to simulate workflow.
                </div>
              </div>
            ) : (
              <div style={{ color: "#6b7280" }}>Only researchers create documents.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

