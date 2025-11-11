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
} from "./schemas";

export type Interview = z.infer<typeof InterviewResponseSchema>;
export type InterviewCreate = z.infer<typeof InterviewCreateSchema>;
export type InterviewUpdate = z.infer<typeof InterviewUpdateSchema>;
export type InterviewCancel = z.infer<typeof InterviewCancelSchema>;
export type InterviewComplete = z.infer<typeof InterviewCompleteSchema>;
export type InterviewListResponse = z.infer<typeof InterviewListResponseSchema>;

export type InterviewType =
  | "phone"
  | "video"
  | "in-person"
  | "technical"
  | "behavioral"
  | "panel";

export type InterviewStatus =
  | "scheduled"
  | "rescheduled"
  | "completed"
  | "cancelled"
  | "no_show";
