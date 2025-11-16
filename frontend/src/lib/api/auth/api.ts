/**
 * Authentication API functions
 */
import { z } from "zod";
import { apiRequest } from "../client";
import { setAuthTokens, clearAuth, type AuthTokens } from "../../auth";
import {
  UserSignUpSchema,
  UserSignInSchema,
  TokenResponseSchema,
  CurrentUserSchema,
  EmailConfirmationResponseSchema,
  MessageResponseSchema,
} from "./schemas";
import type {
  UserSignUp,
  UserSignIn,
  TokenResponse,
  CurrentUser,
  EmailConfirmationResponse,
  MessageResponse,
} from "./types";

export const authApi = {
  /**
   * Register a new user
   * Stores tokens automatically on success
   * Returns either TokenResponse or EmailConfirmationResponse
   */
  async register(
    data: UserSignUp
  ): Promise<TokenResponse | EmailConfirmationResponse> {
    const response = await apiRequest<
      TokenResponse | EmailConfirmationResponse
    >("/api/auth/register", {
      method: "POST",
      requestSchema: UserSignUpSchema,
      responseSchema: z.union([
        TokenResponseSchema,
        EmailConfirmationResponseSchema,
      ]),
      body: data,
    });

    // If we got tokens, store them
    if ("access_token" in response) {
      setAuthTokens(response as AuthTokens);
    }

    return response;
  },

  /**
   * Login with email and password
   * Stores tokens automatically on success
   */
  async login(data: UserSignIn): Promise<TokenResponse> {
    const response = await apiRequest<TokenResponse>("/api/auth/login", {
      method: "POST",
      requestSchema: UserSignInSchema,
      responseSchema: TokenResponseSchema,
      body: data,
    });

    // Store tokens
    setAuthTokens(response);

    return response;
  },

  /**
   * Logout current user
   * Clears stored tokens
   */
  async logout(): Promise<MessageResponse> {
    try {
      await apiRequest<MessageResponse>("/api/auth/logout", {
        method: "POST",
        responseSchema: MessageResponseSchema,
      });
    } finally {
      // Always clear local tokens even if API call fails
      clearAuth();
    }

    return { message: "Successfully logged out" };
  },

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<CurrentUser> {
    return apiRequest<CurrentUser>("/api/auth/me", {
      method: "GET",
      responseSchema: CurrentUserSchema,
    });
  },

  /**
   * Refresh access token
   * Note: Backend expects refresh_token as a plain string in the body
   */
  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    // Backend expects refresh_token as a plain string in the body
    const response = await apiRequest<TokenResponse>("/api/auth/refresh", {
      method: "POST",
      responseSchema: TokenResponseSchema,
      body: refreshToken, // Send as plain string
    });

    // Store new tokens
    setAuthTokens(response);

    return response;
  },
};


