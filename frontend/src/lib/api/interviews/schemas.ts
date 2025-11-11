/**
 * Interview Zod schemas
 * Matches backend Pydantic models
 */
import { z } from "zod";

export const InterviewCreateSchema = z.object({
  application_id: z.string(),
  interview_type: z.enum([
    "phone",
    "video",
    "in-person",
    "technical",
    "behavioral",
    "panel",
  ]),
  scheduled_date: z.coerce.date(),
  duration_minutes: z.number().int().min(15).max(480),
  timezone: z.string(),
  location: z.string().nullable().optional(),
  interviewer_name: z.string().nullable().optional(),
  interviewer_email: z.string().email().nullable().optional(),
  interviewer_phone: z.string().nullable().optional(),
  notes: z.string().nullable().optional(),
  internal_notes: z.string().nullable().optional(),
});

export const InterviewUpdateSchema = z.object({
  scheduled_date: z.coerce.date().optional(),
  duration_minutes: z.number().int().min(15).max(480).optional(),
  timezone: z.string().optional(),
  location: z.string().nullable().optional(),
  interviewer_name: z.string().nullable().optional(),
  interviewer_email: z.string().email().nullable().optional(),
  interviewer_phone: z.string().nullable().optional(),
  notes: z.string().nullable().optional(),
  internal_notes: z.string().nullable().optional(),
});

export const InterviewCancelSchema = z.object({
  reason: z.string().min(1, "Cancellation reason is required"),
});

export const InterviewCompleteSchema = z.object({
  feedback: z.string().nullable().optional(),
  rating: z.number().int().min(1).max(5).nullable().optional(),
  next_step: z.string().nullable().optional(),
});

export const InterviewResponseSchema = z.object({
  id: z.string(),
  application_id: z.string(),
  job_id: z.string(),
  job_seeker_id: z.string(),
  employer_id: z.string(),
  interview_type: z.string(),
  scheduled_date: z.coerce.date(),
  duration_minutes: z.number().int(),
  timezone: z.string(),
  location: z.string().nullable().optional(),
  interviewer_name: z.string().nullable().optional(),
  interviewer_email: z.string().nullable().optional(),
  interviewer_phone: z.string().nullable().optional(),
  notes: z.string().nullable().optional(),
  internal_notes: z.string().nullable().optional(),
  status: z.enum([
    "scheduled",
    "rescheduled",
    "completed",
    "cancelled",
    "no_show",
  ]),
  feedback: z.string().nullable().optional(),
  rating: z.number().int().nullable().optional(),
  reminder_sent: z.boolean(),
  cancelled_by: z.string().nullable().optional(),
  cancelled_reason: z.string().nullable().optional(),
  rescheduled_from: z.coerce.date().nullable().optional(),
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
  // Populated fields
  job_title: z.string().nullable().optional(),
  company: z.string().nullable().optional(),
  job_seeker_name: z.string().nullable().optional(),
  job_seeker_email: z.string().nullable().optional(),
});

export const InterviewListResponseSchema = z.object({
  interviews: z.array(InterviewResponseSchema),
  total: z.number().int(),
});

