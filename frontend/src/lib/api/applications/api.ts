/**
 * Application API functions
 */
import { z } from "zod";
import { apiRequest } from "../client";
import {
  ApplicationCreateSchema,
  ApplicationUpdateSchema,
  ApplicationResponseSchema,
} from "./schemas";

export const applicationApi = {
  async create(data: z.infer<typeof ApplicationCreateSchema>) {
    return apiRequest("/api/applications", {
      method: "POST",
      requestSchema: ApplicationCreateSchema,
      responseSchema: ApplicationResponseSchema,
      body: data,
    });
  },

  async getAll(params?: {
    skip?: number;
    limit?: number;
    job_seeker_id?: string;
    job_id?: string;
    status?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.skip) query.set("skip", params.skip.toString());
    if (params?.limit) query.set("limit", params.limit.toString());
    if (params?.job_seeker_id) query.set("job_seeker_id", params.job_seeker_id);
    if (params?.job_id) query.set("job_id", params.job_id);
    if (params?.status) query.set("status", params.status);

    return apiRequest(`/api/applications?${query}`, {
      method: "GET",
      responseSchema: z.array(ApplicationResponseSchema),
    });
  },

  async getById(applicationId: string) {
    return apiRequest(`/api/applications/${applicationId}`, {
      method: "GET",
      responseSchema: ApplicationResponseSchema,
    });
  },

  async update(
    applicationId: string,
    data: z.infer<typeof ApplicationUpdateSchema>,
    changedBy?: string
  ) {
    const query = changedBy ? `?changed_by=${changedBy}` : "";
    return apiRequest(`/api/applications/${applicationId}${query}`, {
      method: "PUT",
      requestSchema: ApplicationUpdateSchema,
      responseSchema: ApplicationResponseSchema,
      body: data,
    });
  },

  async delete(applicationId: string) {
    return apiRequest(`/api/applications/${applicationId}`, {
      method: "DELETE",
      responseSchema: z.null(),
    });
  },

  async getCount(params?: {
    job_seeker_id?: string;
    job_id?: string;
    status?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.job_seeker_id) query.set("job_seeker_id", params.job_seeker_id);
    if (params?.job_id) query.set("job_id", params.job_id);
    if (params?.status) query.set("status", params.status);

    return apiRequest(`/api/applications/count?${query}`, {
      method: "GET",
      responseSchema: z.object({ count: z.number() }),
    });
  },

  /**
   * Helper: Reject an application with a reason
   */
  async reject(applicationId: string, rejectionReason: string) {
    return this.update(applicationId, {
      status: "Rejected",
      rejection_reason: rejectionReason,
    });
  },

  /**
   * Helper: Extend an offer to an applicant
   */
  async extendOffer(applicationId: string, nextStep?: string) {
    return this.update(applicationId, {
      status: "Offer Extended",
      next_step: nextStep || "Awaiting candidate response",
    });
  },

  /**
   * Helper: Accept an application (marks job as filled, rejects others)
   */
  async accept(applicationId: string) {
    return this.update(applicationId, {
      status: "Accepted",
      next_step: "Onboarding",
    });
  },
};
