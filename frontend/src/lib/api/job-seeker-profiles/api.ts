/**
 * Job Seeker Profile API functions
 */
import { z } from "zod";
import { ApiError, apiRequest } from "../client";
import type { JobSeekerProfile } from "./types";
import {
  JobSeekerProfileCreateSchema,
  JobSeekerProfileUpdateSchema,
  JobSeekerProfileResponseSchema,
} from "./schemas";

export const jobSeekerProfileApi = {
  async create(data: z.infer<typeof JobSeekerProfileCreateSchema>) {
    return apiRequest("/api/job-seeker-profiles", {
      method: "POST",
      requestSchema: JobSeekerProfileCreateSchema,
      responseSchema: JobSeekerProfileResponseSchema,
      body: data,
    });
  },

  async getAll(params?: { skip?: number; limit?: number }) {
    const query = new URLSearchParams();
    if (params?.skip) query.set("skip", params.skip.toString());
    if (params?.limit) query.set("limit", params.limit.toString());

    return apiRequest(`/api/job-seeker-profiles?${query}`, {
      method: "GET",
      responseSchema: z.array(JobSeekerProfileResponseSchema),
    });
  },

  async search(params: {
    skills?: string[];
    location?: string;
    min_experience?: number;
    max_experience?: number;
    skip?: number;
    limit?: number;
  }) {
    const query = new URLSearchParams();
    if (params.skills) {
      params.skills.forEach((skill) => query.append("skills", skill));
    }
    if (params.location) query.set("location", params.location);
    if (params.min_experience !== undefined)
      query.set("min_experience", params.min_experience.toString());
    if (params.max_experience !== undefined)
      query.set("max_experience", params.max_experience.toString());
    if (params.skip) query.set("skip", params.skip.toString());
    if (params.limit) query.set("limit", params.limit.toString());

    return apiRequest(`/api/job-seeker-profiles/search?${query}`, {
      method: "GET",
      responseSchema: z.array(JobSeekerProfileResponseSchema),
    });
  },

  async getById(profileId: string, incrementViews = false) {
    const query = incrementViews ? "?increment_views=true" : "";
    return apiRequest(`/api/job-seeker-profiles/${profileId}${query}`, {
      method: "GET",
      responseSchema: JobSeekerProfileResponseSchema,
    });
  },

  async getByUserId(userId: string): Promise<JobSeekerProfile | null> {
    try {
      return await apiRequest(`/api/job-seeker-profiles/user/${userId}`, {
        method: "GET",
        responseSchema: JobSeekerProfileResponseSchema,
      });
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        return null;
      }
      throw error;
    }
  },

  async update(
    profileId: string,
    data: z.infer<typeof JobSeekerProfileUpdateSchema>
  ) {
    return apiRequest(`/api/job-seeker-profiles/${profileId}`, {
      method: "PUT",
      requestSchema: JobSeekerProfileUpdateSchema,
      responseSchema: JobSeekerProfileResponseSchema,
      body: data,
    });
  },

  async delete(profileId: string) {
    return apiRequest(`/api/job-seeker-profiles/${profileId}`, {
      method: "DELETE",
      responseSchema: z.null(),
    });
  },
};
