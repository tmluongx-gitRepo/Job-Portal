/**
 * TypeScript types for authentication API
 * Derived from Zod schemas
 */
import type { z } from "zod";
import {
  UserSignUpSchema,
  UserSignInSchema,
  TokenResponseSchema,
  UserInfoSchema,
  CurrentUserSchema,
  EmailConfirmationResponseSchema,
  MessageResponseSchema,
} from "./schemas";

export type UserSignUp = z.infer<typeof UserSignUpSchema>;
export type UserSignIn = z.infer<typeof UserSignInSchema>;
export type TokenResponse = z.infer<typeof TokenResponseSchema>;
export type UserInfo = z.infer<typeof UserInfoSchema>;
export type CurrentUser = z.infer<typeof CurrentUserSchema>;
export type EmailConfirmationResponse = z.infer<
  typeof EmailConfirmationResponseSchema
>;
export type MessageResponse = z.infer<typeof MessageResponseSchema>;
