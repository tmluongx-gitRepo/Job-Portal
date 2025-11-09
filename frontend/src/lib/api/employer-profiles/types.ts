/**
 * Employer Profile TypeScript types
 * Inferred from Zod schemas
 */
import { z } from 'zod';
import {
  EmployerProfileResponseSchema,
  EmployerProfileCreateSchema,
  EmployerProfileUpdateSchema,
} from './schemas';

export type EmployerProfile = z.infer<typeof EmployerProfileResponseSchema>;
export type EmployerProfileCreate = z.infer<typeof EmployerProfileCreateSchema>;
export type EmployerProfileUpdate = z.infer<typeof EmployerProfileUpdateSchema>;
