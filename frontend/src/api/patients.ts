import { http } from "./http";

export type Patient = {
  patient_id: string;
  treatment: string;
  outcome: string;
  timestamp: string;
};

export async function listPatients(params?: {
  treatment?: string;
  outcome?: string;
  from_timestamp?: string;
  to_timestamp?: string;
  limit?: number;
  offset?: number;
}): Promise<{ items: Patient[]; total?: number }> {
  const res = await http.get<Patient[]>("/api/patients", { params });
  return { items: res.data };
}

