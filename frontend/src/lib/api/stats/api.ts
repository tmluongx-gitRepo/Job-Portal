/**
 * Stats/Analytics API functions
 */
import { apiRequest } from "../client";
import {
  JobAnalyticsResponseSchema,
  EmployerJobStatsResponseSchema,
  JobSeekerApplicationStatsResponseSchema,
} from "./schemas";

export const statsApi = {
  /**
   * Get analytics for a specific job posting
   * @param jobId - The job ID
   * @returns Job analytics including applications and interview metrics
   */
  async getJobAnalytics(jobId: string) {
    return apiRequest(`/api/jobs/${jobId}/analytics`, {
      method: "GET",
      responseSchema: JobAnalyticsResponseSchema,
    });
  },

  /**
   * Get job management statistics for an employer
   * @param userId - The employer user ID
   * @returns Employer job stats including total jobs and applications
   */
  async getEmployerJobStats(userId: string) {
    return apiRequest(`/api/employer-profiles/user/${userId}/job-stats`, {
      method: "GET",
      responseSchema: EmployerJobStatsResponseSchema,
    });
  },

  /**
   * Get application statistics for a job seeker
   * @param userId - The job seeker user ID
   * @returns Job seeker application stats including pipeline progress
   */
  async getJobSeekerApplicationStats(userId: string) {
    return apiRequest(
      `/api/job-seeker-profiles/user/${userId}/application-stats`,
      {
        method: "GET",
        responseSchema: JobSeekerApplicationStatsResponseSchema,
      }
    );
  },
};
