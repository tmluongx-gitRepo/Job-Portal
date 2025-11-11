/**
 * Base API client utilities
 * Shared across all API modules
 */
import { z } from "zod";

// Get API URL from environment variable
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Custom error class for validation errors
 */
export class ValidationError extends Error {
  constructor(
    message: string,
    public issues: z.ZodIssue[]
  ) {
    super(message);
    this.name = "ValidationError";
  }
}

/**
 * Generic API request function with validation
 * Used by all feature modules
 */
export async function apiRequest<TResponse>(
  endpoint: string,
  options: Omit<RequestInit, "body"> & {
    responseSchema: z.ZodSchema<TResponse>;
    requestSchema?: z.ZodSchema;
    body?: unknown;
  }
): Promise<TResponse> {
  const { responseSchema, requestSchema, body, ...fetchOptions } = options;

  // Validate request body if schema provided
  if (requestSchema && body) {
    const validation = requestSchema.safeParse(body);
    if (!validation.success) {
      throw new ValidationError(
        "Request validation failed",
        validation.error.issues
      );
    }
  }

  // Make the request
  // Ensure endpoint starts with /api prefix
  const apiEndpoint = endpoint.startsWith("/api")
    ? endpoint
    : `/api${endpoint}`;
  const fullUrl = `${API_URL}${apiEndpoint}`;

  // Log the request for debugging (only in browser)
  if (typeof window !== "undefined") {
    console.log(`[API Client] Original endpoint: ${endpoint}`);
    console.log(`[API Client] API endpoint: ${apiEndpoint}`);
    console.log(`[API Client] Full URL: ${fullUrl}`);
  }

  const response = await fetch(fullUrl, {
    ...fetchOptions,
    headers: {
      "Content-Type": "application/json",
      ...fetchOptions.headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  // Handle HTTP errors
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = await response.text();
    }

    // Log error details in development (only in browser)
    if (
      typeof window !== "undefined" &&
      process.env.NODE_ENV === "development"
    ) {
      console.error(`[API Error] ${response.status} ${response.statusText}`, {
        url: fullUrl,
        errorData,
      });
    }

    throw new ApiError(
      `API request failed: ${response.statusText}`,
      response.status,
      errorData
    );
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null as TResponse;
  }

  // Parse response
  let data;
  try {
    data = await response.json();
  } catch (_error) {
    throw new ApiError("Failed to parse response JSON", response.status);
  }

  // Validate response
  const validation = responseSchema.safeParse(data);
  if (!validation.success) {
    throw new ValidationError(
      "Response validation failed",
      validation.error.issues
    );
  }

  return validation.data;
}
