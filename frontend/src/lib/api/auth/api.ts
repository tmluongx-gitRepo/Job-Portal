/**
 * Authentication API functions
 */
import { z } from "zod";
import { apiRequest } from "../client";
import { setAuthTokens, clearAuth, type AuthTokens } from "../../auth";

// Auth schemas matching backend
const UserSignUpSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  account_type: z.enum(["job_seeker", "employer"]),
  full_name: z.string().nullable().optional(),
});

const UserSignInSchema = z.object({
  email: z.string().email(),
  password: z.string(),
});

const UserInfoSchema = z.object({
  id: z.string(),
  email: z.string(),
  account_type: z.string().nullable().optional(),
  email_verified: z.boolean().optional(),
  provider: z.string().optional(),
  created_at: z.string().nullable().optional(),
});

const TokenResponseSchema = z.object({
  access_token: z.string(),
  token_type: z.string().default("bearer"),
  expires_in: z.number(),
  refresh_token: z.string(),
  user: UserInfoSchema,
});

const MessageResponseSchema = z.object({
  message: z.string(),
});

export const authApi = {
  /**
   * Register a new user
   * Stores tokens automatically on success
   */
  async register(data: z.infer<typeof UserSignUpSchema>) {
    const response = await apiRequest<
      | z.infer<typeof TokenResponseSchema>
      | {
          message: string;
          user_id: string;
          email: string;
          email_confirmation_required: boolean;
        }
    >("/api/auth/register", {
      method: "POST",
      requestSchema: UserSignUpSchema,
      responseSchema: z.union([
        TokenResponseSchema,
        z.object({
          message: z.string(),
          user_id: z.string(),
          email: z.string(),
          email_confirmation_required: z.boolean(),
        }),
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
  async login(data: z.infer<typeof UserSignInSchema>) {
    const response = await apiRequest<z.infer<typeof TokenResponseSchema>>(
      "/api/auth/login",
      {
        method: "POST",
        requestSchema: UserSignInSchema,
        responseSchema: TokenResponseSchema,
        body: data,
      }
    );

    // Store tokens
    setAuthTokens(response);

    return response;
  },

  /**
   * Logout current user
   * Clears stored tokens
   */
  async logout() {
    try {
      await apiRequest<z.infer<typeof MessageResponseSchema>>(
        "/api/auth/logout",
        {
          method: "POST",
          responseSchema: MessageResponseSchema,
        }
      );
    } finally {
      // Always clear local tokens even if API call fails
      clearAuth();
    }
  },

  /**
   * Get current user info
   */
  async getCurrentUser() {
    return apiRequest<z.infer<typeof UserInfoSchema>>("/api/auth/me", {
      method: "GET",
      responseSchema: UserInfoSchema,
    });
  },

  /**
   * Refresh access token
   * Note: Backend expects refresh_token as a string body parameter
   */
  async refreshToken(refreshToken: string) {
    // Backend expects refresh_token as a plain string in the body
    const response = await apiRequest<z.infer<typeof TokenResponseSchema>>(
      "/api/auth/refresh",
      {
        method: "POST",
        responseSchema: TokenResponseSchema,
        body: refreshToken, // Send as plain string
      }
    );

    // Store new tokens
    setAuthTokens(response);

    return response;
  },
};
