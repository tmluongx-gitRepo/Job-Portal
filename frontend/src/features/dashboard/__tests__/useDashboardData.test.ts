/**
 * Tests for dashboard data hook
 */
import { renderHook, waitFor } from "@testing-library/react";
import { useDashboardData } from "../hooks/useDashboardData";

describe("useDashboardData", () => {
  it("should load dashboard data when userId is provided", async () => {
    const { result } = renderHook(() => useDashboardData("user123"));

    // Wait for loading to complete
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Should have mock stats data
    expect(result.current.stats).toEqual({
      applicationsThisWeek: 3,
      interviewsScheduled: 1,
      profileViews: 12,
      newMatches: 5,
    });
    expect(result.current.error).toBeNull();
  });

  it("should not load data when no user ID is provided", async () => {
    const { result } = renderHook(() => useDashboardData());

    // Without userId, loading should be false
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.stats).toBeNull();
    expect(result.current.error).toBeNull();
  });
});
