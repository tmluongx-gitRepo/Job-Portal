/**
 * User TypeScript types
 * Inferred from Zod schemas
 */
import { z } from 'zod';
import { UserResponseSchema, UserCreateSchema, UserUpdateSchema } from './schemas';

export type User = z.infer<typeof UserResponseSchema>;
export type UserCreate = z.infer<typeof UserCreateSchema>;
export type UserUpdate = z.infer<typeof UserUpdateSchema>;
