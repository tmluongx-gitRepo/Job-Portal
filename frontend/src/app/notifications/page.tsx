"use client";

import { useState, useEffect, type ReactElement } from "react";
import Link from "next/link";
import {
  Bell,
  Briefcase,
  Calendar,
  CheckCircle,
  Clock,
  Settings,
  Star,
  TrendingUp,
  Users,
  X,
  Filter,
  MoreHorizontal,
  MessageSquare,
  Heart,
  Mail,
  Smartphone,
} from "lucide-react";

// Notification types matching LinkedIn patterns
type NotificationType =
  | "application_status_update"
  | "interview_scheduled"
  | "interview_rescheduled"
  | "job_match"
  | "profile_view"
  | "message"
  | "recommendation"
  | "system";

type NotificationChannel = "in_app" | "email" | "push";

interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  description: string;
  timestamp: Date;
  read: boolean;
  actionUrl?: string;
  actionText?: string;
  icon: typeof Briefcase;
  iconColor: string;
  iconBg: string;
  channels: NotificationChannel[];
}

// Mock notification data
const mockNotifications: Notification[] = [
  {
    id: "1",
    type: "application_status_update",
    title: "Application Status Update",
    description:
      "Your application for Senior Software Engineer at TechCorp has been reviewed",
    timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
    read: false,
    actionUrl: "/applications",
    actionText: "View Application",
    icon: Briefcase,
    iconColor: "text-green-600",
    iconBg: "bg-green-100",
    channels: ["in_app", "email", "push"],
  },
  {
    id: "2",
    type: "interview_scheduled",
    title: "Interview Scheduled",
    description:
      "You have an interview scheduled for tomorrow at 2:00 PM with InnovateLabs",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
    read: false,
    actionUrl: "/applications",
    actionText: "View Details",
    icon: Calendar,
    iconColor: "text-purple-600",
    iconBg: "bg-purple-100",
    channels: ["in_app", "email", "push"],
  },
  {
    id: "8",
    type: "interview_rescheduled",
    title: "Interview Rescheduled",
    description:
      "Your interview with GreenTech Solutions has been rescheduled to Friday at 10:00 AM",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4), // 4 hours ago
    read: false,
    actionUrl: "/applications",
    actionText: "View Details",
    icon: Calendar,
    iconColor: "text-orange-600",
    iconBg: "bg-orange-100",
    channels: ["in_app", "email", "push"],
  },
  {
    id: "3",
    type: "job_match",
    title: "New Job Match",
    description:
      "3 new jobs match your profile: Product Manager positions at top companies",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5), // 5 hours ago
    read: false,
    actionUrl: "/jobs",
    actionText: "View Jobs",
    icon: Star,
    iconColor: "text-amber-600",
    iconBg: "bg-amber-100",
    channels: ["in_app", "email"],
  },
  {
    id: "4",
    type: "profile_view",
    title: "Profile Viewed",
    description: "5 employers viewed your profile this week",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
    read: true,
    actionUrl: "/profile",
    actionText: "Update Profile",
    icon: Users,
    iconColor: "text-blue-600",
    iconBg: "bg-blue-100",
    channels: ["in_app"],
  },
  {
    id: "5",
    type: "recommendation",
    title: "Career Tip",
    description:
      "Remember to keep your skills section up to date - it increases your visibility by 40%",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2), // 2 days ago
    read: true,
    actionUrl: "/profile",
    actionText: "Update Skills",
    icon: Heart,
    iconColor: "text-pink-600",
    iconBg: "bg-pink-100",
    channels: ["in_app"],
  },
  {
    id: "6",
    type: "message",
    title: "New Message",
    description: "You have a new message from TechCorp recruiter",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3), // 3 days ago
    read: true,
    actionUrl: "#",
    actionText: "Read Message",
    icon: MessageSquare,
    iconColor: "text-indigo-600",
    iconBg: "bg-indigo-100",
    channels: ["in_app", "email", "push"],
  },
  {
    id: "7",
    type: "system",
    title: "Profile Strength Improved",
    description:
      "Your profile is now 85% complete. Add work experience to reach 100%",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5), // 5 days ago
    read: true,
    actionUrl: "/profile",
    actionText: "Complete Profile",
    icon: TrendingUp,
    iconColor: "text-green-600",
    iconBg: "bg-green-100",
    channels: ["in_app"],
  },
];

