import { jwtDecode } from "jwt-decode";

export type UserRole = "Researcher" | "Reviewer" | "Admin";

export type AuthUser = {
  id: string;
  email?: string;
  role: UserRole;
};

const TOKEN_KEY = "mvault_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function getCurrentUser(): AuthUser | null {
  const token = getToken();
  if (!token) return null;
  try {
    const decoded = jwtDecode<{ sub: string; role: UserRole }>(token);
    return { id: decoded.sub, role: decoded.role };
  } catch {
    return null;
  }
}

