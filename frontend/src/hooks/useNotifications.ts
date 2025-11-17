"use client";

import { useState, useEffect } from "react";

export interface Notification {
  id: string;
  read: boolean;
  timestamp?: Date | string;
  type?: string;
}

/**
 * Custom hook to manage notification count
 * Currently uses mock data, but can be easily updated to use API
 */
export function useNotifications(
  userType: "job_seeker" | "employer" = "job_seeker"
): {
  unreadCount: number;
  loading: boolean;
} {
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // TODO: Replace with actual API call when backend is ready
    // For now, simulate fetching from localStorage or mock data
    const fetchUnreadCount = async (): Promise<void> => {
      setLoading(true);

      try {
        // Try to get from localStorage first (if notifications page has saved state)
        const storageKey =
          userType === "employer"
            ? "employer_notifications"
            : "job_seeker_notifications";

        const stored = localStorage.getItem(storageKey);
        if (stored) {
          const notifications = JSON.parse(stored) as Notification[];
          const count = notifications.filter((n) => !n.read).length;
          setUnreadCount(count);
        } else {
          // Default mock counts if no stored data
          const defaultCount = userType === "employer" ? 5 : 3;
          setUnreadCount(defaultCount);
        }
      } catch (error) {
        console.error("Error fetching notification count:", error);
        // Fallback to default
        setUnreadCount(0);
      } finally {
        setLoading(false);
      }
    };

    void fetchUnreadCount();

    // Listen for changes from the notifications page
    const handleStorageChange = (e: StorageEvent): void => {
      const storageKey =
        userType === "employer"
          ? "employer_notifications"
          : "job_seeker_notifications";

      if (e.key === storageKey && e.newValue) {
        try {
          const notifications = JSON.parse(e.newValue) as Notification[];
          const count = notifications.filter((n) => !n.read).length;
          setUnreadCount(count);
        } catch (error) {
          console.error("Error parsing notification storage change:", error);
        }
      }
    };

    // Listen for custom event from notifications page
    const handleNotificationUpdate = ((e: CustomEvent) => {
      if (e.detail?.userType === userType) {
        setUnreadCount(e.detail.unreadCount || 0);
      }
    }) as EventListener;

    window.addEventListener("storage", handleStorageChange);
    window.addEventListener("notificationsUpdated", handleNotificationUpdate);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener(
        "notificationsUpdated",
        handleNotificationUpdate
      );
    };
  }, [userType]);

  return { unreadCount, loading };
}
