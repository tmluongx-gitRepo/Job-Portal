/**
 * Application Zod schemas
 * Matches backend Pydantic models
 */
import { z } from 'zod';

export const StatusHistoryEntrySchema = z.object({
  status: z.string(),
  changed_at: z.coerce.date(),
  notes: z.string().nullable().optional(),
  changed_by: z.string().nullable().optional(),
});

export const ApplicationBaseSchema = z.object({
  job_id: z.string(),
  notes: z.string().nullable().optional(),
});

export const ApplicationCreateSchema = ApplicationBaseSchema.extend({
  job_seeker_id: z.string(),
});

export const ApplicationUpdateSchema = z.object({
  status: z.string().optional(),
  notes: z.string().nullable().optional(),
  next_step: z.string().nullable().optional(),
  interview_scheduled_date: z.coerce.date().nullable().optional(),
  rejection_reason: z.string().nullable().optional(),
});

export const ApplicationResponseSchema = ApplicationBaseSchema.extend({
  id: z.string(),
  job_seeker_id: z.string(),
  status: z.string(),
  applied_date: z.coerce.date(),
  next_step: z.string().nullable().optional(),
  interview_scheduled_date: z.coerce.date().nullable().optional(),
  rejection_reason: z.string().nullable().optional(),
  status_history: z.array(StatusHistoryEntrySchema).default([]),
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
});
