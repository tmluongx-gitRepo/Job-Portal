/**
 * Interview API functions
 */
import { z } from "zod";
import { apiRequest } from "../client";
import {
  InterviewCreateSchema,
  InterviewUpdateSchema,
  InterviewCancelSchema,
  InterviewCompleteSchema,
  InterviewResponseSchema,
  InterviewListResponseSchema,
} from "./schemas";

export const interviewApi = {
  async create(data: z.infer<typeof InterviewCreateSchema>) {
    return apiRequest("/interviews", {
      method: "POST",
      requestSchema: InterviewCreateSchema,
      responseSchema: InterviewResponseSchema,
      body: data,
    });
  },

  async getAll(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    upcoming_only?: boolean;
  }) {
    const query = new URLSearchParams();
    // Use explicit undefined checks to allow 0 as valid values
    if (params?.skip !== undefined) query.set("skip", params.skip.toString());
    if (params?.limit !== undefined)
      query.set("limit", params.limit.toString());
    if (params?.status) query.set("status", params.status);
    if (params?.upcoming_only) query.set("upcoming_only", "true");

    return apiRequest(`/interviews?${query}`, {
      method: "GET",
      responseSchema: InterviewListResponseSchema,
    });
  },

  async getUpcoming(params?: { skip?: number; limit?: number }) {
    const query = new URLSearchParams();
    // Use explicit undefined checks to allow 0 as valid values
    if (params?.skip !== undefined) query.set("skip", params.skip.toString());
    if (params?.limit !== undefined)
      query.set("limit", params.limit.toString());

    return apiRequest(`/interviews/upcoming?${query}`, {
      method: "GET",
      responseSchema: InterviewListResponseSchema,
    });
  },

  async getById(interviewId: string) {
    return apiRequest(`/interviews/${interviewId}`, {
      method: "GET",
      responseSchema: InterviewResponseSchema,
    });
  },

  async update(
    interviewId: string,
    data: z.infer<typeof InterviewUpdateSchema>
  ) {
    return apiRequest(`/interviews/${interviewId}`, {
      method: "PUT",
      requestSchema: InterviewUpdateSchema,
      responseSchema: InterviewResponseSchema,
      body: data,
    });
  },

  async cancel(
    interviewId: string,
    data: z.infer<typeof InterviewCancelSchema>
  ) {
    return apiRequest(`/interviews/${interviewId}`, {
      method: "DELETE",
      requestSchema: InterviewCancelSchema,
      responseSchema: z.void(),
      body: data,
    });
  },

  async complete(
    interviewId: string,
    data: z.infer<typeof InterviewCompleteSchema>
  ) {
    return apiRequest(`/interviews/${interviewId}/complete`, {
      method: "POST",
      requestSchema: InterviewCompleteSchema,
      responseSchema: InterviewResponseSchema,
      body: data,
    });
  },
};
