/**
 * Employer Profile API functions
 */
import { z } from "zod";
import { apiRequest } from "../client";
import {
  EmployerProfileCreateSchema,
  EmployerProfileUpdateSchema,
  EmployerProfileResponseSchema,
} from "./schemas";

export const employerProfileApi = {
  async create(data: z.infer<typeof EmployerProfileCreateSchema>) {
    return apiRequest("/employer-profiles", {
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

    return apiRequest(`/employer-profiles?${query}`, {
      method: "GET",
      responseSchema: z.array(EmployerProfileResponseSchema),
    });
  },

  async getById(profileId: string) {
    return apiRequest(`/employer-profiles/${profileId}`, {
      method: "GET",
      responseSchema: EmployerProfileResponseSchema,
    });
  },

  async getByUserId(userId: string) {
    return apiRequest(`/employer-profiles/user/${userId}`, {
      method: "GET",
      responseSchema: EmployerProfileResponseSchema,
    });
  },

  async update(
    profileId: string,
    data: z.infer<typeof EmployerProfileUpdateSchema>
  ) {
    return apiRequest(`/employer-profiles/${profileId}`, {
      method: "PUT",
      requestSchema: EmployerProfileUpdateSchema,
      responseSchema: EmployerProfileResponseSchema,
      body: data,
    });
  },

  async delete(profileId: string) {
    return apiRequest(`/employer-profiles/${profileId}`, {
      method: "DELETE",
      responseSchema: z.null(),
    });
  },
};