// Helper to render channel badge
const ChannelBadge = ({ channel }: { channel: NotificationChannel }): JSX.Element => {
  const channelConfig = {
    in_app: { icon: Bell, label: "App", color: "bg-green-100 text-green-700" },
    email: { icon: Mail, label: "Email", color: "bg-blue-100 text-blue-700" },
    push: {
      icon: Smartphone,
      label: "Push",
      color: "bg-purple-100 text-purple-700",
    },
  };
  const config = channelConfig[channel];
  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-xs font-medium ${config.color}`}
    >
      <Icon className="w-3 h-3" />
      <span>{config.label}</span>
    </span>
  );
};

// Format timestamp like LinkedIn
function formatTimestamp(date: Date | string): string {
  // Convert to Date object if it's a string
  let dateObj: Date;
  
  if (typeof date === 'string') {
    dateObj = new Date(date);
  } else if (date instanceof Date) {
    dateObj = date;
  } else {
    console.warn("Invalid date passed to formatTimestamp:", date);
    return "Invalid date";
  }
  
  // Check if the resulting date is valid
  if (isNaN(dateObj.getTime())) {
    console.warn("Invalid date passed to formatTimestamp:", date);
    return "Invalid date";
  }

  const now = new Date();
  const diffMs = now.getTime() - dateObj.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const diffWeeks = Math.floor(diffDays / 7);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffWeeks < 4) return `${diffWeeks}w ago`;
  return dateObj.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export default function NotificationsPage(): ReactElement {
  const [notifications, setNotifications] =
    useState<Notification[]>(mockNotifications);
  const [filter, setFilter] = useState<"all" | "unread">("all");

  // Helper to get icon by type
  const getIconByType = (type: NotificationType): typeof Briefcase => {
    const iconMap: Record<NotificationType, typeof Briefcase> = {
      application_status_update: Briefcase,
      interview_scheduled: Calendar,
      interview_rescheduled: Calendar,
      job_match: Star,
      profile_view: Users,
      message: MessageSquare,
      recommendation: Heart,
      system: Settings,
    };
    return iconMap[type] || Bell;
  };

  // Load from localStorage on mount and save on changes
  useEffect(() => {
    const stored = localStorage.getItem("job_seeker_notifications");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        // Convert timestamp strings back to Date objects and restore icons
        const withDates = parsed.map((n: Notification) => ({
          ...n,
          timestamp: new Date(n.timestamp),
          icon: getIconByType(n.type),
        }));
        setNotifications(withDates);
      } catch (error) {
        console.error("Error loading notifications from storage:", error);
      }
    }
  }, []);

  // Save to localStorage and dispatch event when notifications change
  useEffect(() => {
    localStorage.setItem("job_seeker_notifications", JSON.stringify(notifications));
    
    // Dispatch custom event for dashboard to listen
    const unreadCount = notifications.filter((n) => !n.read).length;
    window.dispatchEvent(
      new CustomEvent("notificationsUpdated", {
        detail: { userType: "job_seeker", unreadCount },
      })
    );
  }, [notifications]);

  const filteredNotifications =
    filter === "unread"
      ? notifications.filter((n) => !n.read)
      : notifications;

  const unreadCount = notifications.filter((n) => !n.read).length;

  const markAsRead = (id: string): void => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const markAllAsRead = (): void => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const deleteNotification = (id: string): void => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-gradient-to-r from-green-600 to-green-700 rounded-xl">
                <Bell className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-green-900">
                  Notifications
                </h1>
                <p className="text-sm text-green-700">
                  Stay updated with your job search
                </p>
              </div>
            </div>
            <Link
              href="/dashboard"
              className="text-green-700 hover:text-green-800 font-medium transition-colors"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>

        {/* Filters and Actions */}
        <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-4 mb-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setFilter("all")}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${
                  filter === "all"
                    ? "bg-green-600 text-white"
                    : "bg-green-50 text-green-700 hover:bg-green-100"
                }`}
              >
                <Filter className="w-4 h-4" />
                <span>All ({notifications.length})</span>
              </button>
              <button
                onClick={() => setFilter("unread")}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${
                  filter === "unread"
                    ? "bg-green-600 text-white"
                    : "bg-green-50 text-green-700 hover:bg-green-100"
                }`}
              >
                <Bell className="w-4 h-4" />
                <span>Unread ({unreadCount})</span>
              </button>
            </div>

            <div className="flex items-center space-x-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="flex items-center space-x-2 px-4 py-2 rounded-lg font-medium bg-green-50 text-green-700 hover:bg-green-100 transition-all text-sm"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>Mark all as read</span>
                </button>
              )}
              <Link
                href="/notifications/preferences"
                className="p-2 rounded-lg bg-green-50 text-green-700 hover:bg-green-100 transition-all"
                title="Notification preferences"
              >
                <Settings className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>

        {/* Notifications List */}
        <div className="space-y-3">
          {filteredNotifications.length > 0 ? (
            filteredNotifications.map((notification) => {
              const Icon = notification.icon;
              return (
                <div
                  key={notification.id}
                  className={`bg-white/70 backdrop-blur-sm rounded-xl border transition-all hover:shadow-md group ${
                    notification.read
                      ? "border-green-100"
                      : "border-green-300 bg-white/90"
                  }`}
                >
                  <div className="p-5">
                    <div className="flex items-start space-x-4">
                      {/* Icon */}
                      <div
                        className={`flex-shrink-0 p-3 rounded-xl ${notification.iconBg}`}
                      >
                        <Icon className={`w-5 h-5 ${notification.iconColor}`} />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between mb-1">
                          <h3
                            className={`font-semibold text-green-900 ${
                              !notification.read ? "font-bold" : ""
                            }`}
                          >
                            {notification.title}
                          </h3>
                          <div className="flex items-center space-x-2 ml-4">
                            {!notification.read && (
                              <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                            )}
                            <button
                              onClick={() => deleteNotification(notification.id)}
                              className="opacity-0 group-hover:opacity-100 p-1 rounded-lg text-green-600 hover:bg-green-100 transition-all"
                            >
                              <X className="w-4 h-4" />
                            </button>
                            <button className="opacity-0 group-hover:opacity-100 p-1 rounded-lg text-green-600 hover:bg-green-100 transition-all">
                              <MoreHorizontal className="w-4 h-4" />
                            </button>
                          </div>
                        </div>

                        <p className="text-sm text-green-700 mb-2">
                          {notification.description}
                        </p>

                        {/* Delivery Channels */}
                        <div className="flex items-center space-x-2 mb-3">
                          <span className="text-xs text-green-600">Sent via:</span>
                          {notification.channels.map((channel) => (
                            <ChannelBadge key={channel} channel={channel} />
                          ))}
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3 text-xs text-green-600">
                            <span className="flex items-center space-x-1">
                              <Clock className="w-3 h-3" />
                              <span>{formatTimestamp(notification.timestamp)}</span>
                            </span>
                          </div>

                          <div className="flex items-center space-x-2">
                            {!notification.read && (
                              <button
                                onClick={() => markAsRead(notification.id)}
                                className="text-xs text-green-600 hover:text-green-800 font-medium transition-colors"
                              >
                                Mark as read
                              </button>
                            )}
                            {notification.actionUrl && (
                              <Link
                                href={notification.actionUrl}
                                className="text-xs bg-gradient-to-r from-green-600 to-green-700 text-white px-3 py-1.5 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all"
                                onClick={() => markAsRead(notification.id)}
                              >
                                {notification.actionText}
                              </Link>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-12 text-center">
              <Bell className="w-16 h-16 mx-auto text-green-300 mb-4" />
              <h3 className="text-lg font-semibold text-green-900 mb-2">
                {filter === "unread"
                  ? "You're all caught up!"
                  : "No notifications yet"}
              </h3>
              <p className="text-green-700 mb-6">
                {filter === "unread"
                  ? "All your notifications have been read."
                  : "We'll notify you when something important happens."}
              </p>
              <Link
                href="/dashboard"
                className="inline-flex items-center space-x-2 bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all"
              >
                <Briefcase className="w-5 h-5" />
                <span>Go to Dashboard</span>
              </Link>
            </div>
          )}
        </div>

        {/* Additional Info */}
        {filteredNotifications.length > 0 && (
          <div className="mt-8 text-center">
            <p className="text-sm text-green-600">
              Showing {filteredNotifications.length} notification
              {filteredNotifications.length !== 1 ? "s" : ""}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

