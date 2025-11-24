/**
 * User API functions
 */
import { z } from "zod";
import { apiRequest } from "../client";
import {
  UserCreateSchema,
  UserUpdateSchema,
  UserResponseSchema,
} from "./schemas";

export const userApi = {
  async create(data: z.infer<typeof UserCreateSchema>) {
    return apiRequest("/api/users", {
      method: "POST",
      requestSchema: UserCreateSchema,
      responseSchema: UserResponseSchema,
      body: data,
    });
  },

  async getAll(params?: { skip?: number; limit?: number }) {
    const query = new URLSearchParams();
    if (params?.skip) query.set("skip", params.skip.toString());
    if (params?.limit) query.set("limit", params.limit.toString());

    return apiRequest(`/api/users?${query}`, {
      method: "GET",
      responseSchema: z.array(UserResponseSchema),
    });
  },

  async getById(userId: string) {
    return apiRequest(`/api/users/${userId}`, {
      method: "GET",
      responseSchema: UserResponseSchema,
    });
  },

  async getByEmail(email: string) {
    return apiRequest(`/api/users/email/${email}`, {
      method: "GET",
      responseSchema: UserResponseSchema,
    });
  },

  async update(userId: string, data: z.infer<typeof UserUpdateSchema>) {
    return apiRequest(`/api/users/${userId}`, {
      method: "PUT",
      requestSchema: UserUpdateSchema,
      responseSchema: UserResponseSchema,
      body: data,
    });
  },

  async delete(userId: string) {
    return apiRequest(`/api/users/${userId}`, {
      method: "DELETE",
      responseSchema: z.null(),
    });
  },
};
