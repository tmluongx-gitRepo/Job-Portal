/**
 * Application TypeScript types
 * Inferred from Zod schemas
 */
import { z } from "zod";
import {
  ApplicationResponseSchema,
  ApplicationCreateSchema,
  ApplicationUpdateSchema,
} from "./schemas";

export type Application = z.infer<typeof ApplicationResponseSchema>;
export type ApplicationCreate = z.infer<typeof ApplicationCreateSchema>;
export type ApplicationUpdate = z.infer<typeof ApplicationUpdateSchema>;
