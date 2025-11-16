"use client";

import { useState, useEffect, type ReactElement } from "react";
import { usePathname } from "next/navigation";
import HarmonyChatbot from "./HarmonyChatbot";
import { getCurrentUserId } from "../lib/auth";

/**
 * Wrapper component that conditionally renders the Harmony chatbot
 * based on authentication status and current route.
 *
 * The chatbot will only display on authenticated pages (everything
 * except landing page, login, and signup pages).
 */
export default function ChatbotWrapper(): ReactElement | null {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const pathname = usePathname();

  // Check authentication status
  useEffect(() => {
    const checkAuth = (): void => {
      const userId = getCurrentUserId();
      setIsAuthenticated(!!userId);
    };

    // Check immediately and whenever pathname changes
    checkAuth();

    // Also check on storage events (in case auth changes in another tab)
    const handleStorageChange = (): void => {
      checkAuth();
    };

    window.addEventListener("storage", handleStorageChange);
    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };
  }, [pathname]);

  // Pages where chatbot should NOT be displayed
  const excludedPaths = ["/", "/login", "/signup"];

  // Don't render if on excluded paths or not authenticated
  if (excludedPaths.includes(pathname) || !isAuthenticated) {
    return null;
  }

  return (
    <HarmonyChatbot
      isOpen={isChatOpen}
      onClose={() => setIsChatOpen(false)}
      onOpen={() => setIsChatOpen(true)}
    />
  );
}
