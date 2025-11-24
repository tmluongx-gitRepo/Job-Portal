/**
 * Job API functions
 */
import { z } from "zod";
import { apiRequest } from "../client";
import { JobCreateSchema, JobUpdateSchema, JobResponseSchema } from "./schemas";

export const jobApi = {
  async create(data: z.infer<typeof JobCreateSchema>, postedBy?: string) {
    const query = postedBy ? `?posted_by=${postedBy}` : "";
    return apiRequest(`/api/jobs${query}`, {
      method: "POST",
      requestSchema: JobCreateSchema,
      responseSchema: JobResponseSchema,
      body: data,
    });
  },

  async getAll(params?: {
    skip?: number;
    limit?: number;
    is_active?: boolean;
    posted_by?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.set("skip", params.skip.toString());
    if (params?.limit) query.set("limit", params.limit.toString());
    if (params?.is_active !== undefined)
      query.set("is_active", params.is_active.toString());
    if (params?.posted_by) query.set("posted_by", params.posted_by);

    return apiRequest(`/api/jobs?${query}`, {
      method: "GET",
      responseSchema: z.array(JobResponseSchema),
    });
  },

  async search(params: {
    query?: string;
    location?: string;
    job_type?: string;
    remote_ok?: boolean;
    skills?: string[];
    min_salary?: number;
    max_salary?: number;
    experience_required?: string;
    industry?: string;
    company_size?: string;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach((v) => query.append(key, v));
        } else {
          query.set(key, value.toString());
        }
      }
    });

    return apiRequest(`/api/jobs/search?${query}`, {
      method: "GET",
      responseSchema: z.array(JobResponseSchema),
    });
  },

  async getById(jobId: string, incrementViews = false) {
    const query = incrementViews ? "?increment_views=true" : "";
    return apiRequest(`/api/jobs/${jobId}${query}`, {
      method: "GET",
      responseSchema: JobResponseSchema,
    });
  },

  async update(jobId: string, data: z.infer<typeof JobUpdateSchema>) {
    return apiRequest(`/api/jobs/${jobId}`, {
      method: "PUT",
      requestSchema: JobUpdateSchema,
      responseSchema: JobResponseSchema,
      body: data,
    });
  },

  async delete(jobId: string) {
    return apiRequest(`/api/jobs/${jobId}`, {
      method: "DELETE",
      responseSchema: z.null(),
    });
  },

  async getCount(params?: { is_active?: boolean; posted_by?: string }) {
    const query = new URLSearchParams();
    if (params?.is_active !== undefined)
      query.set("is_active", params.is_active.toString());
    if (params?.posted_by) query.set("posted_by", params.posted_by);

    return apiRequest(`/api/jobs/count?${query}`, {
      method: "GET",
      responseSchema: z.object({ count: z.number() }),
    });
  },
};
