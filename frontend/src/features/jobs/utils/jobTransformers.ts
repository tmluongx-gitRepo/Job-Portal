/**
 * Transform functions to convert API data to UI format
 */
import type { Job as ApiJob } from "@/lib/api";
import type { UIJob } from "../types";
import { calculateTimeAgo } from "./dateHelpers";

/**
 * Format salary range for display
 */
export function formatSalary(min?: number, max?: number): string | null {
  if (min && max) {
    return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
  }
  if (min) {
    return `$${min.toLocaleString()}+`;
  }
  return null;
}

/**
 * Transform API job to UI job format
 */
export function transformJobForUI(job: ApiJob): UIJob {
  return {
    id: job.id,
    title: job.title,
    company: job.company,
    location: job.location,
    type: job.job_type || "Full-time",
    salary: formatSalary(job.salary_min, job.salary_max),
    posted: calculateTimeAgo(job.created_at),
    description: job.description,
    requirements: job.skills_required || [],
    benefits: job.benefits || [],
    values: [], // Could be extracted from company profile in the future
    cultureFit: job.responsibilities || [],
  };
}

/**
 * Transform multiple jobs
 */
export function transformJobsForUI(jobs: ApiJob[]): UIJob[] {
  return jobs.map(transformJobForUI);
}

/**
 * Extract unique values from jobs (for filters)
 */
export function extractJobTypes(jobs: ApiJob[]): string[] {
  const types = new Set(jobs.map((job) => job.job_type).filter(Boolean));
  return Array.from(types);
}

/**
 * Extract unique locations
 */
export function extractLocations(jobs: ApiJob[]): string[] {
  const locations = new Set(jobs.map((job) => job.location).filter(Boolean));
  return Array.from(locations);
}
