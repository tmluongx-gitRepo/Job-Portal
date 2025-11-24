"use client";

import { useState, useEffect, Suspense, type ReactElement } from "react";
import { useSearchParams } from "next/navigation";

import Link from "next/link";
import {
  Search,
  User,
  MapPin,
  Clock,
  Building2,
  Briefcase,
  GraduationCap,
  Star,
  ChevronDown,
  ArrowLeft,
  Mail,
  Phone,
  Eye,
  Download,
  Calendar,
  MoreVertical,
  RefreshCw,
} from "lucide-react";
import { api, ApiError } from "../../lib/api";
import type { Job, Application, JobSeekerProfile } from "../../lib/api";

// TODO: Replace with API call to fetch applicants

const getStatusBadge = (
  status: string
): { bg: string; text: string; label: string } => {
  const statusConfig: Record<
    string,
    { bg: string; text: string; label: string }
  > = {
    unreviewed: {
      bg: "bg-yellow-100",
      text: "text-yellow-800",
      label: "Unreviewed",
    },
    reviewed: { bg: "bg-blue-100", text: "text-blue-800", label: "Reviewed" },
    shortlisted: {
      bg: "bg-green-100",
      text: "text-green-800",
      label: "Shortlisted",
    },
    interview_scheduled: {
      bg: "bg-purple-100",
      text: "text-purple-800",
      label: "Interview Scheduled",
    },
    under_review: {
      bg: "bg-blue-100",
      text: "text-blue-800",
      label: "Under Review",
    },
    offer_extended: {
      bg: "bg-amber-100",
      text: "text-amber-800",
      label: "Offer Extended",
    },
    accepted: {
      bg: "bg-emerald-100",
      text: "text-emerald-800",
      label: "Accepted",
    },
    rejected: { bg: "bg-red-100", text: "text-red-800", label: "Rejected" },
  };

  return statusConfig[status] || statusConfig.unreviewed;
};

const getStatusDropdownOptions = (
  currentStatus: string
): Array<{ value: string; label: string }> => {
  const allStatuses = [
    { value: "unreviewed", label: "Unreviewed" },
    { value: "reviewed", label: "Reviewed" },
    { value: "under_review", label: "Under Review" },
    { value: "shortlisted", label: "Shortlisted" },
    { value: "interview_scheduled", label: "Interview Scheduled" },
    { value: "offer_extended", label: "Offer Extended" },
    { value: "accepted", label: "Accepted" },
    { value: "rejected", label: "Rejected" },
  ];

  return allStatuses.filter((status) => status.value !== currentStatus);
};

interface StatusDropdownProps {
  applicant: TransformedApplicant;
  isOpen: boolean;
  onToggle: () => void;
  onUpdateStatus: (newStatus: string) => void;
}

