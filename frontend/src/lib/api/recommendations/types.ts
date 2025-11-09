/**
 * Recommendation TypeScript types
 * Inferred from Zod schemas
 */
import { z } from "zod";
import {
  RecommendationResponseSchema,
  RecommendationCreateSchema,
  RecommendationUpdateSchema,
} from "./schemas";

export type Recommendation = z.infer<typeof RecommendationResponseSchema>;
export type RecommendationCreate = z.infer<typeof RecommendationCreateSchema>;
export type RecommendationUpdate = z.infer<typeof RecommendationUpdateSchema>;
