/**
 * Stats/Analytics Zod schemas
 * Matches backend Pydantic models
 */
import { z } from "zod";

export const TopJobStatsSchema = z.object({
  job_id: z.string(),
  title: z.string(),
  applications: z.number(),
  is_active: z.boolean(),
});

export const JobAnalyticsResponseSchema = z.object({
  job_id: z.string(),
  job_title: z.string(),
  total_applications: z.number(),
  applications_by_status: z.record(z.string(), z.number()),
  recent_applications_count: z.number(),
  interviews_scheduled: z.number(),
  interviews_completed: z.number(),
  avg_interview_rating: z.number().nullable(),
  last_application_date: z.coerce.date().nullable(),
});

export const EmployerJobStatsResponseSchema = z.object({
  employer_id: z.string(),
  total_jobs: z.number(),
  active_jobs: z.number(),
  inactive_jobs: z.number(),
  total_applications_received: z.number(),
  applications_this_week: z.number(),
  top_jobs: z.array(TopJobStatsSchema),
});

export const JobSeekerApplicationStatsResponseSchema = z.object({
  job_seeker_id: z.string(),
  total_applications: z.number(),
  applications_by_status: z.record(z.string(), z.number()),
  applications_this_week: z.number(),
  interviews_scheduled: z.number(),
  interviews_completed: z.number(),
  avg_interview_rating: z.number().nullable(),
  last_application_date: z.coerce.date().nullable(),
});
