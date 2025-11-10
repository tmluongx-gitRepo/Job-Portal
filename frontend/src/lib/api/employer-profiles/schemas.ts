/**
 * Employer Profile Zod schemas
 * Matches backend Pydantic models
 */
import { z } from "zod";

export const EmployerProfileBaseSchema = z.object({
  company_name: z.string().min(1),
  company_website: z.string().url().nullable().optional(),
  company_logo_url: z.string().url().nullable().optional(),
  industry: z.string().nullable().optional(),
  company_size: z.string().nullable().optional(),
  location: z.string().nullable().optional(),
  description: z.string().nullable().optional(),
  founded_year: z
    .number()
    .int()
    .min(1800)
    .max(new Date().getFullYear())
    .nullable()
    .optional(),
  contact_email: z.string().email().nullable().optional(),
  contact_phone: z.string().nullable().optional(),
  benefits_offered: z.array(z.string()).optional(),
  company_culture: z.string().nullable().optional(),
});

export const EmployerProfileCreateSchema = EmployerProfileBaseSchema.extend({
  user_id: z.string(),
});

export const EmployerProfileUpdateSchema = EmployerProfileBaseSchema.partial();

export const EmployerProfileResponseSchema = EmployerProfileBaseSchema.extend({
  id: z.string(),
  user_id: z.string(),
  benefits_offered: z.array(z.string()).default([]),
  jobs_posted_count: z.number().int().nonnegative().default(0),
  active_jobs_count: z.number().int().nonnegative().default(0),
  verified: z.boolean().default(false),
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
});
