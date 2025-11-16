"use client";

import { useState, useEffect, type ReactElement } from "react";
import Link from "next/link";

import {
  Building2,
  Users,
  TrendingUp,
  Plus,
  Briefcase,
  Clock,
  Calendar,
  RefreshCw,
  Sparkles,
  Eye,
  Star,
} from "lucide-react";
import { api, ApiError } from "../../lib/api";
import { getCurrentUserId } from "../../lib/auth";
import type { Job, Application, EmployerProfile } from "../../lib/api";

// Employer-focused healthy reminders
const healthyReminders = [
  "Remember: Great hires take time. Focus on finding the right cultural fit, not just filling positions quickly.",
  "Every candidate deserves respectful communication, even if they&apos;re not the right fit.",
  "Diverse hiring practices lead to stronger, more innovative teams.",
  "A candidate's worth isn't determined by a single interview performance.",
  "Small companies can compete with big ones through authentic culture and growth opportunities.",
  "Hiring is about finding mutual fit, not just evaluating candidates.",
  "Transparency about salary and expectations attracts better candidates.",
  "Every 'no' you give respectfully maintains your company's reputation.",
  "Good hiring practices create ambassadors, even among candidates you don&apos;t hire.",
  "Your hiring process reflects your company values—make it count.",
];

const getStatusBadge = (status: string): { bg: string; text: string } => {
  const statusConfig: Record<string, { bg: string; text: string }> = {
    Active: { bg: "bg-green-100", text: "text-green-800" },
    Paused: { bg: "bg-yellow-100", text: "text-yellow-800" },
    Closed: { bg: "bg-gray-100", text: "text-gray-800" },
    Unreviewed: { bg: "bg-yellow-100", text: "text-yellow-800" },
    Reviewed: { bg: "bg-blue-100", text: "text-blue-800" },
    "Interview Scheduled": { bg: "bg-purple-100", text: "text-purple-800" },
  };
  return statusConfig[status] || { bg: "bg-gray-100", text: "text-gray-800" };
};

interface TransformedJobPosting {
  id: string;
  title: string;
  company: string;
  status: string;
  posted: string;
  applications: number;
  newApplications: number;
  interviews: number;
  hired: number;
  location: string;
  salary: string;
}

interface TransformedApplication {
  id: string;
  candidateName: string;
  jobTitle: string;
  company: string;
  appliedDate: string;
  status: string;
  matchScore: number;
  experience: string;
  location: string;
}

interface TransformedInterview {
  id: string;
  candidateName: string;
  jobTitle: string;
  company: string;
  interviewDate: string;
  interviewType: string;
  interviewer: string;
}

function formatDateAgo(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "1 day ago";
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 14) return "1 week ago";
  if (diffDays < 21) return "2 weeks ago";
  if (diffDays < 30) return "3 weeks ago";
  const diffMonths = Math.floor(diffDays / 30);
  if (diffMonths === 1) return "1 month ago";
  return `${diffMonths} months ago`;
}

function formatSalary(
  min: number | null | undefined,
  max: number | null | undefined
): string {
  if (!min && !max) return "Salary not specified";
  if (!min) return `Up to $${max?.toLocaleString()}`;
  if (!max) return `$${min.toLocaleString()}+`;
  return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
}

