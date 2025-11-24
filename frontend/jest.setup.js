/**
 * Jest setup file
 * Runs before each test
 */

// Add custom matchers from jest-dom (CommonJS require for Jest)
require("@testing-library/jest-dom");

// Mock Next.js router
jest.mock("next/navigation", () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      pathname: "/",
      query: {},
      asPath: "/",
    };
  },
  usePathname() {
    return "/";
  },
  useSearchParams() {
    return new URLSearchParams();
  },
}));

// Mock environment variables
process.env.NEXT_PUBLIC_API_URL = "http://localhost:8000";

// Suppress console errors during tests (optional)
// global.console.error = jest.fn()
