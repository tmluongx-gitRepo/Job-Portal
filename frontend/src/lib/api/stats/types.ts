/**
 * Stats/Analytics TypeScript types
 * Inferred from Zod schemas
 */
import { z } from "zod";
import {
  TopJobStatsSchema,
  JobAnalyticsResponseSchema,
  EmployerJobStatsResponseSchema,
  JobSeekerApplicationStatsResponseSchema,
} from "./schemas";

export type TopJobStats = z.infer<typeof TopJobStatsSchema>;
export type JobAnalyticsResponse = z.infer<typeof JobAnalyticsResponseSchema>;
export type EmployerJobStatsResponse = z.infer<
  typeof EmployerJobStatsResponseSchema
>;
export type JobSeekerApplicationStatsResponse = z.infer<
  typeof JobSeekerApplicationStatsResponseSchema
>;
