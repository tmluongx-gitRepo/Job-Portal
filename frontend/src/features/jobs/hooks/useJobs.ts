/**
 * Custom hook for fetching and managing jobs
 */
import { useState, useEffect, useCallback } from "react";
import { api, ApiError, ValidationError } from "@/lib/api";
import type { Job as ApiJob } from "@/lib/api";
import { transformJobsForUI } from "../utils/jobTransformers";
import type { UIJob } from "../types";

interface UseJobsOptions {
  autoFetch?: boolean;
  limit?: number;
  isActive?: boolean;
}

interface UseJobsReturn {
  jobs: UIJob[];
  rawJobs: ApiJob[];
  loading: boolean;
  error: string | null;
  fetchJobs: () => Promise<void>;
  refetch: () => Promise<void>;
}

/**
 * Hook to fetch and manage jobs list
 */
export function useJobs(options: UseJobsOptions = {}): UseJobsReturn {
  const { autoFetch = true, limit = 100, isActive = true } = options;

  const [rawJobs, setRawJobs] = useState<ApiJob[]>([]);
  const [jobs, setJobs] = useState<UIJob[]>([]);
  const [loading, setLoading] = useState(autoFetch);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // ✅ Make API call
      const fetchedJobs = (await api.jobs.getAll({
        is_active: isActive,
        limit,
      })) as ApiJob[];

      // Store both raw and transformed versions
      setRawJobs(fetchedJobs);
      setJobs(transformJobsForUI(fetchedJobs));

      console.log(`✅ Loaded ${fetchedJobs.length} jobs from database`);
    } catch (err) {
      console.error("❌ Error fetching jobs:", err);

      if (err instanceof ApiError) {
        setError(`Failed to load jobs: ${err.message}`);
      } else if (err instanceof ValidationError) {
        setError("Invalid data received from server");
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setLoading(false);
    }
  }, [isActive, limit]);

  // Auto-fetch on mount if enabled
  useEffect(() => {
    if (autoFetch) {
      void fetchJobs();
    }
  }, [autoFetch, fetchJobs]);

  return {
    jobs,
    rawJobs,
    loading,
    error,
    fetchJobs,
    refetch: fetchJobs,
  };
}
