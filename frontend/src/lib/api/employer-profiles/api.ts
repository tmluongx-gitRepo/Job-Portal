/**
 * Employer Profile API functions
 */
import { z } from "zod";
import { ApiError, apiRequest } from "../client";
import type { EmployerProfile } from "./types";
import {
  EmployerProfileCreateSchema,
  EmployerProfileUpdateSchema,
  EmployerProfileResponseSchema,
} from "./schemas";

export const employerProfileApi = {
  async create(data: z.infer<typeof EmployerProfileCreateSchema>) {
    return apiRequest("/api/employer-profiles", {
      method: "POST",
      requestSchema: EmployerProfileCreateSchema,
      responseSchema: EmployerProfileResponseSchema,
      body: data,
    });
  },

  async getAll(params?: { skip?: number; limit?: number }) {
    const query = new URLSearchParams();
    if (params?.skip) query.set("skip", params.skip.toString());
    if (params?.limit) query.set("limit", params.limit.toString());

    return apiRequest(`/api/employer-profiles?${query}`, {
      method: "GET",
      responseSchema: z.array(EmployerProfileResponseSchema),
    });
  },

  async getById(profileId: string) {
    return apiRequest(`/api/employer-profiles/${profileId}`, {
      method: "GET",
      responseSchema: EmployerProfileResponseSchema,
    });
  },

  async getByUserId(userId: string): Promise<EmployerProfile | null> {
    try {
      return await apiRequest(`/api/employer-profiles/user/${userId}`, {
        method: "GET",
        responseSchema: EmployerProfileResponseSchema,
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
    data: z.infer<typeof EmployerProfileUpdateSchema>
  ) {
    return apiRequest(`/api/employer-profiles/${profileId}`, {
      method: "PUT",
      requestSchema: EmployerProfileUpdateSchema,
      responseSchema: EmployerProfileResponseSchema,
      body: data,
    });
  },

  async delete(profileId: string) {
    return apiRequest(`/api/employer-profiles/${profileId}`, {
      method: "DELETE",
      responseSchema: z.null(),
    });
  },
};
