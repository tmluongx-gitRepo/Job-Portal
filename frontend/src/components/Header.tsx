"use client";

import { useState, useEffect, type ReactElement } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Leaf, Bell, Settings, User as UserIcon } from "lucide-react";
import {
  isAuthenticated,
  getCurrentUser,
  clearAuth,
} from "@/lib/auth";

export default function Header(): ReactElement {
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState<{
    id: string;
    email: string;
    account_type?: string;
  } | null>(null);
  const pathname = usePathname();

  // Check authentication status
  useEffect(() => {
    const checkAuth = (): void => {
      const authStatus = isAuthenticated();
      const currentUser = getCurrentUser();
      setAuthenticated(authStatus);
      setUser(currentUser);
    };

    // Check immediately and on pathname changes
    checkAuth();

    // Listen for storage changes (auth changes in other tabs)
    const handleStorageChange = (): void => {
      checkAuth();
    };

    window.addEventListener("storage", handleStorageChange);
    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };
  }, [pathname]);

  // Determine navigation items based on account type
  const getNavigationItems = () => {
    if (!authenticated || !user) return [];

    const accountType = user.account_type;

    if (accountType === "employer") {
      return [
        { label: "Dashboard", href: "/employer-dashboard" },
        { label: "Job Listings", href: "/jobs" },
        { label: "Applications", href: "/employer-dashboard#applications" },
        { label: "Companies", href: "/employer-dashboard#companies" },
      ];
    } else {
      // Default to job seeker navigation
      return [
        { label: "Dashboard", href: "/dashboard" },
        { label: "Job Search", href: "/jobs" },
        { label: "Profile", href: "/profile" },
      ];
    }
  };

  const navigationItems = getNavigationItems();
  const isDashboardActive =
    pathname === "/dashboard" || pathname === "/employer-dashboard";

  const handleLogout = async (): Promise<void> => {
    try {
      // TODO: Call logout API when ready
      clearAuth();
      window.location.href = "/";
    } catch (error) {
      console.error("Logout error:", error);
      clearAuth();
      window.location.href = "/";
    }
  };

  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-green-200 shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-3">
          <Link href="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-amber-500 rounded-lg flex items-center justify-center">
              <Leaf className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="text-2xl font-bold bg-gradient-to-r from-green-700 to-green-800 bg-clip-text text-transparent">
                Career Harmony
              </span>
              <div className="text-xs text-green-600">
                Work-Life Balance • Professional Growth
              </div>
            </div>
          </Link>

          {/* Navigation - Show different items based on authentication */}
          {authenticated && navigationItems.length > 0 ? (
            <nav className="hidden md:flex items-center space-x-8">
              {navigationItems.map((item) => {
                const isActive =
                  pathname === item.href ||
                  (item.href.includes("dashboard") && isDashboardActive);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`${
                      isActive
                        ? "text-green-800 font-semibold"
                        : "text-green-700 hover:text-green-800 font-medium"
                    } transition-colors`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          ) : (
            <nav className="hidden md:flex items-center space-x-8">
              <Link
                href="/#solutions"
                className="text-green-700 hover:text-green-800 font-medium transition-colors"
              >
                Solutions
              </Link>
              <Link
                href="/jobs"
                className="text-green-700 hover:text-green-800 font-medium transition-colors"
              >
                Career Search
              </Link>
              <Link
                href="/about"
                className="text-green-700 hover:text-green-800 font-medium transition-colors"
              >
                About Us
              </Link>
            </nav>
          )}

          <div className="flex items-center space-x-4">
            {authenticated && user ? (
              <>
                {/* Authenticated user actions */}
                <button
                  className="text-green-700 hover:text-green-800 transition-colors p-2"
                  aria-label="Notifications"
                >
                  <Bell className="w-5 h-5" />
                </button>
                <Link
                  href="/profile"
                  className="text-green-700 hover:text-green-800 transition-colors p-2"
                  aria-label="Settings"
                >
                  <Settings className="w-5 h-5" />
                </Link>
                <Link
                  href="/profile"
                  className="flex items-center space-x-2 text-green-700 hover:text-green-800 transition-colors"
                >
                  <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-amber-500 rounded-full flex items-center justify-center">
                    <UserIcon className="w-4 h-4 text-white" />
                  </div>
                  <span className="hidden md:block font-medium">
                    {user.email.split("@")[0]}
                  </span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="text-green-700 hover:text-green-800 font-medium transition-colors"
                >
                  Logout
                </button>
                {/* Motivational message */}
                <div className="hidden lg:block bg-gradient-to-r from-amber-100 to-green-100 border border-amber-200 rounded-full px-4 py-1 ml-4">
                  <span className="text-green-800 font-medium text-sm">
                    {user.account_type === "employer"
                      ? "✨ Build great teams!"
                      : "✨ Find your path!"}
                  </span>
                </div>
              </>
            ) : (
              <>
                {/* Unauthenticated user actions */}
                <Link
                  href="/login"
                  className="text-green-700 hover:text-green-800 font-medium transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href="/signup"
                  className="bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-2 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all shadow-sm"
                >
                  Join Our Community
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
