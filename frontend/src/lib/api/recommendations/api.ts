/**
 * Recommendation API functions
 */
import { z } from 'zod';
import { apiRequest } from '../client';
import { RecommendationCreateSchema, RecommendationUpdateSchema, RecommendationResponseSchema } from './schemas';

export const recommendationApi = {
  async create(data: z.infer<typeof RecommendationCreateSchema>) {
    return apiRequest('/recommendations', {
      method: 'POST',
      requestSchema: RecommendationCreateSchema,
      responseSchema: RecommendationResponseSchema,
      body: data,
    });
  },

  async getForJobSeeker(
    jobSeekerId: string,
    params?: {
      skip?: number;
      limit?: number;
      min_match?: number;
      include_viewed?: boolean;
      include_dismissed?: boolean;
      include_applied?: boolean;
    }
  ) {
    const query = new URLSearchParams();
    if (params?.skip) query.set('skip', params.skip.toString());
    if (params?.limit) query.set('limit', params.limit.toString());
    if (params?.min_match) query.set('min_match', params.min_match.toString());
    if (params?.include_viewed !== undefined)
      query.set('include_viewed', params.include_viewed.toString());
    if (params?.include_dismissed !== undefined)
      query.set('include_dismissed', params.include_dismissed.toString());
    if (params?.include_applied !== undefined)
      query.set('include_applied', params.include_applied.toString());

    return apiRequest(`/recommendations/job-seeker/${jobSeekerId}?${query}`, {
      method: 'GET',
      responseSchema: z.array(z.any()), // Complex enriched response
    });
  },

  async getCandidatesForJob(
    jobId: string,
    params?: {
      skip?: number;
      limit?: number;
      min_match?: number;
    }
  ) {
    const query = new URLSearchParams();
    if (params?.skip) query.set('skip', params.skip.toString());
    if (params?.limit) query.set('limit', params.limit.toString());
    if (params?.min_match) query.set('min_match', params.min_match.toString());

    return apiRequest(`/recommendations/job/${jobId}/candidates?${query}`, {
      method: 'GET',
      responseSchema: z.array(z.any()), // Complex enriched response
    });
  },

  async getById(recommendationId: string) {
    return apiRequest(`/recommendations/${recommendationId}`, {
      method: 'GET',
      responseSchema: RecommendationResponseSchema,
    });
  },

  async update(
    recommendationId: string,
    data: z.infer<typeof RecommendationUpdateSchema>
  ) {
    return apiRequest(`/recommendations/${recommendationId}`, {
      method: 'PUT',
      requestSchema: RecommendationUpdateSchema,
      responseSchema: RecommendationResponseSchema,
      body: data,
    });
  },

  async markViewed(recommendationId: string) {
    return apiRequest(`/recommendations/${recommendationId}/view`, {
      method: 'POST',
      responseSchema: z.object({ message: z.string() }),
    });
  },

  async dismiss(recommendationId: string) {
    return apiRequest(`/recommendations/${recommendationId}/dismiss`, {
      method: 'POST',
      responseSchema: z.object({ message: z.string() }),
    });
  },

  async delete(recommendationId: string) {
    return apiRequest(`/recommendations/${recommendationId}`, {
      method: 'DELETE',
      responseSchema: z.null(),
    });
  },

  async getCount(
    jobSeekerId: string,
    params?: {
      viewed?: boolean;
      dismissed?: boolean;
    }
  ) {
    const query = new URLSearchParams();
    if (params?.viewed !== undefined)
      query.set('viewed', params.viewed.toString());
    if (params?.dismissed !== undefined)
      query.set('dismissed', params.dismissed.toString());

    return apiRequest(`/recommendations/count/${jobSeekerId}?${query}`, {
      method: 'GET',
      responseSchema: z.object({ count: z.number() }),
    });
  },
};
