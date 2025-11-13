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

  let response: Response;
  try {
    response = await fetch(fullUrl, {
      ...fetchOptions,
      headers: {
        "Content-Type": "application/json",
        ...fetchOptions.headers,
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (fetchError) {
    // Handle network errors (CORS, connection refused, etc.)
    const errorMessage =
      fetchError instanceof Error
        ? fetchError.message
        : "Network error occurred";

    // Log detailed error in development
    if (typeof window !== "undefined" && process.env.NODE_ENV === "development") {
      console.error(`[API Network Error] ${errorMessage}`, {
        url: fullUrl,
        error: fetchError,
        apiUrl: API_URL,
        endpoint: apiEndpoint,
      });
    }

    // Provide helpful error message
    if (errorMessage.includes("Failed to fetch") || errorMessage.includes("NetworkError")) {
      throw new ApiError(
        `Unable to connect to API server at ${API_URL}. Please ensure the backend is running.`,
        0,
        {
          originalError: errorMessage,
          url: fullUrl,
          suggestion: "Check that the backend server is running and accessible.",
        }
      );
    }

    throw new ApiError(
      `Network error: ${errorMessage}`,
      0,
      {
        originalError: fetchError,
        url: fullUrl,
      }
    );
  }

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

/**
 * Upload a file to the API
 * Used for resume uploads and other file uploads
 */
export async function uploadFile<TResponse>(
  endpoint: string,
  file: File,
  additionalData?: Record<string, string>,
  options?: {
    responseSchema?: z.ZodSchema<TResponse>;
  }
): Promise<TResponse | null> {
  const apiEndpoint = endpoint.startsWith("/api")
    ? endpoint
    : `/api${endpoint}`;
  const fullUrl = `${API_URL}${apiEndpoint}`;

  // Create FormData
  const formData = new FormData();
  formData.append("file", file);
  
  // Add any additional form fields
  if (additionalData) {
    Object.entries(additionalData).forEach(([key, value]) => {
      formData.append(key, value);
    });
  }

  let response: Response;
  try {
    response = await fetch(fullUrl, {
      method: "POST",
      body: formData,
      // Don't set Content-Type header - browser will set it with boundary
    });
  } catch (fetchError) {
    const errorMessage =
      fetchError instanceof Error
        ? fetchError.message
        : "Network error occurred";

    if (typeof window !== "undefined" && process.env.NODE_ENV === "development") {
      console.error(`[API Upload Error] ${errorMessage}`, {
        url: fullUrl,
        error: fetchError,
      });
    }

    throw new ApiError(
      `Failed to upload file: ${errorMessage}`,
      0,
      { originalError: fetchError, url: fullUrl }
    );
  }

  // Handle HTTP errors
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = await response.text();
    }

    throw new ApiError(
      `File upload failed: ${response.statusText}`,
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

  // Validate response if schema provided
  if (options?.responseSchema) {
    const validation = options.responseSchema.safeParse(data);
    if (!validation.success) {
      throw new ValidationError(
        "Response validation failed",
        validation.error.issues
      );
    }
    return validation.data;
  }

  return data as TResponse;
}
