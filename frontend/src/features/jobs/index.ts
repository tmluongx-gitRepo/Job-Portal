/**
 * Jobs feature barrel export
 * Import everything from this file
 */

// Hooks
export { useJobs } from "./hooks/useJobs";
export { useJobSearch } from "./hooks/useJobSearch";

// Utils
export { calculateTimeAgo, formatDate, isRecent } from "./utils/dateHelpers";
export {
  formatSalary,
  transformJobForUI,
  transformJobsForUI,
  extractJobTypes,
  extractLocations,
} from "./utils/jobTransformers";

// Types
export type { UIJob, JobSearchParams, JobFilters, ApiJob } from "./types";
