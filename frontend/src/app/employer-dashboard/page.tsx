"use client";

import { useState, type ReactElement } from "react";

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

// TODO: Replace with API call to fetch employer info
const employerInfo = {
  name: "Sarah Martinez",
  role: "Senior Recruiter",
  companies: [
    { id: "techflow", name: "TechFlow Solutions", role: "Lead Recruiter" },
    { id: "innovate", name: "InnovateNow Corp", role: "HR Consultant" },
    { id: "datacore", name: "DataCore Industries", role: "Talent Acquisition" },
  ],
};

// TODO: Replace with API call to fetch job postings
const jobPostings = [
  {
    id: 1,
    title: "Marketing Coordinator",
    company: "TechFlow Solutions",
    status: "Active",
    posted: "2 weeks ago",
    applications: 28,
    newApplications: 5,
    interviews: 3,
    hired: 0,
    location: "Phoenix, AZ",
    salary: "$45,000 - $55,000",
  },
  {
    id: 2,
    title: "Senior Developer",
    company: "InnovateNow Corp",
    status: "Active",
    posted: "1 week ago",
    applications: 45,
    newApplications: 12,
    interviews: 8,
    hired: 1,
    location: "Remote",
    salary: "$85,000 - $105,000",
  },
  {
    id: 3,
    title: "Business Analyst",
    company: "DataCore Industries",
    status: "Paused",
    posted: "3 weeks ago",
    applications: 67,
    newApplications: 2,
    interviews: 15,
    hired: 2,
    location: "Scottsdale, AZ",
    salary: "$65,000 - $75,000",
  },
];

// TODO: Replace with API call to fetch recent applications
const recentApplications = [
  {
    id: 1,
    candidateName: "Alex Johnson",
    jobTitle: "Marketing Coordinator",
    company: "TechFlow Solutions",
    appliedDate: "2 hours ago",
    status: "Unreviewed",
    matchScore: 89,
    experience: "3 years",
    location: "Phoenix, AZ",
  },
  {
    id: 2,
    candidateName: "Maria Garcia",
    jobTitle: "Senior Developer",
    company: "InnovateNow Corp",
    appliedDate: "5 hours ago",
    status: "Unreviewed",
    matchScore: 94,
    experience: "7 years",
    location: "Remote",
  },
  {
    id: 3,
    candidateName: "David Chen",
    jobTitle: "Business Analyst",
    company: "DataCore Industries",
    appliedDate: "1 day ago",
    status: "Reviewed",
    matchScore: 76,
    experience: "4 years",
    location: "Tempe, AZ",
  },
];

// TODO: Replace with API call to fetch upcoming interviews
const upcomingInterviews = [
  {
    id: 1,
    candidateName: "Jessica Williams",
    jobTitle: "Marketing Coordinator",
    company: "TechFlow Solutions",
    interviewDate: "Today at 2:00 PM",
    interviewType: "Phone Screen",
    interviewer: "Sarah Martinez",
  },
  {
    id: 2,
    candidateName: "Robert Kumar",
    jobTitle: "Senior Developer",
    company: "InnovateNow Corp",
    interviewDate: "Tomorrow at 10:00 AM",
    interviewType: "Technical Interview",
    interviewer: "Mike Thompson",
  },
];

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

export default function EmployerDashboard(): ReactElement {
  const [selectedCompany, setSelectedCompany] = useState("all");
  const [currentReminder, setCurrentReminder] = useState(healthyReminders[0]);

  const generateReminder = (): void => {
    const randomIndex = Math.floor(Math.random() * healthyReminders.length);
    setCurrentReminder(healthyReminders[randomIndex]);
  };

  // Filter data based on selected company
  const filteredJobPostings =
    selectedCompany === "all"
      ? jobPostings
      : jobPostings.filter((job) => {
          const company = employerInfo.companies.find(
            (c) => c.id === selectedCompany
          );
          return job.company === company?.name;
        });

  const filteredApplications =
    selectedCompany === "all"
      ? recentApplications
      : recentApplications.filter((app) => {
          const company = employerInfo.companies.find(
            (c) => c.id === selectedCompany
          );
          return app.company === company?.name;
        });

  const filteredInterviews =
    selectedCompany === "all"
      ? upcomingInterviews
      : upcomingInterviews.filter((interview) => {
          const company = employerInfo.companies.find(
            (c) => c.id === selectedCompany
          );
          return interview.company === company?.name;
        });

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-green-900 mb-2 flex items-center">
                Good morning, {employerInfo.name}!
                <Building2 className="w-8 h-8 ml-3 text-green-600" />
              </h1>
              <p className="text-green-700">
                Ready to connect great talent with meaningful opportunities?
              </p>
            </div>

            {/* Company Selector */}
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
                {employerInfo.companies.map((company) => (
                  <option key={company.id} value={company.id}>
                    {company.name}
                  </option>
                ))}
              </select>
            </div>
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
              <button className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm">
                <Plus className="w-4 h-4 mr-2" />
                Post New Job
              </button>
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
            <button className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm">
              <Eye className="w-4 h-4 mr-2" />
              Review Applications
            </button>
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

                  <p className="text-xs text-green-600 mt-2">
                    Posted {job.posted}
                  </p>
                </div>
              ))}
            </div>

            {filteredJobPostings.length === 0 && (
              <div className="text-center py-8">
                <Briefcase className="w-12 h-12 mx-auto text-green-300 mb-4" />
                <p className="text-green-600">
                  {selectedCompany === "all"
                    ? "No job postings found across all companies"
                    : `No job postings found for ${
                        employerInfo.companies.find(
                          (c) => c.id === selectedCompany
                        )?.name
                      }`}
                </p>
              </div>
            )}

            <button className="w-full mt-4 bg-gradient-to-r from-green-600 to-green-700 text-white py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center">
              <Plus className="w-5 h-5 mr-2" />
              Create New Job Posting
            </button>
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
                    ? "No recent applications across all companies"
                    : `No recent applications for ${
                        employerInfo.companies.find(
                          (c) => c.id === selectedCompany
                        )?.name
                      }`}
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
                  ? "No upcoming interviews across all companies"
                  : `No upcoming interviews for ${
                      employerInfo.companies.find(
                        (c) => c.id === selectedCompany
                      )?.name
                    }`}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
