/**
 * Job Seeker Profile Zod schemas
 * Matches backend Pydantic models
 */
import { z } from 'zod';

export const JobSeekerPreferencesSchema = z.object({
  desired_salary_min: z.number().int().nonnegative().nullable().optional(),
  desired_salary_max: z.number().int().nonnegative().nullable().optional(),
  job_types: z.array(z.string()).default([]),
  remote_ok: z.boolean().default(true),
  preferred_locations: z.array(z.string()).default([]),
  industry_preferences: z.array(z.string()).default([]),
  company_size_preferences: z.array(z.string()).default([]),
  work_environment_preferences: z.array(z.string()).default([]),
});

export const JobSeekerProfileBaseSchema = z.object({
  first_name: z.string().min(1),
  last_name: z.string().min(1),
  email: z.string().email(),
  phone: z.string().nullable().optional(),
  location: z.string().nullable().optional(),
  bio: z.string().nullable().optional(),
  resume_file_url: z.string().url().nullable().optional(),
  resume_file_name: z.string().nullable().optional(),
  skills: z.array(z.string()).default([]),
  experience_years: z.number().int().nonnegative().default(0),
  education_level: z.string().nullable().optional(),
  preferences: JobSeekerPreferencesSchema.nullable().optional(),
});

export const JobSeekerProfileCreateSchema = JobSeekerProfileBaseSchema.extend({
  user_id: z.string(),
});

export const JobSeekerProfileUpdateSchema = z.object({
  first_name: z.string().min(1).optional(),
  last_name: z.string().min(1).optional(),
  email: z.string().email().optional(),
  phone: z.string().nullable().optional(),
  location: z.string().nullable().optional(),
  bio: z.string().nullable().optional(),
  resume_file_url: z.string().url().nullable().optional(),
  resume_file_name: z.string().nullable().optional(),
  skills: z.array(z.string()).optional(),
  experience_years: z.number().int().nonnegative().optional(),
  education_level: z.string().nullable().optional(),
  preferences: JobSeekerPreferencesSchema.nullable().optional(),
});

export const JobSeekerProfileResponseSchema = JobSeekerProfileBaseSchema.extend({
  id: z.string(),
  user_id: z.string(),
  profile_views: z.number().int().nonnegative().default(0),
  profile_completion_percentage: z.number().int().min(0).max(100).nullable().optional(),
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
});
