/**
 * Authentication utilities
 * Handles token storage and retrieval for API authentication
 */

const ACCESS_TOKEN_KEY = "auth_access_token";
const REFRESH_TOKEN_KEY = "auth_refresh_token";
const USER_KEY = "auth_user";

export interface AuthUser {
  id: string;
  email: string;
  account_type?: string;
  email_verified?: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  expires_in?: number;
  user: AuthUser;
}

/**
 * Store authentication tokens and user info
 */
export function setAuthTokens(tokens: AuthTokens): void {
  if (typeof window === "undefined") return;

  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  localStorage.setItem(USER_KEY, JSON.stringify(tokens.user));
}

/**
 * Get the access token
 */
export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

/**
 * Get the refresh token
 */
export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Get the current authenticated user
 */
export function getCurrentUser(): AuthUser | null {
  if (typeof window === "undefined") return null;

  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;

  try {
    return JSON.parse(userStr) as AuthUser;
  } catch {
    return null;
  }
}

/**
 * Get the current user ID from stored token/user info
 */
export function getCurrentUserId(): string | null {
  const user = getCurrentUser();
  return user?.id || null;
}

/**
 * Clear authentication tokens and user info
 */
export function clearAuth(): void {
  if (typeof window === "undefined") return;

  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getAccessToken() !== null && getCurrentUserId() !== null;
}

/**
 * Decode JWT token to get user info (without verification)
 * This is a simple decode for getting user ID - backend validates the token
 */
export function decodeToken(
  token: string
): { sub?: string; email?: string } | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;

    const payload = parts[1];
    const decoded = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(decoded) as { sub?: string; email?: string };
  } catch {
    return null;
  }
}
