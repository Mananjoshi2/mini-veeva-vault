import { http } from "./http";
import { AuthUser, setToken } from "../auth/auth";

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
  user: AuthUser;
};

export async function login(email: string, password: string): Promise<TokenResponse> {
  const res = await http.post<TokenResponse>("/api/auth/login", { email, password });
  setToken(res.data.access_token);
  return res.data;
}

export async function signup(email: string, password: string, role?: string): Promise<TokenResponse> {
  const res = await http.post<TokenResponse>("/api/auth/signup", { email, password, role: role ?? null });
  setToken(res.data.access_token);
  return res.data;
}

