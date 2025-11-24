/**
 * Tests for date helper functions
 */
import { calculateTimeAgo, formatDate, isRecent } from "../utils/dateHelpers";

describe("calculateTimeAgo", () => {
  it('should return "Today" for current date', () => {
    const now = new Date();
    expect(calculateTimeAgo(now)).toBe("Today");
  });

  it('should return "1 day ago" for yesterday', () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    expect(calculateTimeAgo(yesterday)).toBe("1 day ago");
  });

  it("should return days for dates within a week", () => {
    const threeDaysAgo = new Date();
    threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);
    expect(calculateTimeAgo(threeDaysAgo)).toBe("3 days ago");
  });

  it('should return "1 week ago" for 7-13 days', () => {
    const tenDaysAgo = new Date();
    tenDaysAgo.setDate(tenDaysAgo.getDate() - 10);
    expect(calculateTimeAgo(tenDaysAgo)).toBe("1 week ago");
  });
});

describe("formatDate", () => {
  it("should format date correctly", () => {
    const date = new Date("2024-01-15");
    const formatted = formatDate(date);
    expect(formatted).toMatch(/Jan 15, 2024/);
  });
});

describe("isRecent", () => {
  it("should return true for dates within threshold", () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    expect(isRecent(yesterday, 7)).toBe(true);
  });

  it("should return false for dates outside threshold", () => {
    const tenDaysAgo = new Date();
    tenDaysAgo.setDate(tenDaysAgo.getDate() - 10);
    expect(isRecent(tenDaysAgo, 7)).toBe(false);
  });
});
