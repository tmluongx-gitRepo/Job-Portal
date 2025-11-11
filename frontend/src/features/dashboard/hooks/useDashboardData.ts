/**
 * Custom hook for fetching dashboard data
 */
import { useState, useEffect, useCallback } from "react";
import { ApiError, ValidationError } from "@/lib/api";
import type {
  DashboardStats,
  UserApplication,
  JobRecommendation,
} from "../types";

interface UseDashboardDataReturn {
  stats: DashboardStats | null;
  applications: UserApplication[];
  recommendations: JobRecommendation[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Hook to fetch all dashboard data
 *
 * TODO: Replace with real API calls when user authentication is implemented
 */
export function useDashboardData(userId?: string): UseDashboardDataReturn {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [_applications] = useState<UserApplication[]>([]);
  const [_recommendations] = useState<JobRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = useCallback(async () => {
    if (!userId) {
      // No user ID - use mock data or wait for auth
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // ✅ When auth is ready, fetch real data
      // const [userStats, userApps, userRecs] = await Promise.all([
      //   api.users.getStats(userId),
      //   api.applications.getAll({ job_seeker_id: userId, limit: 10 }),
      //   api.recommendations.getForJobSeeker(userId, { limit: 10 }),
      // ]);

      // For now, set mock data
      setStats({
        applicationsThisWeek: 3,
        interviewsScheduled: 1,
        profileViews: 12,
        newMatches: 5,
      });

      console.log("✅ Dashboard data loaded");
    } catch (err) {
      console.error("❌ Error fetching dashboard data:", err);

      if (err instanceof ApiError) {
        setError(`Failed to load dashboard: ${err.message}`);
      } else if (err instanceof ValidationError) {
        setError("Invalid data received");
      } else {
        setError("Failed to load dashboard");
      }
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    void fetchDashboardData();
  }, [fetchDashboardData]);

  return {
    stats,
    applications: _applications,
    recommendations: _recommendations,
    loading,
    error,
    refetch: fetchDashboardData,
  };
}
