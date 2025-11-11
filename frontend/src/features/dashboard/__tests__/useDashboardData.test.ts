/**
 * Tests for dashboard data hook
 */
import { renderHook, waitFor } from "@testing-library/react";
import { useDashboardData } from "../hooks/useDashboardData";

describe("useDashboardData", () => {
  it("should initialize with loading state", () => {
    const { result } = renderHook(() => useDashboardData());

    expect(result.current.loading).toBe(true);
    expect(result.current.stats).toBeNull();
  });

  it("should handle no user ID", async () => {
    const { result } = renderHook(() => useDashboardData());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
  });
});
