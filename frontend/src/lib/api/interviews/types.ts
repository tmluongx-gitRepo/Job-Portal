/**
 * Interview TypeScript types
 * Inferred from Zod schemas
 */
import { z } from "zod";
import {
  InterviewResponseSchema,
  InterviewCreateSchema,
  InterviewUpdateSchema,
  InterviewCancelSchema,
  InterviewCompleteSchema,
  InterviewListResponseSchema,
  INTERVIEW_TYPES,
  INTERVIEW_STATUSES,
} from "./schemas";

export type Interview = z.infer<typeof InterviewResponseSchema>;
export type InterviewCreate = z.infer<typeof InterviewCreateSchema>;
export type InterviewUpdate = z.infer<typeof InterviewUpdateSchema>;
export type InterviewCancel = z.infer<typeof InterviewCancelSchema>;
export type InterviewComplete = z.infer<typeof InterviewCompleteSchema>;
export type InterviewListResponse = z.infer<typeof InterviewListResponseSchema>;

// Derive types from centralized enum arrays to avoid drift
export type InterviewType = (typeof INTERVIEW_TYPES)[number];
export type InterviewStatus = (typeof INTERVIEW_STATUSES)[number];
