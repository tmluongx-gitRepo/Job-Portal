/**
 * Custom hook for job search functionality
 */
import { useState, useCallback } from "react";
import { api, ApiError, ValidationError } from "@/lib/api";
import type { Job as ApiJob } from "@/lib/api";
import { transformJobsForUI } from "../utils/jobTransformers";
import type { UIJob, JobSearchParams } from "../types";

interface UseJobSearchReturn {
  jobs: UIJob[];
  rawJobs: ApiJob[];
  loading: boolean;
  error: string | null;
  searchJobs: (params: JobSearchParams) => Promise<void>;
  clearSearch: () => void;
}

/**
 * Hook to handle job search operations
 */
export function useJobSearch(): UseJobSearchReturn {
  const [rawJobs, setRawJobs] = useState<ApiJob[]>([]);
  const [jobs, setJobs] = useState<UIJob[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const searchJobs = useCallback(async (params: JobSearchParams) => {
    setLoading(true);
    setError(null);

    try {
      // ✅ Make search API call
      const searchResults = (await api.jobs.search({
        query: params.query || undefined,
        location: params.location || undefined,
        job_type: params.jobType || undefined,
        remote_ok: params.remoteOk,
        skills: params.skills,
        min_salary: params.minSalary,
        max_salary: params.maxSalary,
        is_active: true,
        limit: 100,
      })) as ApiJob[];

      setRawJobs(searchResults);
      setJobs(transformJobsForUI(searchResults));

      console.log(`✅ Search found ${searchResults.length} jobs`);
    } catch (err) {
      console.error("❌ Search error:", err);

      if (err instanceof ApiError) {
        setError(`Search failed: ${err.message}`);
      } else if (err instanceof ValidationError) {
        setError("Invalid search parameters");
      } else {
        setError("Search failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const clearSearch = useCallback(() => {
    setJobs([]);
    setRawJobs([]);
    setError(null);
  }, []);

  return {
    jobs,
    rawJobs,
    loading,
    error,
    searchJobs,
    clearSearch,
  };
}
