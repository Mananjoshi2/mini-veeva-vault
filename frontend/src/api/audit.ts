import { http } from "./http";

export type AuditLog = {
  id: number;
  user_id?: string | null;
  action: string;
  timestamp: string;
  entity_type?: string | null;
  entity_id?: string | null;
  details?: Record<string, any> | null;
};

export async function listAuditLogs(params?: {
  entity_type?: string;
  action?: string;
  entity_id?: string;
  user_id?: string;
  from_timestamp?: string;
  to_timestamp?: string;
  limit?: number;
  offset?: number;
}): Promise<AuditLog[]> {
  const res = await http.get<AuditLog[]>("/api/audit-logs", { params });
  return res.data;
}

