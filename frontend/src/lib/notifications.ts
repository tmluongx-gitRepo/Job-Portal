// Export notification types and mock data for reuse across components
export type NotificationType =
  | "application_update"
  | "interview_scheduled"
  | "job_match"
  | "profile_view"
  | "message"
  | "recommendation"
  | "system"
  | "new_application"
  | "interview_reminder"
  | "candidate_accepted"
  | "job_expired";

export type NotificationChannel = "in_app" | "email" | "push";

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  description: string;
  timestamp: Date;
  read: boolean;
  actionUrl?: string;
  actionText?: string;
  icon: string; // Icon name as string for serialization
  iconColor: string;
  iconBg: string;
  channels: NotificationChannel[]; // Which channels this notification was sent through
}

// Notification Preferences
export interface NotificationPreference {
  type: NotificationType;
  label: string;
  description: string;
  channels: {
    in_app: boolean;
    email: boolean;
    push: boolean;
  };
  category: "important" | "updates" | "promotional";
}

// Default preferences for Job Seekers
export const defaultJobSeekerPreferences: NotificationPreference[] = [
  {
    type: "application_update",
    label: "Application Updates",
    description: "When your application status changes",
    channels: { in_app: true, email: true, push: true },
    category: "important",
  },
  {
    type: "interview_scheduled",
    label: "Interview Scheduled",
    description: "When an interview is scheduled or rescheduled",
    channels: { in_app: true, email: true, push: true },
    category: "important",
  },
  {
    type: "job_match",
    label: "Job Matches",
    description: "New jobs that match your profile",
    channels: { in_app: true, email: true, push: false },
    category: "updates",
  },
  {
    type: "profile_view",
    label: "Profile Views",
    description: "When employers view your profile",
    channels: { in_app: true, email: false, push: false },
    category: "updates",
  },
  {
    type: "message",
    label: "Messages",
    description: "New messages from employers or recruiters",
    channels: { in_app: true, email: true, push: true },
    category: "important",
  },
  {
    type: "recommendation",
    label: "Career Tips",
    description: "Helpful career advice and recommendations",
    channels: { in_app: true, email: false, push: false },
    category: "promotional",
  },
  {
    type: "system",
    label: "System Updates",
    description: "Important system announcements and updates",
    channels: { in_app: true, email: false, push: false },
    category: "updates",
  },
];

// Default preferences for Employers
export const defaultEmployerPreferences: NotificationPreference[] = [
  {
    type: "new_application",
    label: "New Applications",
    description: "When candidates apply to your job postings",
    channels: { in_app: true, email: true, push: true },
    category: "important",
  },
  {
    type: "interview_reminder",
    label: "Interview Reminders",
    description: "Reminders for upcoming interviews",
    channels: { in_app: true, email: true, push: true },
    category: "important",
  },
  {
    type: "candidate_accepted",
    label: "Offer Acceptances",
    description: "When candidates accept your job offers",
    channels: { in_app: true, email: true, push: true },
    category: "important",
  },
  {
    type: "job_expired",
    label: "Job Posting Expiring",
    description: "When your job postings are about to expire",
    channels: { in_app: true, email: true, push: false },
    category: "updates",
  },
  {
    type: "profile_view",
    label: "Company Profile Views",
    description: "Analytics about your company profile views",
    channels: { in_app: true, email: false, push: false },
    category: "updates",
  },
  {
    type: "system",
    label: "System Updates",
    description: "Important system announcements and updates",
    channels: { in_app: true, email: false, push: false },
    category: "updates",
  },
];

// Job Seeker Notifications
export const mockJobSeekerNotifications: Notification[] = [
  {
    id: "1",
    type: "application_update",
    title: "Application Update",
    description:
      "Your application for Senior Software Engineer at TechCorp has been reviewed",
    timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
    read: false,
    actionUrl: "/applications",
    actionText: "View Application",
    icon: "Briefcase",
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
    icon: "Calendar",
    iconColor: "text-purple-600",
    iconBg: "bg-purple-100",
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
    icon: "Star",
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
    icon: "Users",
    iconColor: "text-blue-600",
    iconBg: "bg-blue-100",
    channels: ["in_app"],
  },
];

// Employer Notifications
export const mockEmployerNotifications: Notification[] = [
  {
    id: "1",
    type: "new_application",
    title: "New Application Received",
    description:
      "You received 3 new applications for Senior Software Engineer position",
    timestamp: new Date(Date.now() - 1000 * 60 * 15), // 15 minutes ago
    read: false,
    actionUrl: "/applications",
    actionText: "Review Applications",
    icon: "Users",
    iconColor: "text-green-600",
    iconBg: "bg-green-100",
    channels: ["in_app", "email", "push"],
  },
  {
    id: "2",
    type: "interview_reminder",
    title: "Interview Reminder",
    description:
      "Reminder: You have an interview with Sarah Johnson in 1 hour for Product Manager role",
    timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
    read: false,
    actionUrl: "/employer-dashboard",
    actionText: "View Schedule",
    icon: "Calendar",
    iconColor: "text-purple-600",
    iconBg: "bg-purple-100",
    channels: ["in_app", "email", "push"],
  },
  {
    id: "3",
    type: "candidate_accepted",
    title: "Candidate Accepted Offer",
    description: "John Doe accepted your offer for Senior Developer position",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3), // 3 hours ago
    read: false,
    actionUrl: "/applications",
    actionText: "View Details",
    icon: "CheckCircle",
    iconColor: "text-green-600",
    iconBg: "bg-green-100",
    channels: ["in_app", "email", "push"],
  },
  {
    id: "4",
    type: "job_expired",
    title: "Job Posting Expiring Soon",
    description:
      "Your job posting for UX Designer will expire in 3 days. Consider renewing.",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 12), // 12 hours ago
    read: true,
    actionUrl: "/job-posting",
    actionText: "Renew Posting",
    icon: "Clock",
    iconColor: "text-amber-600",
    iconBg: "bg-amber-100",
    channels: ["in_app", "email"],
  },
  {
    id: "5",
    type: "profile_view",
    title: "Company Profile Views",
    description: "Your company profile was viewed 45 times this week",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
    read: true,
    actionUrl: "/employer-dashboard",
    actionText: "View Analytics",
    icon: "TrendingUp",
    iconColor: "text-blue-600",
    iconBg: "bg-blue-100",
    channels: ["in_app"],
  },
];

// Utility function to format timestamps
export function formatNotificationTimestamp(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const diffWeeks = Math.floor(diffDays / 7);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffWeeks < 4) return `${diffWeeks}w ago`;
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

// Helper to get channel icon/label
export function getChannelInfo(channel: NotificationChannel): {
  label: string;
  icon: string;
  description: string;
} {
  const channelMap = {
    in_app: {
      label: "In-App",
      icon: "Bell",
      description: "Receive notifications within the application",
    },
    email: {
      label: "Email",
      icon: "Mail",
      description: "Receive notifications via email",
    },
    push: {
      label: "Push",
      icon: "Smartphone",
      description: "Receive push notifications on your mobile device",
    },
  };
  return channelMap[channel];
}
