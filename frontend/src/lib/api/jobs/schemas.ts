/**
 * Job Zod schemas
 * Matches backend Pydantic models
 */
import { z } from "zod";

export const JobBaseSchema = z.object({
  title: z.string().min(1),
  company: z.string().min(1),
  description: z.string().min(1),
  requirements: z.string().nullable().optional(),
  responsibilities: z.array(z.string()).default([]),
  location: z.string().min(1),
  job_type: z.string(), // "Full-time", "Part-time", "Contract", "Internship"
  remote_ok: z.boolean().default(false),
  salary_min: z.number().int().nonnegative().nullable().optional(),
  salary_max: z.number().int().nonnegative().nullable().optional(),
  experience_required: z.string().nullable().optional(),
  education_required: z.string().nullable().optional(),
  industry: z.string().nullable().optional(),
  company_size: z.string().nullable().optional(),
  benefits: z.array(z.string()).default([]),
  skills_required: z.array(z.string()).default([]),
  application_deadline: z.coerce.date().nullable().optional(),
});

export const JobCreateSchema = JobBaseSchema;

export const JobUpdateSchema = z.object({
  title: z.string().min(1).optional(),
  company: z.string().min(1).optional(),
  description: z.string().min(1).optional(),
  requirements: z.string().nullable().optional(),
  responsibilities: z.array(z.string()).optional(),
  location: z.string().min(1).optional(),
  job_type: z.string().optional(),
  remote_ok: z.boolean().optional(),
  salary_min: z.number().int().nonnegative().nullable().optional(),
  salary_max: z.number().int().nonnegative().nullable().optional(),
  experience_required: z.string().nullable().optional(),
  education_required: z.string().nullable().optional(),
  industry: z.string().nullable().optional(),
  company_size: z.string().nullable().optional(),
  benefits: z.array(z.string()).optional(),
  skills_required: z.array(z.string()).optional(),
  application_deadline: z.coerce.date().nullable().optional(),
  is_active: z.boolean().optional(),
});

export const JobResponseSchema = JobBaseSchema.extend({
  id: z.string(),
  is_active: z.boolean().default(true),
  view_count: z.number().int().nonnegative().default(0),
  application_count: z.number().int().nonnegative().default(0),
  posted_by: z.string().nullable().optional(),
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
});
