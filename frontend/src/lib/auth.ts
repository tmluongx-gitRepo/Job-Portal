/**
 * Authentication utilities for token storage and management
 * Uses localStorage to persist authentication state
 */

import type { UserInfo } from "./api/auth/types";

// Storage keys
const ACCESS_TOKEN_KEY = "auth_access_token";
const REFRESH_TOKEN_KEY = "auth_refresh_token";
const USER_KEY = "auth_user";

// Re-export UserInfo as AuthUser for convenience
export type AuthUser = UserInfo;

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user: AuthUser;
}

/**
 * Store authentication tokens and user info in localStorage
 */
export function setAuthTokens(tokens: AuthTokens): void {
  if (typeof window === "undefined") return;

  try {
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
    localStorage.setItem(USER_KEY, JSON.stringify(tokens.user));
  } catch (error) {
    console.error("Failed to store auth tokens:", error);
  }
}

/**
 * Get the current access token from localStorage
 */
export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;

  try {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  } catch (error) {
    console.error("Failed to get access token:", error);
    return null;
  }
}

/**
 * Get the current refresh token from localStorage
 */
export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;

  try {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  } catch (error) {
    console.error("Failed to get refresh token:", error);
    return null;
  }
}

/**
 * Get the current user from localStorage
 */
export function getCurrentUser(): AuthUser | null {
  if (typeof window === "undefined") return null;

  try {
    const userStr = localStorage.getItem(USER_KEY);
    // Handle null, undefined, or the string "undefined"
    if (!userStr || userStr === "undefined" || userStr === "null") {
      return null;
    }
    return JSON.parse(userStr) as AuthUser;
  } catch (error) {
    console.error("Failed to get current user:", error);
    // Clear invalid data
    localStorage.removeItem(USER_KEY);
    return null;
  }
}

/**
 * Get the current user ID (MongoDB ObjectId from backend)
 */
export function getCurrentUserId(): string | null {
  const user = getCurrentUser();
  return user?.id || null;
}

/**
 * Clear all authentication data from localStorage
 */
export function clearAuth(): void {
  if (typeof window === "undefined") return;

  try {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } catch (error) {
    console.error("Failed to clear auth:", error);
  }
}

/**
 * Check if user is currently authenticated
 */
export function isAuthenticated(): boolean {
  const token = getAccessToken();
  const user = getCurrentUser();
  return !!(token && user);
}

/**
 * Decode JWT token to get payload (for debugging/validation)
 * Note: This doesn't verify the signature, just decodes the payload
 */
export function decodeToken(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;

    const payload = parts[1];
    const decoded = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(decoded) as Record<string, unknown>;
  } catch (error) {
    console.error("Failed to decode token:", error);
    return null;
  }
}


