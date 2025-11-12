"use client";

import { useState, useEffect, type ReactElement } from "react";

import Link from "next/link";
import {
  Leaf,
  Heart,
  Search,
  FileText,
  Star,
  Calendar,
  TrendingUp,
  Plus,
  Briefcase,
  Clock,
  CheckCircle,
  RefreshCw,
  Sparkles,
} from "lucide-react";
import { api, ApiError } from "../../lib/api";
import type {
  Application,
  JobSeekerProfile,
  Recommendation,
} from "../../lib/api";

// Sample data removed - now fetched from API

const healthyReminders = [
  "Remember: Every 'no' brings you closer to your perfect 'yes'.",
  "Your worth isn't determined by application responses.",
  "It's okay to take breaks from job searching when you need them.",
  "Quality applications matter more than quantity.",
  "You're allowed to have standards for how you want to be treated.",
  "Job hunting is temporary - your resilience is permanent.",
];

export default function DashboardPage(): ReactElement {
  // ⚠️ TODO: Replace with actual user data from auth context when authentication is implemented
  const userName = "Alex";
  const userId = "507f1f77bcf86cd799439011"; // PLACEHOLDER - Valid ObjectId format for testing

  const [currentReminder, setCurrentReminder] = useState(healthyReminders[0]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // API data
  const [applications, setApplications] = useState<Application[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [profile, setProfile] = useState<JobSeekerProfile | null>(null);
  const [_jobSeekerProfileId, setJobSeekerProfileId] = useState<string | null>(
    null
  );

  const generateReminder = (): void => {
    const randomIndex = Math.floor(Math.random() * healthyReminders.length);
    setCurrentReminder(healthyReminders[randomIndex]);
  };

  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async (): Promise<void> => {
      setLoading(true);
      setError(null);

      try {
        // First, fetch profile to get job seeker profile ID
        let profileId: string | null = null;
        try {
          const userProfile = (await api.jobSeekerProfiles.getByUserId(
            userId
          )) as JobSeekerProfile;
          setProfile(userProfile);
          profileId = userProfile.id;
          setJobSeekerProfileId(profileId);
        } catch (_err) {
          // Profile might not exist - that's okay, but we can't fetch applications/recommendations
          console.info(
            "[Dashboard] Profile not found - cannot fetch applications/recommendations"
          );
        }

        if (profileId) {
          // Fetch applications for this job seeker
          const apps = (await api.applications.getAll({
            job_seeker_id: profileId,
            limit: 10,
          })) as Application[];
          setApplications(apps);

          // Fetch recommendations
          const recs = (await api.recommendations.getForJobSeeker(profileId, {
            limit: 5,
            include_viewed: false,
            include_dismissed: false,
            include_applied: false,
          })) as Recommendation[];
          setRecommendations(recs);
        } else {
          // No profile means no applications or recommendations yet
          setApplications([]);
          setRecommendations([]);
        }
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
        if (err instanceof ApiError) {
          setError(`Failed to load dashboard: ${err.message}`);
        } else {
          setError("An unexpected error occurred. Please try again.");
        }
      } finally {
        setLoading(false);
      }
    };

    void fetchDashboardData();
  }, [userId]);

  // Calculate stats from fetched data
  const calculateStats = (): {
    applicationsThisWeek: number;
    interviewsScheduled: number;
    profileViews: number;
    newMatches: number;
  } => {
    const now = new Date();
    const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

    const applicationsThisWeek = applications.filter((app) => {
      const appliedDate = new Date(app.applied_date);
      return appliedDate >= oneWeekAgo;
    }).length;

    const interviewsScheduled = applications.filter((app) => {
      return (
        app.status === "Interview Scheduled" ||
        app.interview_scheduled_date !== null
      );
    }).length;

    const profileViews = profile?.profile_views || 0;

    const newMatches = recommendations.filter(
      (rec) => !rec.viewed && !rec.dismissed && !rec.applied
    ).length;

    return {
      applicationsThisWeek,
      interviewsScheduled,
      profileViews,
      newMatches,
    };
  };

  const stats = calculateStats();

  // Transform applications for display
  // Note: Applications include job_id but not job details
  // For now, we'll show the job_id - in the future we could fetch job details
  const transformedApplications = applications.slice(0, 3).map((app) => {
    // Format applied date as "X days ago"
    const formatAppliedDate = (date: Date): string => {
      const now = new Date();
      const diffTime = Math.abs(now.getTime() - date.getTime());
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

      if (diffDays === 0) return "today";
      if (diffDays === 1) return "1 day ago";
      if (diffDays < 7) return `${diffDays} days ago`;
      if (diffDays < 14) return "1 week ago";
      if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
      if (diffDays < 60) return "1 month ago";
      return `${Math.floor(diffDays / 30)} months ago`;
    };

    // Determine next step based on status
    let nextStep = app.next_step || "Application in queue for review";
    if (app.status === "Interview Scheduled" && app.interview_scheduled_date) {
      const interviewDate = new Date(app.interview_scheduled_date);
      nextStep = `Interview scheduled for ${interviewDate.toLocaleDateString()}`;
    } else if (app.status === "Under Review") {
      nextStep = "Waiting for initial response";
    }

    return {
      id: app.id,
      company: `Job ${app.job_id.substring(0, 8)}...`, // TODO: Fetch job details to get company name
      role: "View job details", // TODO: Fetch job details to get job title
      status: app.status,
      appliedDate: formatAppliedDate(app.applied_date),
      nextStep,
      jobId: app.job_id, // Store job ID for potential linking
    };
  });

  // Transform recommendations for display
  const transformedRecommendations = recommendations.slice(0, 3).map((rec) => ({
    id: rec.id,
    company: rec.job_company || "Company",
    role: rec.job_title || "Job",
    match: `${rec.match_percentage || 0}%`,
    reason: rec.reasoning || "Great match for your skills and experience",
  }));

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Loading State */}
        {loading && (
          <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-12 text-center mb-8">
            <RefreshCw className="w-8 h-8 text-green-600 animate-spin mx-auto mb-4" />
            <p className="text-green-700">Loading dashboard...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-8">
            <p className="text-red-800 font-semibold mb-2">Error</p>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* Welcome Section */}
        {!loading && (
          <>
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-green-900 mb-2 flex items-center">
                Good morning, {userName}!
                <Leaf className="w-8 h-8 ml-3 text-green-600" />
              </h1>
              <p className="text-green-700">
                Ready to continue nurturing your career growth?
              </p>
            </div>

            {/* Daily Reminder */}
            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6 mb-8">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-green-800 flex items-center">
                  <Heart className="w-5 h-5 mr-2" />
                  Your Daily Reminder
                </h3>
                <button
                  onClick={generateReminder}
                  className="flex items-center space-x-2 text-green-600 hover:text-green-800 transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span className="text-sm">New Reminder</span>
                </button>
              </div>
              <div className="bg-gradient-to-r from-green-50 to-amber-50 border border-green-200 rounded-lg p-4">
                <p className="text-green-800 font-medium italic">
                  &quot;{currentReminder}&quot;
                </p>
              </div>
            </div>

            {/* Quick Stats with Integrated Actions */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-green-700">
                    Applications This Week
                  </h3>
                  <Briefcase className="w-5 h-5 text-green-600" />
                </div>
                <p className="text-2xl font-bold text-green-900">
                  {stats.applicationsThisWeek}
                </p>
                <p className="text-xs text-green-600 mb-4 flex items-center">
                  Quality over quantity
                  <Heart className="w-3 h-3 ml-1 text-green-500" />
                </p>
                <div className="space-y-2">
                  <Link
                    href="/jobs"
                    className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm"
                  >
                    <Search className="w-4 h-4 mr-2" />
                    Search New Jobs
                  </Link>
                  <Link
                    href="/applications"
                    className="w-full bg-green-50 text-green-700 border border-green-300 py-2 px-4 rounded-lg font-medium hover:bg-green-100 transition-all flex items-center justify-center text-sm"
                  >
                    <Briefcase className="w-4 h-4 mr-2" />
                    View Applications
                  </Link>
                </div>
              </div>

              <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-green-700">
                    Interviews Scheduled
                  </h3>
                  <Calendar className="w-5 h-5 text-green-600" />
                </div>
                <p className="text-2xl font-bold text-green-900">
                  {stats.interviewsScheduled}
                </p>
                <p className="text-xs text-green-600 mb-4 flex items-center">
                  You&apos;ve got this!
                  <Calendar className="w-3 h-3 ml-1 text-green-500" />
                </p>
                <Link
                  href="/applications"
                  className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm"
                >
                  <Calendar className="w-4 h-4 mr-2" />
                  Manage Interviews
                </Link>
              </div>

              <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-green-700">
                    Profile Views
                  </h3>
                  <TrendingUp className="w-5 h-5 text-green-600" />
                </div>
                <p className="text-2xl font-bold text-green-900">
                  {stats.profileViews}
                </p>
                <p className="text-xs text-green-600 mb-4 flex items-center">
                  People notice you
                  <Star className="w-3 h-3 ml-1 text-amber-500" />
                </p>
                <Link
                  href="/profile"
                  className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Update Profile
                </Link>
              </div>

              <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-green-700">
                    New Matches
                  </h3>
                  <Star className="w-5 h-5 text-green-600" />
                </div>
                <p className="text-2xl font-bold text-green-900">
                  {stats.newMatches}
                </p>
                <p className="text-xs text-green-600 mb-4 flex items-center">
                  Great opportunities waiting!
                  <TrendingUp className="w-3 h-3 ml-1 text-green-500" />
                </p>
                <div className="space-y-2">
                  <Link
                    href="/profile"
                    className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm"
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    Update Resume
                  </Link>
                  <a
                    href="#recommendations-section"
                    className="w-full bg-green-50 text-green-700 border border-green-300 py-2 px-4 rounded-lg font-medium hover:bg-green-100 transition-all flex items-center justify-center text-sm"
                  >
                    <Star className="w-4 h-4 mr-2" />
                    View Matches
                  </a>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Recent Applications */}
              <div
                id="applications-section"
                className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6"
              >
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-green-900">
                    Your Applications
                  </h2>
                  <Link
                    href="/applications"
                    className="text-green-700 hover:text-green-800 font-medium transition-colors"
                  >
                    View All
                  </Link>
                </div>

                <div className="space-y-4">
                  {transformedApplications.length > 0 ? (
                    transformedApplications.map((app) => (
                      <div
                        key={app.id}
                        className="bg-white/60 rounded-lg p-4 border border-green-100"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h3 className="font-semibold text-green-900">
                              {app.role}
                            </h3>
                            <p className="text-sm text-green-700">
                              {app.company}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            {app.status === "Interview Scheduled" && (
                              <Calendar className="w-4 h-4 text-amber-600" />
                            )}
                            {app.status === "Under Review" && (
                              <Clock className="w-4 h-4 text-blue-600" />
                            )}
                            {app.status === "Application Submitted" && (
                              <CheckCircle className="w-4 h-4 text-green-600" />
                            )}
                            <span
                              className={`text-xs px-2 py-1 rounded-full ${
                                app.status === "Interview Scheduled"
                                  ? "bg-amber-100 text-amber-800"
                                  : app.status === "Under Review"
                                    ? "bg-blue-100 text-blue-800"
                                    : "bg-green-100 text-green-800"
                              }`}
                            >
                              {app.status}
                            </span>
                          </div>
                        </div>
                        <p className="text-xs text-green-600 mb-2">
                          Applied {app.appliedDate}
                        </p>
                        <p className="text-sm text-green-700">{app.nextStep}</p>
                      </div>
                    ))
                  ) : (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                      <p className="text-green-700 text-sm">
                        No applications yet. Start applying to jobs to track
                        your progress!
                      </p>
                    </div>
                  )}
                </div>

                <Link
                  href="/applications"
                  className="w-full mt-4 bg-gradient-to-r from-green-600 to-green-700 text-white py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  Track New Application
                </Link>
              </div>

              {/* Recommendations */}
              <div
                id="recommendations-section"
                className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6"
              >
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-green-900">
                    Recommended for You
                  </h2>
                  <Link
                    href="/jobs"
                    className="text-green-700 hover:text-green-800 font-medium transition-colors"
                  >
                    See More
                  </Link>
                </div>

                <div className="space-y-4">
                  {transformedRecommendations.length > 0 ? (
                    transformedRecommendations.map((rec) => (
                      <div
                        key={rec.id}
                        className="bg-white/60 rounded-lg p-4 border border-green-100"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <h3 className="font-semibold text-green-900">
                              {rec.role}
                            </h3>
                            <p className="text-sm text-green-700">
                              {rec.company}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Star className="w-4 h-4 text-amber-500" />
                            <span className="text-sm font-medium text-green-800">
                              {rec.match} match
                            </span>
                          </div>
                        </div>
                        <p className="text-sm text-green-600 mb-3 flex items-start">
                          <span className="flex items-center mr-2">
                            <span className="font-medium">Harmony says</span>
                            <Sparkles className="w-3 h-3 ml-1 text-amber-500" />
                          </span>
                          <span className="italic">
                            &quot;{rec.reason}&quot;
                          </span>
                        </p>
                        <Link
                          href="/jobs"
                          className="text-green-700 hover:text-green-800 font-medium text-sm transition-colors"
                        >
                          View Details →
                        </Link>
                      </div>
                    ))
                  ) : (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                      <p className="text-green-700 text-sm">
                        No recommendations yet. Complete your profile to get
                        personalized job matches!
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
