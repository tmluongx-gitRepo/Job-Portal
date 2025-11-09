/**
 * Recommendation Zod schemas
 * Matches backend Pydantic models
 */
import { z } from "zod";

export const RecommendationFactorsSchema = z.object({
  skills_match: z.number().min(0).max(100).optional(),
  location_match: z.number().min(0).max(100).optional(),
  salary_match: z.number().min(0).max(100).optional(),
  experience_match: z.number().min(0).max(100).optional(),
  education_match: z.number().min(0).max(100).optional(),
});

export const RecommendationCreateSchema = z.object({
  job_seeker_id: z.string(),
  job_id: z.string(),
  match_percentage: z.number().min(0).max(100),
  reasoning: z.string(),
  factors: RecommendationFactorsSchema,
  ai_generated: z.boolean().default(true),
});

export const RecommendationUpdateSchema = z.object({
  viewed: z.boolean().optional(),
  dismissed: z.boolean().optional(),
  applied: z.boolean().optional(),
});

export const RecommendationResponseSchema = z.object({
  id: z.string(),
  job_seeker_id: z.string(),
  job_id: z.string(),
  match_percentage: z.number().min(0).max(100),
  reasoning: z.string(),
  factors: RecommendationFactorsSchema,
  ai_generated: z.boolean().default(true),
  viewed: z.boolean().default(false),
  dismissed: z.boolean().default(false),
  applied: z.boolean().default(false),
  created_at: z.coerce.date(),
});
