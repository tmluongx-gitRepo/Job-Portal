"use client";

import { useState, useEffect, type ReactElement } from "react";
import Link from "next/link";
import {
  Bell,
  Users,
  Calendar,
  CheckCircle,
  Clock,
  Settings,
  Star,
  TrendingUp,
  Briefcase,
  X,
  Filter,
  MoreHorizontal,
  Building2,
  UserPlus,
  Mail,
  Smartphone,
  AlertCircle,
  Eye,
} from "lucide-react";

// Notification types for employers
type EmployerNotificationType =
  | "new_application"
  | "candidate_match"
  | "interview_reminder"
  | "interview_scheduled"
  | "candidate_accepted"
  | "candidate_rejected"
  | "job_posting_expiring"
  | "job_posting_views"
  | "competitor_posting"
  | "active_job_seeker"
  | "message"
  | "system";

type NotificationChannel = "in_app" | "email" | "push";

interface EmployerNotification {
  id: string;
  type: EmployerNotificationType;
  title: string;
  description: string;
  timestamp: Date;
  read: boolean;
  actionUrl?: string;
  actionText?: string;
  icon: typeof Users;
  iconColor: string;
  iconBg: string;
  channels: NotificationChannel[];
  priority: "high" | "medium" | "low";
}

// Mock employer notification data - chronologically ordered
const mockEmployerNotifications: EmployerNotification[] = [
  {
    id: "1",
    type: "new_application",
    title: "3 New Applications Received",
    description:
      "You received 3 new applications for Senior Software Engineer position at TechCorp",
    timestamp: new Date(Date.now() - 1000 * 60 * 15), // 15 minutes ago
    read: false,
    actionUrl: "/applications",
    actionText: "Review Applications",
    icon: Users,
    iconColor: "text-green-600",
    iconBg: "bg-green-100",
    channels: ["in_app", "email", "push"],
    priority: "high",
  },
  {
    id: "2",
    type: "candidate_match",
    title: "5 Candidates Match Your Job Post",
    description:
      "5 active job seekers match the requirements for your Product Manager position",
    timestamp: new Date(Date.now() - 1000 * 60 * 45), // 45 minutes ago
    read: false,
    actionUrl: "/applications",
    actionText: "View Matches",
    icon: Star,
    iconColor: "text-amber-600",
    iconBg: "bg-amber-100",
    channels: ["in_app", "email"],
    priority: "high",
  },
  {
    id: "3",
    type: "interview_reminder",
    title: "Interview Reminder",
    description:
      "Reminder: Interview with Sarah Johnson in 1 hour for Product Manager role",
    timestamp: new Date(Date.now() - 1000 * 60 * 60), // 1 hour ago
    read: false,
    actionUrl: "/employer-dashboard",
    actionText: "View Schedule",
    icon: Calendar,
    iconColor: "text-purple-600",
    iconBg: "bg-purple-100",
    channels: ["in_app", "email", "push"],
    priority: "high",
  },
  {
    id: "4",
    type: "active_job_seeker",
    title: "New Active Job Seekers in Your Area",
    description:
      "15 new job seekers with Software Engineering skills are actively looking in San Francisco",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3), // 3 hours ago
    read: true,
    actionUrl: "/job-posting",
    actionText: "Post a Job",
    icon: UserPlus,
    iconColor: "text-blue-600",
    iconBg: "bg-blue-100",
    channels: ["in_app"],
    priority: "medium",
  },
  {
    id: "5",
    type: "candidate_accepted",
    title: "Candidate Accepted Your Offer",
    description:
      "John Doe accepted your offer for Senior Developer position at TechCorp",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5), // 5 hours ago
    read: true,
    actionUrl: "/applications",
    actionText: "View Details",
    icon: CheckCircle,
    iconColor: "text-green-600",
    iconBg: "bg-green-100",
    channels: ["in_app", "email", "push"],
    priority: "high",
  },
  {
    id: "6",
    type: "job_posting_views",
    title: "Your Job Post is Trending",
    description:
      "Your Senior Software Engineer position received 124 views this week (+45% from last week)",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 8), // 8 hours ago
    read: true,
    actionUrl: "/employer-dashboard",
    actionText: "View Analytics",
    icon: TrendingUp,
    iconColor: "text-blue-600",
    iconBg: "bg-blue-100",
    channels: ["in_app", "email"],
    priority: "medium",
  },
  {
    id: "7",
    type: "competitor_posting",
    title: "Competitor Posted Similar Job",
    description:
      "A competitor posted a Senior Software Engineer position with similar requirements and higher salary range",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 12), // 12 hours ago
    read: true,
    actionUrl: "/jobs",
    actionText: "View Posting",
    icon: Eye,
    iconColor: "text-orange-600",
    iconBg: "bg-orange-100",
    channels: ["in_app"],
    priority: "medium",
  },
  {
    id: "8",
    type: "job_posting_expiring",
    title: "Job Posting Expiring Soon",
    description:
      "Your job posting for UX Designer will expire in 3 days. Consider renewing or editing.",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
    read: true,
    actionUrl: "/job-posting",
    actionText: "Renew Posting",
    icon: AlertCircle,
    iconColor: "text-amber-600",
    iconBg: "bg-amber-100",
    channels: ["in_app", "email"],
    priority: "medium",
  },
  {
    id: "9",
    type: "message",
    title: "New Message from Candidate",
    description: "You have a new message from candidate Jane Smith regarding the interview schedule",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2), // 2 days ago
    read: true,
    actionUrl: "#",
    actionText: "Read Message",
    icon: Mail,
    iconColor: "text-indigo-600",
    iconBg: "bg-indigo-100",
    channels: ["in_app", "email", "push"],
    priority: "high",
  },
  {
    id: "10",
    type: "interview_scheduled",
    title: "Interview Scheduled by Candidate",
    description:
      "Michael Brown confirmed interview slot for tomorrow at 2:00 PM for Backend Developer position",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3), // 3 days ago
    read: true,
    actionUrl: "/employer-dashboard",
    actionText: "View Details",
    icon: Calendar,
    iconColor: "text-purple-600",
    iconBg: "bg-purple-100",
    channels: ["in_app", "email"],
    priority: "high",
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

