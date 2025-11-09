/**
 * User Zod schemas
 * Matches backend Pydantic models
 */
import { z } from 'zod';

export const UserBaseSchema = z.object({
  email: z.string().email(),
  account_type: z.enum(['job_seeker', 'employer']).default('job_seeker'),
});

export const UserCreateSchema = UserBaseSchema;

export const UserUpdateSchema = z.object({
  email: z.string().email().optional(),
  account_type: z.enum(['job_seeker', 'employer']).optional(),
});

export const UserResponseSchema = UserBaseSchema.extend({
  id: z.string(),
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
});
