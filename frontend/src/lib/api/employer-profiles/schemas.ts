/**
 * Employer Profile Zod schemas
 * Matches backend Pydantic models
 */
import { z } from 'zod';

export const EmployerProfileBaseSchema = z.object({
  company_name: z.string().min(1),
  company_website: z.string().url().nullable().optional(),
  company_description: z.string().nullable().optional(),
  industry: z.string().nullable().optional(),
  company_size: z.string().nullable().optional(),
  founded_year: z.number().int().min(1800).max(new Date().getFullYear()).nullable().optional(),
  headquarters_location: z.string().nullable().optional(),
  contact_email: z.string().email(),
  contact_phone: z.string().nullable().optional(),
  logo_url: z.string().url().nullable().optional(),
});

export const EmployerProfileCreateSchema = EmployerProfileBaseSchema.extend({
  user_id: z.string(),
});

export const EmployerProfileUpdateSchema = EmployerProfileBaseSchema.partial();

export const EmployerProfileResponseSchema = EmployerProfileBaseSchema.extend({
  id: z.string(),
  user_id: z.string(),
  jobs_posted_count: z.number().int().nonnegative().default(0),
  active_jobs_count: z.number().int().nonnegative().default(0),
  verified: z.boolean().default(false),
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
});
