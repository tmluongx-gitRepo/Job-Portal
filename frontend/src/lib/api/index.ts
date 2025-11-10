/**
 * Main API barrel export
 *
 * Usage:
 *   import { api } from '@/lib/api';
 *   import type { User, Job } from '@/lib/api';
 *
 *   const jobs = await api.jobs.search({ query: 'engineer' });
 */

// Export error classes and utilities
export { ApiError, ValidationError, API_URL } from "./client";

// Export all API functions
export { userApi } from "./users";
export { jobApi } from "./jobs";
export { applicationApi } from "./applications";
export { jobSeekerProfileApi } from "./job-seeker-profiles";
export { employerProfileApi } from "./employer-profiles";
export { recommendationApi } from "./recommendations";

// Export all TypeScript types
export type * from "./users/types";
export type * from "./jobs/types";
export type * from "./applications/types";
export type * from "./job-seeker-profiles/types";
export type * from "./employer-profiles/types";
export type * from "./recommendations/types";

// Export all Zod schemas (for advanced usage)
export * as UserSchemas from "./users/schemas";
export * as JobSchemas from "./jobs/schemas";
export * as ApplicationSchemas from "./applications/schemas";
export * as JobSeekerProfileSchemas from "./job-seeker-profiles/schemas";
export * as EmployerProfileSchemas from "./employer-profiles/schemas";
export * as RecommendationSchemas from "./recommendations/schemas";

// Unified API object for convenience
import { userApi } from "./users";
import { jobApi } from "./jobs";
import { applicationApi } from "./applications";
import { jobSeekerProfileApi } from "./job-seeker-profiles";
import { employerProfileApi } from "./employer-profiles";
import { recommendationApi } from "./recommendations";

export const api = {
  users: userApi,
  jobs: jobApi,
  applications: applicationApi,
  jobSeekerProfiles: jobSeekerProfileApi,
  employerProfiles: employerProfileApi,
  recommendations: recommendationApi,
};
