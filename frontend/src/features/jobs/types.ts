/**
 * Job feature type definitions
 */
import type { Job as ApiJob } from "@/lib/api";

/**
 * UI-friendly job type (transformed from API response)
 */
export interface UIJob {
  id: string;
  title: string;
  company: string;
  location: string;
  type: string;
  salary: string | null;
  posted: string;
  description: string;
  requirements: string[];
  benefits: string[];
  values: string[];
  cultureFit: string[];
  hasApplied?: boolean;
  appliedDate?: string;
}

/**
 * Job search params
 */
export interface JobSearchParams {
  query?: string;
  location?: string;
  jobType?: string;
  remoteOk?: boolean;
  skills?: string[];
  minSalary?: number;
  maxSalary?: number;
}

/**
 * Job filters state
 */
export interface JobFilters {
  jobType: string;
  salaryRange: string;
  companyValues: string;
  postedDate: string;
}

/**
 * Re-export API job type for convenience
 */
export type { ApiJob };