export default function EmployerDashboard(): ReactElement {
  const userId = getCurrentUserId() || "507f1f77bcf86cd799439011"; // Fallback for testing
  const [selectedCompany, setSelectedCompany] = useState("all");
  const [currentReminder, setCurrentReminder] = useState(healthyReminders[0]);

  // API state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [employerProfile, setEmployerProfile] =
    useState<EmployerProfile | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [_allApplications, setAllApplications] = useState<Application[]>([]);

  // Transformed data
  const [jobPostings, setJobPostings] = useState<TransformedJobPosting[]>([]);
  const [recentApplications, setRecentApplications] = useState<
    TransformedApplication[]
  >([]);
  const [upcomingInterviews, setUpcomingInterviews] = useState<
    TransformedInterview[]
  >([]);

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
        // Fetch employer profile
        let profile: EmployerProfile | null = null;
        let employerProfileId: string | null = null;
        try {
          profile = await api.employerProfiles.getByUserId(userId);
          setEmployerProfile(profile);
          employerProfileId = profile.id;
        } catch (_err) {
          console.info(
            "[Employer Dashboard] Profile not found - cannot fetch jobs/applications"
          );
        }

        if (employerProfileId) {
          // Fetch jobs posted by this employer
          const employerJobs = (await api.jobs.getAll({
            posted_by: employerProfileId,
            limit: 100,
          })) as Job[];
          setJobs(employerJobs);

          // Fetch applications for all jobs
          const jobIds = employerJobs.map((job: Job) => job.id);
          const applicationsPromises = jobIds.map((jobId: string) =>
            api.applications.getAll({ job_id: jobId, limit: 100 })
          );
          const applicationsArrays = await Promise.all(applicationsPromises);
          const flatApplications: Application[] = applicationsArrays.flat();
          setAllApplications(flatApplications);

          // Transform jobs
          const transformedJobs: TransformedJobPosting[] = employerJobs.map(
            (job: Job) => {
              const jobApplications = flatApplications.filter(
                (app: Application) => app.job_id === job.id
              );
              const newApplications = jobApplications.filter(
                (app: Application) => {
                  const appliedDate = new Date(app.applied_date);
                  const sevenDaysAgo = new Date();
                  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
                  return appliedDate >= sevenDaysAgo;
                }
              );
              const interviews = jobApplications.filter(
                (app: Application) =>
                  app.status === "interview_scheduled" ||
                  app.status === "interviewed"
              ).length;
              const hired = jobApplications.filter(
                (app: Application) => app.status === "hired"
              ).length;

              return {
                id: job.id,
                title: job.title,
                company: job.company,
                status: job.is_active ? "Active" : "Paused",
                posted: formatDateAgo(new Date(job.created_at)),
                applications: jobApplications.length,
                newApplications: newApplications.length,
                interviews,
                hired,
                location: job.remote_ok ? "Remote" : job.location,
                salary: formatSalary(job.salary_min, job.salary_max),
              };
            }
          );
          setJobPostings(transformedJobs);

          // Transform recent applications (last 10, sorted by date)
          const sortedApplications = flatApplications
            .sort(
              (a: Application, b: Application) =>
                new Date(b.applied_date).getTime() -
                new Date(a.applied_date).getTime()
            )
            .slice(0, 10);

          const transformedApplications: TransformedApplication[] =
            await Promise.all(
              sortedApplications.map(async (app: Application) => {
                const job = employerJobs.find((j: Job) => j.id === app.job_id);
                // TODO: Fetch job seeker profile to get name, experience, location
                // For now, using placeholder data
                return {
                  id: app.id,
                  candidateName: `Candidate ${app.job_seeker_id.slice(0, 8)}`,
                  jobTitle: job?.title || "Unknown Job",
                  company: job?.company || "Unknown Company",
                  appliedDate: formatDateAgo(new Date(app.applied_date)),
                  status: app.status === "pending" ? "Unreviewed" : "Reviewed",
                  matchScore: 0, // TODO: Calculate match score
                  experience: "Unknown", // TODO: Get from job seeker profile
                  location: job?.location || "Unknown",
                };
              })
            );
          setRecentApplications(transformedApplications);

          // Transform upcoming interviews
          const interviewApplications = flatApplications.filter(
            (app: Application) =>
              app.status === "interview_scheduled" &&
              app.interview_scheduled_date &&
              new Date(app.interview_scheduled_date) >= new Date()
          );
          const transformedInterviews: TransformedInterview[] =
            await Promise.all(
              interviewApplications.map(async (app: Application) => {
                const job = employerJobs.find((j: Job) => j.id === app.job_id);
                const interviewDate = app.interview_scheduled_date
                  ? new Date(app.interview_scheduled_date)
                  : new Date();
                const isToday =
                  interviewDate.toDateString() === new Date().toDateString();
                const isTomorrow =
                  interviewDate.toDateString() ===
                  new Date(Date.now() + 86400000).toDateString();

                let dateStr = "";
                if (isToday) {
                  dateStr = `Today at ${interviewDate.toLocaleTimeString(
                    "en-US",
                    {
                      hour: "numeric",
                      minute: "2-digit",
                    }
                  )}`;
                } else if (isTomorrow) {
                  dateStr = `Tomorrow at ${interviewDate.toLocaleTimeString(
                    "en-US",
                    {
                      hour: "numeric",
                      minute: "2-digit",
                    }
                  )}`;
                } else {
                  dateStr = interviewDate.toLocaleDateString("en-US", {
                    weekday: "short",
                    month: "short",
                    day: "numeric",
                    hour: "numeric",
                    minute: "2-digit",
                  });
                }

                return {
                  id: app.id,
                  candidateName: `Candidate ${app.job_seeker_id.slice(0, 8)}`, // TODO: Get from profile
                  jobTitle: job?.title || "Unknown Job",
                  company: job?.company || "Unknown Company",
                  interviewDate: dateStr,
                  interviewType: "Interview", // TODO: Get from application data
                  interviewer: profile?.name || "Unknown", // TODO: Get from employer profile
                };
              })
            );
          setUpcomingInterviews(transformedInterviews);
        } else {
          // No profile means no data
          setJobPostings([]);
          setRecentApplications([]);
          setUpcomingInterviews([]);
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
  }, []);

  // Get unique companies from jobs
  const companies = Array.from(new Set(jobs.map((job) => job.company)));

  // Filter data based on selected company
  const filteredJobPostings =
    selectedCompany === "all"
      ? jobPostings
      : jobPostings.filter((job) => job.company === selectedCompany);

  const filteredApplications =
    selectedCompany === "all"
      ? recentApplications
      : recentApplications.filter((app) => app.company === selectedCompany);

  const filteredInterviews =
    selectedCompany === "all"
      ? upcomingInterviews
      : upcomingInterviews.filter(
          (interview) => interview.company === selectedCompany
        );

  // Calculate summary metrics based on filtered data
  const totalActiveJobs = filteredJobPostings.filter(
    (job) => job.status === "Active"
  ).length;
  const totalApplications = filteredJobPostings.reduce(
    (sum, job) => sum + job.applications,
    0
  );
  const totalNewApplications = filteredJobPostings.reduce(
    (sum, job) => sum + job.newApplications,
    0
  );
  const totalInterviews = filteredJobPostings.reduce(
    (sum, job) => sum + job.interviews,
    0
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 mx-auto text-green-600 animate-spin mb-4" />
          <p className="text-green-800">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100 flex items-center justify-center">
        <div className="text-center max-w-md">
          <Building2 className="w-12 h-12 mx-auto text-red-500 mb-4" />
          <p className="text-red-800 font-semibold mb-2">
            Error loading dashboard
          </p>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-green-900 mb-2 flex items-center">
                Good morning, {employerProfile?.company_name || "Employer"}!
                <Building2 className="w-8 h-8 ml-3 text-green-600" />
              </h1>
              <p className="text-green-700">
                Ready to connect great talent with meaningful opportunities?
              </p>
            </div>

            {/* Company Selector */}
            {companies.length > 0 && (
              <div className="relative text-right w-full md:w-auto">
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Company Filter:
                </label>
                <select
                  value={selectedCompany}
                  onChange={(e) => setSelectedCompany(e.target.value)}
                  className="px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 bg-white/80 min-w-[200px] w-full md:w-auto"
                >
                  <option value="all">All Companies</option>
                  {companies.map((company) => (
                    <option key={company} value={company}>
                      {company}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </div>

        {/* Daily Reminder - Employer Version */}
        <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-green-800 flex items-center">
              <Sparkles className="w-5 h-5 mr-2" />
              Hiring Wisdom Reminder
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

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-green-700">
                Active Job Postings
              </h3>
              <Briefcase className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-green-900">
              {totalActiveJobs}
            </p>
            <p className="text-xs text-green-600 mb-4 flex items-center">
              Opportunities available
              <Building2 className="w-3 h-3 ml-1 text-green-500" />
            </p>
            <div className="space-y-2">
              <Link
                href="/job-posting"
                className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm"
              >
                <Plus className="w-4 h-4 mr-2" />
                Post New Job
              </Link>
              <button className="w-full bg-green-50 text-green-700 border border-green-300 py-2 px-4 rounded-lg font-medium hover:bg-green-100 transition-all flex items-center justify-center text-sm">
                <Eye className="w-4 h-4 mr-2" />
                Manage Jobs
              </button>
            </div>
          </div>

          <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-green-700">
                New Applications
              </h3>
              <Users className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-green-900">
              {totalNewApplications}
            </p>
            <p className="text-xs text-green-600 mb-4 flex items-center">
              Awaiting your review
              <Clock className="w-3 h-3 ml-1 text-amber-500" />
            </p>
            {filteredJobPostings.length > 0 && filteredJobPostings[0] && (
              <Link
                href={`/applications?jobId=${filteredJobPostings[0].id}`}
                className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm"
              >
                <Eye className="w-4 h-4 mr-2" />
                Review Applications
              </Link>
            )}
          </div>

          <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-green-700">
                Interviews This Week
              </h3>
              <Calendar className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-green-900">
              {totalInterviews}
            </p>
            <p className="text-xs text-green-600 mb-4 flex items-center">
              Great connections ahead!
              <Calendar className="w-3 h-3 ml-1 text-green-500" />
            </p>
            <button className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm">
              <Calendar className="w-4 h-4 mr-2" />
              Manage Schedule
            </button>
          </div>

          <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-green-700">
                Total Applications
              </h3>
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-green-900">
              {totalApplications}
            </p>
            <p className="text-xs text-green-600 mb-4 flex items-center">
              Interest in your roles
              <TrendingUp className="w-3 h-3 ml-1 text-green-500" />
            </p>
            <div className="space-y-2">
              <button className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm">
                <TrendingUp className="w-4 h-4 mr-2" />
                View Analytics
              </button>
              <button className="w-full bg-green-50 text-green-700 border border-green-300 py-2 px-4 rounded-lg font-medium hover:bg-green-100 transition-all flex items-center justify-center text-sm">
                <Users className="w-4 h-4 mr-2" />
                Manage Companies
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Job Postings Overview */}
          <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-green-900">
                Your Job Postings
              </h2>
              <button className="text-green-700 hover:text-green-800 font-medium transition-colors">
                View All
              </button>
            </div>

            <div className="space-y-4">
              {filteredJobPostings.map((job) => (
                <div
                  key={job.id}
                  className="bg-white/60 rounded-lg p-4 border border-green-100"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-semibold text-green-900">
                        {job.title}
                      </h3>
                      <p className="text-sm text-green-700">{job.company}</p>
                      <p className="text-xs text-green-600">
                        {job.location} • {job.salary}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span
                        className={`text-xs px-2 py-1 rounded-full font-medium ${
                          getStatusBadge(job.status).bg
                        } ${getStatusBadge(job.status).text}`}
                      >
                        {job.status}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 text-xs text-green-700">
                    <div className="text-center">
                      <p className="font-semibold">{job.applications}</p>
                      <p>Total Applied</p>
                    </div>
                    <div className="text-center">
                      <p className="font-semibold text-amber-600">
                        {job.newApplications}
                      </p>
                      <p>New</p>
                    </div>
                    <div className="text-center">
                      <p className="font-semibold">{job.interviews}</p>
                      <p>Interviews</p>
                    </div>
                    <div className="text-center">
                      <p className="font-semibold text-green-600">
                        {job.hired}
                      </p>
                      <p>Hired</p>
                    </div>
                  </div>

                  <div className="mt-2 flex items-center justify-between">
                    <p className="text-xs text-green-600">
                      Posted {job.posted}
                    </p>
                    {process.env.NODE_ENV === "development" && (
                      <button
                        onClick={() => {
                          void navigator.clipboard.writeText(job.id);
                          alert(`Job ID copied: ${job.id}`);
                        }}
                        className="text-xs text-green-500 font-mono hover:text-green-700 hover:underline cursor-pointer"
                        title="Click to copy full Job ID (Dev Only)"
                      >
                        ID: {job.id.slice(0, 8)}...
                      </button>
                    )}
                  </div>

                  <Link
                    href={`/applications?jobId=${job.id}`}
                    className="mt-3 w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm"
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    View Applications ({job.applications})
                  </Link>
                </div>
              ))}
            </div>

            {filteredJobPostings.length === 0 && (
              <div className="text-center py-8">
                <Briefcase className="w-12 h-12 mx-auto text-green-300 mb-4" />
                <p className="text-green-600">
                  {selectedCompany === "all"
                    ? "No job postings found. Create your first job posting to get started!"
                    : `No job postings found for ${selectedCompany}`}
                </p>
              </div>
            )}

            <Link
              href="/job-posting"
              className="w-full mt-4 bg-gradient-to-r from-green-600 to-green-700 text-white py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center"
            >
              <Plus className="w-5 h-5 mr-2" />
              Create New Job Posting
            </Link>
          </div>

          {/* Recent Applications */}
          <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-green-900">
                Recent Applications
              </h2>
              <button className="text-green-700 hover:text-green-800 font-medium transition-colors">
                View All
              </button>
            </div>

            <div className="space-y-4">
              {filteredApplications.map((application) => (
                <div
                  key={application.id}
                  className="bg-white/60 rounded-lg p-4 border border-green-100"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-semibold text-green-900">
                        {application.candidateName}
                      </h3>
                      <p className="text-sm text-green-700">
                        {application.jobTitle}
                      </p>
                      <p className="text-xs text-green-600">
                        Candidate for: {application.company}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Star className="w-4 h-4 text-amber-500" />
                      <span className="text-sm font-medium text-green-800">
                        {application.matchScore}%
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-4 text-xs text-green-600">
                      <span>{application.experience} experience</span>
                      <span>{application.location}</span>
                    </div>
                    <span
                      className={`text-xs px-2 py-1 rounded-full font-medium ${
                        getStatusBadge(application.status).bg
                      } ${getStatusBadge(application.status).text}`}
                    >
                      {application.status}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <p className="text-xs text-green-600">
                      Applied {application.appliedDate}
                    </p>
                    <button className="text-green-600 hover:text-green-800 text-sm font-medium transition-colors">
                      Review →
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {filteredApplications.length === 0 && (
              <div className="text-center py-8">
                <Users className="w-12 h-12 mx-auto text-green-300 mb-4" />
                <p className="text-green-600">
                  {selectedCompany === "all"
                    ? "No recent applications yet. Applications will appear here once candidates apply to your jobs."
                    : `No recent applications for ${selectedCompany}`}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Upcoming Interviews */}
        <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-green-900">
              Upcoming Interviews
            </h2>
            <button className="text-green-700 hover:text-green-800 font-medium transition-colors">
              View Calendar
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredInterviews.map((interview) => (
              <div
                key={interview.id}
                className="bg-white/60 rounded-lg p-4 border border-green-100"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-green-900">
                      {interview.candidateName}
                    </h3>
                    <p className="text-sm text-green-700">
                      {interview.jobTitle}
                    </p>
                    <p className="text-xs text-green-600">
                      Candidate for: {interview.company}
                    </p>
                  </div>
                  <Calendar className="w-5 h-5 text-green-500" />
                </div>

                <div className="space-y-1 text-sm text-green-700">
                  <p>
                    <span className="font-medium">When:</span>{" "}
                    {interview.interviewDate}
                  </p>
                  <p>
                    <span className="font-medium">Type:</span>{" "}
                    {interview.interviewType}
                  </p>
                  <p>
                    <span className="font-medium">Interviewer:</span>{" "}
                    {interview.interviewer}
                  </p>
                </div>

                <div className="flex gap-2 mt-4">
                  <button className="flex-1 bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-3 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all text-sm">
                    Join Meeting
                  </button>
                  <button className="flex-1 bg-green-50 text-green-700 border border-green-300 py-2 px-3 rounded-lg font-medium hover:bg-green-100 transition-all text-sm">
                    Reschedule
                  </button>
                </div>
              </div>
            ))}
          </div>

          {filteredInterviews.length === 0 && (
            <div className="text-center py-8">
              <Calendar className="w-12 h-12 mx-auto text-green-300 mb-4" />
              <p className="text-green-600">
                {selectedCompany === "all"
                  ? "No upcoming interviews scheduled. Interviews will appear here once scheduled."
                  : `No upcoming interviews for ${selectedCompany}`}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