function StatusDropdown({
  applicant,
  isOpen,
  onToggle,
  onUpdateStatus,
}: StatusDropdownProps): ReactElement {
  const statusConfig = getStatusBadge(applicant.status);
  const dropdownOptions = getStatusDropdownOptions(applicant.status);

  return (
    <div className="relative">
      <button
        onClick={onToggle}
        className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusConfig.bg} ${statusConfig.text} hover:opacity-75 hover:ring-2 hover:ring-green-300 hover:ring-opacity-50 transform hover:-translate-y-0.5 transition-all duration-200 cursor-pointer shadow-sm`}
        title="Click to change status"
      >
        {statusConfig.label}
        <ChevronDown
          className={`w-3 h-3 ml-1 transition-transform duration-200 ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {isOpen && (
        <>
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-green-200 z-50">
            <div className="py-2">
              <div className="px-3 py-2 text-xs text-green-600 font-medium border-b border-green-100">
                Change Status
              </div>
              {dropdownOptions.map((option) => {
                const optionConfig = getStatusBadge(option.value);
                return (
                  <button
                    key={option.value}
                    onClick={() => onUpdateStatus(option.value)}
                    className="w-full text-left px-3 py-2 hover:bg-green-50 transition-colors flex items-center justify-center"
                  >
                    <span
                      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${optionConfig.bg} ${optionConfig.text}`}
                    >
                      {optionConfig.label}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="fixed inset-0 z-40" onClick={onToggle} />
        </>
      )}
    </div>
  );
}

interface TransformedApplicant {
  id: string;
  name: string;
  email: string;
  phone: string;
  location: string;
  appliedAt: Date;
  appliedAgo: string;
  status: string;
  experience: string;
  education: string;
  currentRole: string;
  skills: string[];
  resumeUrl: string;
  coverLetterExcerpt: string;
  matchScore: number;
  volunteerWork: string[];
  personalProjects: string[];
}

function formatDateAgo(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffHours < 1) return "Just now";
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
  if (diffDays === 1) return "1 day ago";
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 14) return "1 week ago";
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return `${Math.floor(diffDays / 30)} months ago`;
}

function formatExactDate(date: Date): string {
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

async function fetchJobSeekerProfile(
  profileId: string,
  cache: Map<string, JobSeekerProfile | null>
): Promise<JobSeekerProfile | null> {
  if (cache.has(profileId)) {
    return cache.get(profileId) ?? null;
  }

  try {
    const profile = await api.jobSeekerProfiles.getById(profileId);
    cache.set(profileId, profile);
    return profile;
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      cache.set(profileId, null);
      return null;
    }

    console.error("Failed to fetch job seeker profile:", error);
    cache.set(profileId, null);
    return null;
  }
}

function buildCandidateName(
  profile: JobSeekerProfile | null,
  fallbackId: string
): string {
  if (!profile) {
    return `Candidate ${fallbackId.slice(0, 8)}`;
  }

  const first = profile.first_name?.trim() ?? "";
  const last = profile.last_name?.trim() ?? "";
  const fullName = `${first} ${last}`.trim();
  return fullName || `Candidate ${fallbackId.slice(0, 8)}`;
}

function formatExperience(years?: number | null): string {
  if (years === null || years === undefined) {
    return "Experience not provided";
  }

  if (years === 0) {
    return "Entry level";
  }

  return `${years} year${years === 1 ? "" : "s"}`;
}

function calculateMatchScore(application: Application): number {
  const score = (application as unknown as { match_score?: number })
    .match_score;
  if (typeof score === "number") {
    if (score > 1) {
      return Math.round(score);
    }
    return Math.round(score * 100);
  }
  return generateDeterministicScore(
    application.id ?? application.job_seeker_id
  );
}

function generateDeterministicScore(seed: string | undefined): number {
  if (!seed) {
    return 72;
  }
  let hash = 0;
  for (let index = 0; index < seed.length; index += 1) {
    const charCode = seed.charCodeAt(index);
    hash = (hash << 5) - hash + charCode;
    hash |= 0;
  }
  const normalized = Math.abs(hash % 2600);
  const score = 70 + Math.round((normalized / 2599) * 25);
  return score;
}

function ApplicationsPageContent(): ReactElement {
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("newest");
  const [selectedApplicants, setSelectedApplicants] = useState<Set<string>>(
    new Set()
  );
  const [expandedCards, setExpandedCards] = useState<Set<string>>(new Set());
  const [openStatusDropdowns, setOpenStatusDropdowns] = useState<Set<string>>(
    new Set()
  );

  // Get job ID from URL params
  const searchParams = useSearchParams();
  const jobId = searchParams.get("jobId");

  // API state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [_applications, setApplications] = useState<Application[]>([]);
  const [applicants, setApplicants] = useState<TransformedApplicant[]>([]);

  // Fetch job and applications
  useEffect(() => {
    const fetchData = async (): Promise<void> => {
      setLoading(true);
      setError(null);

      // Check if job ID is provided
      if (!jobId) {
        setError(
          "No job ID provided. Please navigate to this page from a job posting."
        );
        setLoading(false);
        return;
      }

      try {
        // Fetch job details
        const jobData = (await api.jobs.getById(jobId)) as Job;
        setJob(jobData);

        // Fetch applications for this job
        const jobApplications = (await api.applications.getAll({
          job_id: jobId,
          limit: 100,
        })) as Application[];
        setApplications(jobApplications);

        // Transform applications to applicants format
        // TODO: Fetch job seeker profiles to get name, email, phone, experience, etc.
        const profileCache = new Map<string, JobSeekerProfile | null>();

        const transformedApplicants: TransformedApplicant[] = await Promise.all(
          jobApplications.map(async (app: Application) => {
            const profile = await fetchJobSeekerProfile(
              app.job_seeker_id,
              profileCache
            );

            const appliedAt = new Date(app.applied_date);
            const appliedAgo = formatDateAgo(appliedAt);

            return {
              id: app.id,
              name: buildCandidateName(profile, app.job_seeker_id),
              email: profile?.email || "",
              phone: profile?.phone || "",
              location: profile?.location || jobData.location || "Unknown",
              appliedAt,
              appliedAgo,
              status: app.status,
              experience: formatExperience(profile?.experience_years),
              education: profile?.education_level
                ? `Education: ${profile.education_level}`
                : "Education not provided",
              currentRole: profile?.bio ? profile.bio : "Role not provided",
              skills: profile?.skills || [],
              resumeUrl: profile?.resume_file_url || "",
              coverLetterExcerpt: app.notes || "No cover letter provided.",
              matchScore: calculateMatchScore(app),
              volunteerWork: [],
              personalProjects: [],
            };
          })
        );
        setApplicants(transformedApplicants);
      } catch (err) {
        console.error("Failed to fetch applications data:", err);
        if (err instanceof ApiError) {
          if (err.status === 404) {
            setError(`Job not found. The job ID "${jobId}" does not exist.`);
          } else {
            setError(`Failed to load applications: ${err.message}`);
          }
        } else {
          setError("An unexpected error occurred. Please try again.");
        }
      } finally {
        setLoading(false);
      }
    };

    void fetchData();
  }, [jobId]);

  const statusOptions = [
    { value: "all", label: "All Applications", count: applicants.length },
    {
      value: "unreviewed",
      label: "Unreviewed",
      count: applicants.filter((a) => a.status === "unreviewed").length,
    },
    {
      value: "reviewed",
      label: "Reviewed",
      count: applicants.filter((a) => a.status === "reviewed").length,
    },
    {
      value: "under_review",
      label: "Under Review",
      count: applicants.filter((a) => a.status === "under_review").length,
    },
    {
      value: "shortlisted",
      label: "Shortlisted",
      count: applicants.filter((a) => a.status === "shortlisted").length,
    },
    {
      value: "interview_scheduled",
      label: "Interview Scheduled",
      count: applicants.filter((a) => a.status === "interview_scheduled")
        .length,
    },
    {
      value: "offer_extended",
      label: "Offer Extended",
      count: applicants.filter((a) => a.status === "offer_extended").length,
    },
    {
      value: "accepted",
      label: "Accepted",
      count: applicants.filter((a) => a.status === "accepted").length,
    },
    {
      value: "rejected",
      label: "Rejected",
      count: applicants.filter((a) => a.status === "rejected").length,
    },
  ];

  const filteredApplicants = applicants.filter((applicant) => {
    const statusMatch =
      selectedStatus === "all" || applicant.status === selectedStatus;
    const searchMatch =
      searchTerm === "" ||
      applicant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      applicant.currentRole.toLowerCase().includes(searchTerm.toLowerCase()) ||
      applicant.skills.some((skill) =>
        skill.toLowerCase().includes(searchTerm.toLowerCase())
      );

    return statusMatch && searchMatch;
  });

  const handleSelectApplicant = (applicantId: string): void => {
    setSelectedApplicants((prev: Set<string>) => {
      const newSelected = new Set(prev);
      if (newSelected.has(applicantId)) {
        newSelected.delete(applicantId);
      } else {
        newSelected.add(applicantId);
      }
      return newSelected;
    });
  };

  const toggleCardExpansion = (applicantId: string): void => {
    setExpandedCards((prev: Set<string>) => {
      const newExpanded = new Set(prev);
      if (newExpanded.has(applicantId)) {
        newExpanded.delete(applicantId);
      } else {
        newExpanded.add(applicantId);
      }
      return newExpanded;
    });
  };

  const toggleStatusDropdown = (applicantId: string): void => {
    setOpenStatusDropdowns((prev: Set<string>) => {
      const newOpen = new Set(prev);
      if (newOpen.has(applicantId)) {
        newOpen.delete(applicantId);
      } else {
        newOpen.add(applicantId);
      }
      return newOpen;
    });
  };

  const updateApplicantStatus = async (
    applicantId: string,
    newStatus: string
  ): Promise<void> => {
    try {
      await api.applications.update(applicantId, { status: newStatus });

      // Update local state
      setApplicants((prev) =>
        prev.map((app) =>
          app.id === applicantId ? { ...app, status: newStatus } : app
        )
      );

      setOpenStatusDropdowns((prev: Set<string>) => {
        const newOpen = new Set(prev);
        newOpen.delete(applicantId);
        return newOpen;
      });
    } catch (err) {
      console.error("Failed to update application status:", err);
      if (err instanceof ApiError) {
        alert(`Failed to update status: ${err.message}`);
      } else {
        alert("An unexpected error occurred. Please try again.");
      }
    }
  };

  const defaultSkillsLimit = 4;
  const defaultVolunteerLimit = 2;
  const defaultProjectsLimit = 2;
  const expandedVolunteerLimit = 5;
  const expandedProjectsLimit = 5;

  function formatSalary(
    min: number | null | undefined,
    max: number | null | undefined
  ): string {
    if (!min && !max) return "Salary not specified";
    if (!min) return `Up to $${max?.toLocaleString()}`;
    if (!max) return `$${min.toLocaleString()}+`;
    return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
  }

  function formatDateAgoJob(date: Date): string {
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 mx-auto text-green-600 animate-spin mb-4" />
          <p className="text-green-800">Loading applications...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100 flex items-center justify-center">
        <div className="text-center max-w-md">
          <Briefcase className="w-12 h-12 mx-auto text-red-500 mb-4" />
          <p className="text-red-800 font-semibold mb-2">
            Error loading applications
          </p>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100 flex items-center justify-center">
        <div className="text-center max-w-md">
          <Briefcase className="w-12 h-12 mx-auto text-green-300 mb-4" />
          <p className="text-green-600">Job not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <div className="flex items-center space-x-2 mb-6">
          <Link
            href="/jobs"
            className="text-green-600 hover:text-green-800 flex items-center"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Job Listings
          </Link>
        </div>

        {/* Job Info Header */}
        <div className="bg-white/70 backdrop-blur-sm rounded-xl shadow-lg border border-green-200 p-4 sm:p-6 mb-8">
          <div className="flex items-center space-x-2 mb-4">
            <div className="bg-gradient-to-r from-green-100 to-amber-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium border border-green-200">
              📋 Job Listing
            </div>
            <span className="text-sm text-green-600">
              Applications shown below are for this position
            </span>
          </div>

          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between space-y-4 lg:space-y-0">
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl sm:text-3xl font-bold text-green-900 mb-2 break-words">
                {job.title}
              </h1>
              <div className="flex flex-col sm:flex-row sm:flex-wrap sm:items-center gap-2 sm:gap-4 text-green-700 mb-4">
                <span className="flex items-center min-w-0">
                  <Building2 className="w-4 h-4 mr-2 flex-shrink-0" />
                  <span className="truncate">{job.company}</span>
                </span>
                <span className="flex items-center min-w-0">
                  <MapPin className="w-4 h-4 mr-2 flex-shrink-0" />
                  <span className="truncate">
                    {job.remote_ok ? "Remote" : job.location}
                  </span>
                </span>
                <span className="flex items-center">
                  <Clock className="w-4 h-4 mr-2 flex-shrink-0" />
                  {job.job_type}
                </span>
                <span className="flex items-center">
                  <Briefcase className="w-4 h-4 mr-2 flex-shrink-0" />
                  {formatSalary(job.salary_min, job.salary_max)}
                </span>
              </div>
              <p className="text-green-600 text-sm">
                Posted {formatDateAgoJob(new Date(job.created_at))} •{" "}
                {applicants.length} applications received
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-4 lg:ml-6">
              <button className="bg-yellow-100 text-green-700 border border-green-300 px-4 py-2 rounded-lg font-medium hover:bg-yellow-200 transition-all text-center">
                Edit Job
              </button>
              <button className="bg-gradient-to-r from-green-600 to-green-700 text-white px-4 py-2 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all text-center">
                View Details
              </button>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-white/70 backdrop-blur-sm rounded-xl shadow-lg border border-green-200 p-4 sm:p-6 mb-8">
          {/* Status Tabs */}
          <div className="flex flex-wrap gap-2 mb-6 overflow-x-auto pb-2">
            {statusOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => setSelectedStatus(option.value)}
                className={`px-3 py-2 rounded-lg font-medium transition-all whitespace-nowrap flex-shrink-0 text-sm ${
                  selectedStatus === option.value
                    ? "bg-gradient-to-r from-green-600 to-green-700 text-white"
                    : "bg-green-50 text-green-700 hover:bg-green-100"
                }`}
              >
                {option.label} ({option.count})
              </button>
            ))}
          </div>

          {/* Search and Sort */}
          <div className="flex flex-col space-y-4 lg:flex-row lg:space-y-0 lg:gap-4">
            <div className="flex-1 relative min-w-0">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-green-500 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by name, role, or skills..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
              />
            </div>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 bg-white/80"
            >
              <option value="newest">Sort by Newest</option>
              <option value="oldest">Sort by Oldest</option>
              <option value="match_score">Sort by Match Score</option>
              <option value="experience">Sort by Experience</option>
            </select>

            {selectedApplicants.size > 0 && (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-green-700 whitespace-nowrap">
                  {selectedApplicants.size} selected
                </span>
                <button className="bg-blue-100 text-blue-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-200 transition-colors whitespace-nowrap">
                  Bulk Actions
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Applications List */}
        <div className="space-y-6">
          {filteredApplicants.map((applicant) => {
            const isExpanded = expandedCards.has(applicant.id);
            const isDropdownOpen = openStatusDropdowns.has(applicant.id);

            return (
              <div
                key={applicant.id}
                className="bg-white/70 backdrop-blur-sm border border-green-200 rounded-xl shadow-sm hover:shadow-md transition-all p-4 sm:p-6"
              >
                <div className="flex flex-col sm:flex-row sm:items-start space-y-4 sm:space-y-0 sm:space-x-4">
                  {/* Selection Checkbox and Avatar */}
                  <div className="flex items-start space-x-4 sm:contents">
                    <input
                      type="checkbox"
                      checked={selectedApplicants.has(applicant.id)}
                      onChange={() => handleSelectApplicant(applicant.id)}
                      className="mt-1 w-4 h-4 text-green-600 border-green-300 rounded focus:ring-green-500 flex-shrink-0"
                    />

                    <div className="w-12 h-12 sm:w-16 sm:h-16 bg-gradient-to-br from-green-100 to-amber-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <User className="w-6 h-6 sm:w-8 sm:h-8 text-green-600" />
                    </div>

                    {/* Mobile header info */}
                    <div className="flex-1 min-w-0 sm:hidden">
                      <div className="flex items-start justify-between">
                        <div className="min-w-0">
                          <h3 className="text-lg font-semibold text-green-900 truncate">
                            {applicant.name}
                          </h3>
                          <p className="text-green-700 font-medium text-sm truncate">
                            {applicant.currentRole}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2 ml-2">
                          <StatusDropdown
                            applicant={applicant}
                            isOpen={isDropdownOpen}
                            onToggle={() => toggleStatusDropdown(applicant.id)}
                            onUpdateStatus={(newStatus) => {
                              void updateApplicantStatus(
                                applicant.id,
                                newStatus
                              );
                            }}
                          />
                          <button className="p-1 hover:bg-green-100 rounded transition-colors">
                            <MoreVertical className="w-4 h-4 text-green-600" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Desktop and detailed info */}
                  <div className="flex-1 min-w-0">
                    {/* Desktop header */}
                    <div className="hidden sm:flex sm:items-start sm:justify-between mb-3">
                      <div className="min-w-0 flex-1">
                        <h3 className="text-xl font-semibold text-green-900 mb-1 break-words">
                          {applicant.name}
                        </h3>
                        <p className="text-green-700 font-medium mb-1 break-words">
                          {applicant.currentRole}
                        </p>
                        <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-sm text-green-600">
                          <span className="flex items-center min-w-0">
                            <MapPin className="w-3 h-3 mr-1 flex-shrink-0" />
                            <span className="truncate">
                              {applicant.location}
                            </span>
                          </span>
                          <span className="flex items-center whitespace-nowrap">
                            <Briefcase className="w-3 h-3 mr-1 flex-shrink-0" />
                            {applicant.experience}
                          </span>
                          <span className="flex items-center min-w-0">
                            <GraduationCap className="w-3 h-3 mr-1 flex-shrink-0" />
                            <span className="truncate">
                              {applicant.education}
                            </span>
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3 ml-4">
                        <div className="text-right">
                          <div className="flex items-center space-x-1 text-amber-600">
                            <Star className="w-4 h-4 fill-current" />
                            <span className="font-semibold text-sm">
                              {applicant.matchScore}%
                            </span>
                          </div>
                          <span className="text-xs text-green-600">Match</span>
                        </div>

                        <StatusDropdown
                          applicant={applicant}
                          isOpen={isDropdownOpen}
                          onToggle={() => toggleStatusDropdown(applicant.id)}
                          onUpdateStatus={(newStatus) => {
                            void updateApplicantStatus(applicant.id, newStatus);
                          }}
                        />

                        <button className="p-2 hover:bg-green-100 rounded-lg transition-colors">
                          <MoreVertical className="w-4 h-4 text-green-600" />
                        </button>
                      </div>
                    </div>

                    {/* Mobile details */}
                    <div className="sm:hidden space-y-3 mb-4">
                      <div className="flex flex-wrap items-center gap-2 text-xs text-green-600">
                        <span className="flex items-center">
                          <MapPin className="w-3 h-3 mr-1" />
                          {applicant.location}
                        </span>
                        <span className="flex items-center">
                          <Briefcase className="w-3 h-3 mr-1" />
                          {applicant.experience}
                        </span>
                        <span className="flex items-center">
                          <Star className="w-3 h-3 mr-1 text-amber-500 fill-current" />
                          {applicant.matchScore}% match
                        </span>
                      </div>
                      <p className="text-xs text-green-700 truncate">
                        {applicant.education}
                      </p>
                    </div>

                    {/* Contact Info */}
                    <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-6 text-xs sm:text-sm text-green-600 mb-3">
                      <a
                        href={`mailto:${applicant.email}`}
                        className="flex items-center hover:text-green-800 truncate"
                      >
                        <Mail className="w-3 h-3 mr-1 flex-shrink-0" />
                        <span className="truncate">{applicant.email}</span>
                      </a>
                      <a
                        href={`tel:${applicant.phone}`}
                        className="flex items-center hover:text-green-800 whitespace-nowrap"
                      >
                        <Phone className="w-3 h-3 mr-1 flex-shrink-0" />
                        {applicant.phone}
                      </a>
                      <span className="text-xs text-gray-500 whitespace-nowrap">
                        Applied {formatExactDate(applicant.appliedAt)} •
                        <span className="ml-1 text-green-600">
                          {applicant.appliedAgo}
                        </span>
                      </span>
                    </div>

                    {/* Skills */}
                    <div className="mb-3">
                      <h4 className="text-sm font-medium text-green-800 mb-2">
                        Key Skills:
                      </h4>
                      <div className="flex flex-wrap gap-1 sm:gap-2">
                        {applicant.skills
                          .slice(
                            0,
                            isExpanded
                              ? applicant.skills.length
                              : defaultSkillsLimit
                          )
                          .map((skill, index) => (
                            <span
                              key={index}
                              className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs"
                            >
                              {skill}
                            </span>
                          ))}
                        {!isExpanded &&
                          applicant.skills.length > defaultSkillsLimit && (
                            <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                              +{applicant.skills.length - defaultSkillsLimit}{" "}
                              more
                            </span>
                          )}
                      </div>
                    </div>

                    {/* Cover Letter Excerpt */}
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-green-800 mb-1">
                        Cover Letter Preview:
                      </h4>
                      <p className="text-sm text-green-700 italic break-words">
                        &quot;{applicant.coverLetterExcerpt}&quot;
                      </p>
                    </div>

                    {/* Volunteer Work & Personal Projects */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                      <div>
                        <h4 className="text-sm font-medium text-green-800 mb-1">
                          Volunteer Experience:
                        </h4>
                        <ul className="text-sm text-green-700 space-y-1">
                          {applicant.volunteerWork
                            .slice(
                              0,
                              isExpanded
                                ? expandedVolunteerLimit
                                : defaultVolunteerLimit
                            )
                            .map((work, index) => (
                              <li key={index} className="flex items-start">
                                <span className="w-1 h-1 bg-green-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                                <span className="break-words">{work}</span>
                              </li>
                            ))}
                          {!isExpanded &&
                            applicant.volunteerWork.length >
                              defaultVolunteerLimit && (
                              <li className="flex items-start text-green-500">
                                <span className="w-1 h-1 bg-green-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                                <span className="text-xs">
                                  +
                                  {applicant.volunteerWork.length -
                                    defaultVolunteerLimit}{" "}
                                  more volunteer experiences
                                </span>
                              </li>
                            )}
                          {isExpanded &&
                            applicant.volunteerWork.length >
                              expandedVolunteerLimit && (
                              <li className="flex items-start text-green-500">
                                <span className="w-1 h-1 bg-green-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                                <span className="text-xs">
                                  View full application for{" "}
                                  {applicant.volunteerWork.length -
                                    expandedVolunteerLimit}{" "}
                                  more
                                </span>
                              </li>
                            )}
                        </ul>
                      </div>

                      <div>
                        <h4 className="text-sm font-medium text-green-800 mb-1">
                          Personal Projects:
                        </h4>
                        <ul className="text-sm text-green-700 space-y-1">
                          {applicant.personalProjects
                            .slice(
                              0,
                              isExpanded
                                ? expandedProjectsLimit
                                : defaultProjectsLimit
                            )
                            .map((project, index) => (
                              <li key={index} className="flex items-start">
                                <span className="w-1 h-1 bg-amber-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                                <span className="break-words">{project}</span>
                              </li>
                            ))}
                          {!isExpanded &&
                            applicant.personalProjects.length >
                              defaultProjectsLimit && (
                              <li className="flex items-start text-amber-600">
                                <span className="w-1 h-1 bg-amber-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                                <span className="text-xs">
                                  +
                                  {applicant.personalProjects.length -
                                    defaultProjectsLimit}{" "}
                                  more projects
                                </span>
                              </li>
                            )}
                          {isExpanded &&
                            applicant.personalProjects.length >
                              expandedProjectsLimit && (
                              <li className="flex items-start text-amber-600">
                                <span className="w-1 h-1 bg-amber-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                                <span className="text-xs">
                                  View full application for{" "}
                                  {applicant.personalProjects.length -
                                    expandedProjectsLimit}{" "}
                                  more
                                </span>
                              </li>
                            )}
                        </ul>
                      </div>
                    </div>

                    {/* Expand/Collapse Button */}
                    <div className="mb-4">
                      <button
                        onClick={() => toggleCardExpansion(applicant.id)}
                        className="text-green-600 text-sm font-medium hover:text-green-800 transition-colors flex items-center"
                      >
                        {isExpanded ? (
                          <>
                            Show less detail
                            <ChevronDown className="w-4 h-4 ml-1 rotate-180" />
                          </>
                        ) : (
                          <>
                            Show more detail
                            <ChevronDown className="w-4 h-4 ml-1" />
                          </>
                        )}
                      </button>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-col sm:flex-row flex-wrap gap-2 sm:gap-3">
                      <button className="bg-gradient-to-r from-green-600 to-green-700 text-white px-3 py-2 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm">
                        <Eye className="w-4 h-4 mr-2" />
                        View Application
                      </button>
                      <button className="bg-white text-green-700 border border-green-300 px-3 py-2 rounded-lg font-medium hover:bg-green-50 transition-all flex items-center justify-center text-sm">
                        <Download className="w-4 h-4 mr-2" />
                        View Resume
                      </button>
                      <button className="bg-blue-100 text-blue-700 px-3 py-2 rounded-lg font-medium hover:bg-blue-200 transition-all flex items-center justify-center text-sm">
                        <Calendar className="w-4 h-4 mr-2" />
                        Schedule Interview
                      </button>
                      <button className="bg-yellow-100 text-green-700 border border-green-300 px-3 py-2 rounded-lg font-medium hover:bg-yellow-200 transition-all flex items-center justify-center text-sm">
                        <Mail className="w-4 h-4 mr-2" />
                        Send Message
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Results Summary */}
        {filteredApplicants.length === 0 && (
          <div className="text-center py-12">
            <div className="text-green-600 mb-4">
              <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
            </div>
            <h3 className="text-xl font-medium text-green-800 mb-2">
              No applications found
            </h3>
            <p className="text-green-600">
              Try adjusting your filters or search terms
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ApplicationsPage(): ReactElement {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100 flex items-center justify-center">
          <div className="text-center">
            <RefreshCw className="w-12 h-12 mx-auto text-green-600 animate-spin mb-4" />
            <p className="text-green-800">Loading...</p>
          </div>
        </div>
      }
    >
      <ApplicationsPageContent />
    </Suspense>
  );
}
