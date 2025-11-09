/**
 * Job Seeker Profile TypeScript types
 * Inferred from Zod schemas
 */
import { z } from "zod";
import {
  JobSeekerProfileResponseSchema,
  JobSeekerProfileCreateSchema,
  JobSeekerProfileUpdateSchema,
} from "./schemas";

export type JobSeekerProfile = z.infer<typeof JobSeekerProfileResponseSchema>;
export type JobSeekerProfileCreate = z.infer<
  typeof JobSeekerProfileCreateSchema
>;
export type JobSeekerProfileUpdate = z.infer<
  typeof JobSeekerProfileUpdateSchema
>;