// Format timestamp
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

export default function EmployerNotificationsPage(): ReactElement {
  const [notifications, setNotifications] = useState<EmployerNotification[]>(
    mockEmployerNotifications
  );
  const [filter, setFilter] = useState<"all" | "unread">("all");

  // Helper to get icon by type
  const getIconByType = (type: EmployerNotificationType): typeof Users => {
    const iconMap: Record<EmployerNotificationType, typeof Users> = {
      new_application: Users,
      candidate_match: Star,
      interview_reminder: Calendar,
      interview_scheduled: Calendar,
      candidate_accepted: CheckCircle,
      candidate_rejected: X,
      job_posting_expiring: AlertCircle,
      job_posting_views: TrendingUp,
      competitor_posting: Eye,
      active_job_seeker: UserPlus,
      message: Mail,
      system: Settings,
    };
    return iconMap[type] || Bell;
  };

  // Load from localStorage on mount and save on changes
  useEffect(() => {
    const stored = localStorage.getItem("employer_notifications");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        // Convert timestamp strings back to Date objects and restore icons
        const withDates = parsed.map((n: EmployerNotification) => ({
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
    localStorage.setItem("employer_notifications", JSON.stringify(notifications));
    
    // Dispatch custom event for dashboard to listen
    const unreadCount = notifications.filter((n) => !n.read).length;
    window.dispatchEvent(
      new CustomEvent("notificationsUpdated", {
        detail: { userType: "employer", unreadCount },
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
                <h1 className="text-3xl font-bold text-green-900 flex items-center space-x-2">
                  <span>Employer Notifications</span>
                  <Building2 className="w-7 h-7 text-green-700" />
                </h1>
                <p className="text-sm text-green-700">
                  Stay updated with candidates and job postings
                </p>
              </div>
            </div>
            <Link
              href="/employer-dashboard"
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

        {/* Notifications List - Chronological Order */}
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
                  } ${
                    notification.priority === "high"
                      ? "ring-2 ring-red-200 ring-opacity-50"
                      : ""
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
                          <div className="flex items-center space-x-2">
                            <h3
                              className={`font-semibold text-green-900 ${
                                !notification.read ? "font-bold" : ""
                              }`}
                            >
                              {notification.title}
                            </h3>
                            {notification.priority === "high" && (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                                High Priority
                              </span>
                            )}
                          </div>
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
                  : "We'll notify you when candidates apply or interact with your jobs."}
              </p>
              <Link
                href="/employer-dashboard"
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
              {filteredNotifications.length !== 1 ? "s" : ""} in chronological order
            </p>
          </div>
        )}
      </div>
    </div>
  );
}


