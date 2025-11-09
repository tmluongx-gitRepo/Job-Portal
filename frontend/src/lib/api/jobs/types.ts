/**
 * Job TypeScript types
 * Inferred from Zod schemas
 */
import { z } from "zod";
import { JobResponseSchema, JobCreateSchema, JobUpdateSchema } from "./schemas";

export type Job = z.infer<typeof JobResponseSchema>;
export type JobCreate = z.infer<typeof JobCreateSchema>;
export type JobUpdate = z.infer<typeof JobUpdateSchema>;
