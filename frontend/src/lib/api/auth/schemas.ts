/**
 * Zod schemas for authentication API
 * These match the backend Pydantic schemas in backend/app/auth/auth_schemas.py
 */
import { z } from "zod";

// UserSignUp schema - matches backend UserSignUp
export const UserSignUpSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  account_type: z.enum(["job_seeker", "employer"], {
    errorMap: () => ({
      message: "Account type must be 'job_seeker' or 'employer'",
    }),
  }),
  full_name: z.string().nullable().optional(),
});

// UserSignIn schema - matches backend UserSignIn
export const UserSignInSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});

// UserInfo schema - matches backend UserInfo
export const UserInfoSchema = z.object({
  id: z.string(),
  email: z.string(),
  account_type: z.string().nullable().optional(),
  email_verified: z.boolean().optional().default(false),
  provider: z.string().optional().default("email"),
  created_at: z.string().nullable().optional(),
});

// TokenResponse schema - matches backend TokenResponse
export const TokenResponseSchema = z.object({
  access_token: z.string(),
  token_type: z.string().default("bearer"),
  expires_in: z.number(),
  refresh_token: z.string(),
  user: UserInfoSchema,
});

// CurrentUser schema - matches backend CurrentUser
export const CurrentUserSchema = z.object({
  id: z.string(),
  email: z.string(),
  account_type: z.string().nullable().optional(),
  provider: z.string(),
  email_verified: z.boolean(),
  role: z.string(),
  metadata: z.record(z.unknown()).optional().default({}),
});

// Email confirmation response schema (alternative response from register endpoint)
export const EmailConfirmationResponseSchema = z.object({
  message: z.string(),
  user_id: z.string(),
  email: z.string(),
  email_confirmation_required: z.literal(true),
});

// MessageResponse schema - matches backend MessageResponse
export const MessageResponseSchema = z.object({
  message: z.string(),
});
