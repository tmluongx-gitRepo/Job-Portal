"use client";

import { useState, useEffect, type ReactElement } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Leaf, Bell, Settings, User } from "lucide-react";
import { getCurrentUser, isAuthenticated } from "../lib/auth";

export default function Header(): ReactElement {
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState<{ id: string; email: string; account_type?: string } | null>(null);
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
  const isDashboardActive = pathname === "/dashboard" || pathname === "/employer-dashboard";

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
                const isActive = pathname === item.href || (item.href.includes("dashboard") && isDashboardActive);
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

          {/* Right side - Different content for authenticated vs unauthenticated */}
          {authenticated ? (
            <div className="flex items-center space-x-4">
              <button
                className="text-green-700 hover:text-green-800 transition-colors"
                aria-label="Notifications"
              >
                <Bell className="w-5 h-5" />
              </button>
              <Link
                href="/profile"
                className="text-green-700 hover:text-green-800 transition-colors"
                aria-label="Settings"
              >
                <Settings className="w-5 h-5" />
              </Link>
              <Link
                href="/profile"
                className="w-8 h-8 bg-gradient-to-r from-green-100 to-amber-100 rounded-full flex items-center justify-center hover:shadow-md transition-shadow"
                aria-label="User profile"
              >
                <User className="w-5 h-5 text-green-700" />
              </Link>
              <div className="bg-gradient-to-r from-amber-100 to-green-100 text-green-800 px-4 py-2 rounded-full font-medium border border-green-200 shadow-sm">
                {user?.account_type === "employer"
                  ? "✨ Build great teams!"
                  : "✨ Find your path!"}
              </div>
            </div>
          ) : (
            <div className="flex items-center space-x-4">
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
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
