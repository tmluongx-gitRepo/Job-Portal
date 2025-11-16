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
export { ApiError, ValidationError, API_URL, uploadFile } from "./client";

// Export all API functions
export { authApi } from "./auth";
export { userApi } from "./users";
export { jobApi } from "./jobs";
export { applicationApi } from "./applications";
export { interviewApi } from "./interviews";
export { jobSeekerProfileApi } from "./job-seeker-profiles";
export { employerProfileApi } from "./employer-profiles";
export { recommendationApi } from "./recommendations";
export { statsApi } from "./stats";
export { authApi } from "./auth/api";

// Export all TypeScript types
export type * from "./auth/types";
export type * from "./users/types";
export type * from "./jobs/types";
export type * from "./applications/types";
export type * from "./interviews/types";
export type * from "./job-seeker-profiles/types";
export type * from "./employer-profiles/types";
export type * from "./recommendations/types";
export type * from "./stats/types";

// Export all Zod schemas (for advanced usage)
export * as AuthSchemas from "./auth/schemas";
export * as UserSchemas from "./users/schemas";
export * as JobSchemas from "./jobs/schemas";
export * as ApplicationSchemas from "./applications/schemas";
export * as InterviewSchemas from "./interviews/schemas";
export * as JobSeekerProfileSchemas from "./job-seeker-profiles/schemas";
export * as EmployerProfileSchemas from "./employer-profiles/schemas";
export * as RecommendationSchemas from "./recommendations/schemas";
export * as StatsSchemas from "./stats/schemas";

// Unified API object for convenience
import { authApi } from "./auth";
import { userApi } from "./users";
import { jobApi } from "./jobs";
import { applicationApi } from "./applications";
import { interviewApi } from "./interviews";
import { jobSeekerProfileApi } from "./job-seeker-profiles";
import { employerProfileApi } from "./employer-profiles";
import { recommendationApi } from "./recommendations";
import { statsApi } from "./stats";
import { authApi } from "./auth/api";

export const api = {
  auth: authApi,
  users: userApi,
  jobs: jobApi,
  applications: applicationApi,
  interviews: interviewApi,
  jobSeekerProfiles: jobSeekerProfileApi,
  employerProfiles: employerProfileApi,
  recommendations: recommendationApi,
  stats: statsApi,
  auth: authApi,
};
