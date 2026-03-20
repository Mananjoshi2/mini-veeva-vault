import { http } from "./http";

export type DocumentStatus = "Draft" | "Submitted" | "Approved" | "Rejected";

export type DocumentVersionOut = {
  id: string;
  document_id: string;
  version_number: number;
  status: DocumentStatus;
  original_filename?: string | null;
  created_by: string;
  created_at: string;
  reviewed_by?: string | null;
  review_comment?: string | null;
};

export type DocumentListItem = {
  id: string;
  title: string;
  owner_id: string;
  reviewer_id?: string | null;
  current_version_number: number;
  current_status: DocumentStatus;
  updated_at: string;
};

export type DocumentOut = {
  id: string;
  title: string;
  owner_id: string;
  reviewer_id?: string | null;
  created_at: string;
  updated_at: string;
  current_version: DocumentVersionOut;
};

export type DocumentHistoryEvent = {
  id: string;
  document_version_id: string;
  from_status?: string | null;
  to_status: string;
  action: string;
  actor_user_id: string;
  comment?: string | null;
  created_at: string;
};

export async function listDocuments(): Promise<DocumentListItem[]> {
  const res = await http.get<DocumentListItem[]>("/api/documents");
  return res.data;
}

export async function getDocument(documentId: string): Promise<DocumentOut> {
  const res = await http.get<DocumentOut>(`/api/documents/${documentId}`);
  return res.data;
}

export async function getApprovalQueue(): Promise<DocumentListItem[]> {
  const res = await http.get<DocumentListItem[]>("/api/documents/approvals/queue");
  return res.data;
}

export async function createDocument(payload: {
  title: string;
  reviewer_email?: string | null;
  description?: string | null;
  file: File;
}): Promise<DocumentOut> {
  const form = new FormData();
  form.append("title", payload.title);
  if (payload.reviewer_email) form.append("reviewer_email", payload.reviewer_email);
  if (payload.description) form.append("description", payload.description);
  form.append("document_file", payload.file);
  const res = await http.post<DocumentOut>("/api/documents", form, { headers: { "Content-Type": "multipart/form-data" } });
  return res.data;
}

export async function createNewVersion(payload: { documentId: string; file: File; description?: string | null }): Promise<DocumentVersionOut> {
  const form = new FormData();
  if (payload.description) form.append("description", payload.description);
  form.append("document_file", payload.file);
  const res = await http.post<DocumentVersionOut>(`/api/documents/${payload.documentId}/versions`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function submitDocument(documentId: string, comment?: string | null): Promise<DocumentVersionOut> {
  const res = await http.post<DocumentVersionOut>(`/api/documents/${documentId}/submit`, { comment: comment ?? null });
  return res.data;
}

export async function reviewDocument(
  documentId: string,
  payload: { decision: "Approved" | "Rejected"; comment?: string | null },
): Promise<DocumentVersionOut> {
  const res = await http.post<DocumentVersionOut>(`/api/documents/${documentId}/review`, payload);
  return res.data;
}

export async function getDocumentHistory(documentId: string): Promise<DocumentHistoryEvent[]> {
  const res = await http.get<DocumentHistoryEvent[]>(`/api/documents/${documentId}/history`);
  return res.data;
}

