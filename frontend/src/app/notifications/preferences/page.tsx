"use client";

import { useState } from "react";
import type React from "react";
import Link from "next/link";
import {
  Bell,
  Mail,
  Smartphone,
  ArrowLeft,
  Save,
  Shield,
  Info,
  CheckCircle,
} from "lucide-react";
import {
  defaultJobSeekerPreferences,
  type NotificationPreference,
  type NotificationChannel,
  getChannelInfo,
} from "../../../lib/notifications";

export default function NotificationPreferencesPage(): React.ReactNode {
  const [preferences, setPreferences] = useState<NotificationPreference[]>(
    defaultJobSeekerPreferences
  );
  const [saved, setSaved] = useState(false);
  const [userEmail] = useState("user@example.com"); // TODO: Get from auth context

  const toggleChannel = (
    type: string,
    channel: NotificationChannel
  ): void => {
    setPreferences((prev) =>
      prev.map((pref) =>
        pref.type === type
          ? {
              ...pref,
              channels: { ...pref.channels, [channel]: !pref.channels[channel] },
            }
          : pref
      )
    );
    setSaved(false);
  };

  const handleSave = (): void => {
    // TODO: Save preferences to backend
    console.log("Saving preferences:", preferences);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const categoryLabels = {
    important: {
      label: "Important Notifications",
      description: "Critical updates you shouldn't miss",
      color: "text-red-700",
      bg: "bg-red-50",
      border: "border-red-200",
    },
    updates: {
      label: "Activity Updates",
      description: "Keep track of your job search activity",
      color: "text-blue-700",
      bg: "bg-blue-50",
      border: "border-blue-200",
    },
    promotional: {
      label: "Tips & Recommendations",
      description: "Helpful advice to improve your job search",
      color: "text-green-700",
      bg: "bg-green-50",
      border: "border-green-200",
    },
  };

  const channels: NotificationChannel[] = ["in_app", "email", "push"];

  const groupedPreferences = preferences.reduce(
    (acc, pref) => {
      if (!acc[pref.category]) {
        acc[pref.category] = [];
      }
      acc[pref.category].push(pref);
      return acc;
    },
    {} as Record<string, NotificationPreference[]>
  );

  const getChannelIcon = (channel: NotificationChannel): typeof Bell => {
    switch (channel) {
      case "in_app":
        return Bell;
      case "email":
        return Mail;
      case "push":
        return Smartphone;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/notifications"
            className="inline-flex items-center text-green-700 hover:text-green-800 font-medium mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Notifications
          </Link>

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-gradient-to-r from-green-600 to-green-700 rounded-xl">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-green-900">
                  Notification Preferences
                </h1>
                <p className="text-sm text-green-700">
                  Choose how you want to receive notifications
                </p>
              </div>
            </div>

            {saved && (
              <div className="flex items-center space-x-2 bg-green-100 text-green-800 px-4 py-2 rounded-lg">
                <CheckCircle className="w-5 h-5" />
                <span className="font-medium">Preferences saved!</span>
              </div>
            )}
          </div>
        </div>

        {/* Email Info Banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
          <div className="flex items-start space-x-3">
            <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm text-blue-900 font-medium">
                Email notifications will be sent to: <span className="font-bold">{userEmail}</span>
              </p>
              <p className="text-xs text-blue-700 mt-1">
                Update your email address in your profile settings
              </p>
            </div>
          </div>
        </div>

        {/* Channel Legend */}
        <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6 mb-6">
          <h3 className="text-lg font-semibold text-green-900 mb-4">
            Notification Channels
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {channels.map((channel) => {
              const Icon = getChannelIcon(channel);
              const info = getChannelInfo(channel);
              return (
                <div
                  key={channel}
                  className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg"
                >
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Icon className="w-5 h-5 text-green-700" />
                  </div>
                  <div>
                    <p className="font-semibold text-green-900 text-sm">
                      {info.label}
                    </p>
                    <p className="text-xs text-green-700">{info.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Preferences by Category */}
        <div className="space-y-6">
          {Object.entries(groupedPreferences).map(([category, prefs]) => {
            const categoryInfo =
              categoryLabels[category as keyof typeof categoryLabels];
            return (
              <div
                key={category}
                className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 overflow-hidden"
              >
                {/* Category Header */}
                <div
                  className={`p-4 border-b ${categoryInfo.border} ${categoryInfo.bg}`}
                >
                  <h3
                    className={`font-semibold ${categoryInfo.color} text-lg`}
                  >
                    {categoryInfo.label}
                  </h3>
                  <p className="text-sm text-green-700">
                    {categoryInfo.description}
                  </p>
                </div>

                {/* Preferences List */}
                <div className="divide-y divide-green-100">
                  {prefs.map((pref) => (
                    <div key={pref.type} className="p-6">
                      <div className="mb-4">
                        <h4 className="font-semibold text-green-900 mb-1">
                          {pref.label}
                        </h4>
                        <p className="text-sm text-green-700">
                          {pref.description}
                        </p>
                      </div>

                      {/* Channel Toggles */}
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        {channels.map((channel) => {
                          const Icon = getChannelIcon(channel);
                          const info = getChannelInfo(channel);
                          const isEnabled = pref.channels[channel];

                          return (
                            <button
                              key={channel}
                              onClick={() => toggleChannel(pref.type, channel)}
                              className={`flex items-center justify-between p-3 rounded-lg border-2 transition-all ${
                                isEnabled
                                  ? "bg-green-50 border-green-500"
                                  : "bg-gray-50 border-gray-200 hover:border-gray-300"
                              }`}
                            >
                              <div className="flex items-center space-x-2">
                                <Icon
                                  className={`w-4 h-4 ${
                                    isEnabled
                                      ? "text-green-700"
                                      : "text-gray-400"
                                  }`}
                                />
                                <span
                                  className={`text-sm font-medium ${
                                    isEnabled
                                      ? "text-green-900"
                                      : "text-gray-600"
                                  }`}
                                >
                                  {info.label}
                                </span>
                              </div>
                              <div
                                className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                                  isEnabled
                                    ? "bg-green-600 border-green-600"
                                    : "bg-white border-gray-300"
                                }`}
                              >
                                {isEnabled && (
                                  <CheckCircle className="w-3 h-3 text-white" />
                                )}
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Save Button */}
        <div className="mt-8 flex justify-center">
          <button
            onClick={handleSave}
            className="flex items-center space-x-3 bg-gradient-to-r from-green-600 to-green-700 text-white px-8 py-4 rounded-xl font-semibold hover:from-green-700 hover:to-green-800 transition-all shadow-lg hover:shadow-xl"
          >
            <Save className="w-5 h-5" />
            <span>Save Preferences</span>
          </button>
        </div>

        {/* Additional Info */}
        <div className="mt-8 bg-amber-50 border border-amber-200 rounded-xl p-4">
          <div className="flex items-start space-x-3">
            <Info className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-amber-900">
              <p className="font-medium mb-2">About Notification Channels:</p>
              <ul className="space-y-1 text-amber-800">
                <li>
                  • <strong>In-App:</strong> Notifications appear within Career Harmony when you&apos;re logged in
                </li>
                <li>
                  • <strong>Email:</strong> Notifications are sent to your registered email address
                </li>
                <li>
                  • <strong>Push:</strong> Receive instant notifications on your mobile device (requires mobile app)
                </li>
              </ul>
              <p className="mt-3 text-xs text-amber-700">
                You can change these preferences at any time. Some critical notifications may be sent regardless of your preferences.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}






