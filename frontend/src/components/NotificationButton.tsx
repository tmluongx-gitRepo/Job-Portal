"use client";

import { type ReactElement } from "react";
import Link from "next/link";
import { Bell } from "lucide-react";

interface NotificationButtonProps {
  unreadCount?: number;
  className?: string;
  href?: string;
}

export default function NotificationButton({
  unreadCount = 0,
  className = "",
  href = "/notifications",
}: NotificationButtonProps): ReactElement {
  return (
    <Link
      href={href}
      className={`relative p-3 bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 hover:bg-green-50 hover:border-green-300 transition-all group ${className}`}
      title="View notifications"
    >
      <Bell className="w-5 h-5 text-green-700 group-hover:text-green-800 transition-colors" />

      {/* Unread Badge - positioned at top-right corner of rounded rectangle */}
      {unreadCount > 0 && (
        <>
          <span className="absolute -top-1 -right-1 bg-gradient-to-r from-red-500 to-red-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center shadow-lg z-10">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>

          {/* Pulse animation for unread notifications */}
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full animate-ping opacity-75"></span>
        </>
      )}
    </Link>
  );
}
