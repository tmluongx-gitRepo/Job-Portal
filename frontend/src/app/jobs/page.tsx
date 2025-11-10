"use client";

import { useState } from "react";

import {
  Search,
  MapPin,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import JobListing from "../../components/JobListing";

// Sample job data - will be replaced with API call later
const sampleJobs = [
  {
    id: 1,
    title: "Marketing Coordinator",
    company: "TechFlow Solutions",
    location: "Phoenix, AZ",
    type: "Full-time",
    salary: "$45,000 - $55,000",
    posted: "2 days ago",
    description:
      "Join our dynamic marketing team to create engaging campaigns and build meaningful connections with our community.",
    requirements: [
      "2+ years marketing experience",
      "Social media management",
      "Content creation",
    ],
    benefits: ["Health insurance", "Flexible schedule", "401k matching"],
    values: ["Innovation", "Work-Life Balance", "Community Impact"],
    cultureFit: [
      "Collaborative team environment",
      "Creative problem-solving encouraged",
      "Casual dress code",
    ],
  },
  {
    id: 2,
    title: "Business Analyst",
    company: "DataCore Industries",
    location: "Scottsdale, AZ",
    type: "Full-time",
    salary: null,
    posted: "1 week ago",
    description:
      "Analyze business processes and collaborate with teams to drive data-informed decision making.",
    requirements: [
      "Bachelor's degree preferred",
      "Excel proficiency",
      "Problem-solving skills",
    ],
    benefits: [
      "Remote work options",
      "Professional development",
      "Team outings",
    ],
    values: null,
    cultureFit: [
      "Data-driven decision making",
      "Cross-functional collaboration",
      "Continuous learning mindset",
    ],
  },
  {
    id: 3,
    title: "Customer Success Associate",
    company: "Summit Financial",
    location: "Remote",
    type: "Full-time",
    salary: "$42,000 - $50,000",
    posted: "3 days ago",
    description:
      "Help our clients achieve their financial goals while building lasting relationships.",
    requirements: [
      "Strong communication skills",
      "Customer service experience",
      "Detail-oriented",
    ],
    benefits: [
      "Health & dental",
      "Home office stipend",
      "Growth opportunities",
    ],
    values: ["Client-First Approach", "Integrity", "Professional Growth"],
    cultureFit: [
      "Relationship-focused environment",
      "Empathy and patience valued",
      "Results-oriented team",
    ],
  },
  {
    id: 4,
    title: "Project Manager",
    company: "InnovateNow Corp",
    location: "Tempe, AZ",
    type: "Full-time",
    salary: "$65,000 - $75,000",
    posted: "5 days ago",
    description:
      "Lead cross-functional teams to deliver impactful projects that drive business growth.",
    requirements: [
      "3+ years project management",
      "Agile methodology",
      "Leadership experience",
    ],
    benefits: ["Comprehensive benefits", "Flexible PTO", "Learning budget"],
    values: ["Innovation", "Transparency", "Continuous Improvement"],
    cultureFit: null,
  },
  {
    id: 5,
    title: "Administrative Assistant",
    company: "Metro Healthcare Group",
    location: "Phoenix, AZ",
    type: "Part-time",
    salary: "$16 - $19 per hour",
    posted: "1 day ago",
    description:
      "Support our healthcare team with administrative tasks in a caring, patient-focused environment.",
    requirements: [
      "High school diploma",
      "Microsoft Office",
      "Healthcare experience preferred",
    ],
    benefits: ["Healthcare discount", "Flexible hours", "Supportive team"],
    values: ["Patient Care", "Compassion", "Teamwork"],
    cultureFit: [
      "Caring and supportive atmosphere",
      "Patient-first mentality",
      "Collaborative healthcare team",
    ],
  },
  {
    id: 6,
    title: "Sales Representative",
    company: "BlueTech Systems",
    location: "Mesa, AZ",
    type: "Full-time",
    salary: null,
    posted: "4 days ago",
    description:
      "Build relationships with clients and help them find technology solutions that fit their needs.",
    requirements: [
      "Sales experience helpful",
      "Relationship building",
      "Tech interest",
    ],
    benefits: [
      "Commission structure",
      "Training program",
      "Career advancement",
    ],
    values: null,
    cultureFit: null,
  },
  {
    id: 7,
    title: "UX Designer",
    company: "Creative Solutions Co.",
    location: "Phoenix, AZ",
    type: "Full-time",
    salary: "$55,000 - $70,000",
    posted: "1 week ago",
    description:
      "Design user-centered experiences that delight customers and drive business results.",
    requirements: [
      "2+ years UX design",
      "Figma proficiency",
      "User research experience",
    ],
    benefits: [
      "Health insurance",
      "Creative freedom",
      "Design conference budget",
    ],
    values: ["User-Centered Design", "Innovation", "Collaboration"],
    cultureFit: [
      "Design thinking culture",
      "Feedback-driven environment",
      "Work-life balance focus",
    ],
    hasApplied: true,
    appliedDate: "2024-10-28",
  },
];

export default function JobsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [location, setLocation] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [savedJobs, setSavedJobs] = useState<Set<number>>(new Set());
  const [saveMessages, setSaveMessages] = useState<Record<number, string>>({});
  const [expandedJobs, setExpandedJobs] = useState<Set<number>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const jobsPerPage = 10;

  // TODO: Replace with API call
  const jobs = sampleJobs;

  const handleSaveJob = (jobId: number): void => {
    setSavedJobs((prev: any) => {
      const newSaved = new Set(prev);
      if (newSaved.has(jobId)) {
        newSaved.delete(jobId);
        setSaveMessages((prev: any) => ({
          ...prev,
          [jobId]: "Job removed from saved",
        }));
      } else {
        newSaved.add(jobId);
        setSaveMessages((prev: any) => ({ ...prev, [jobId]: "Job saved!" }));
      }

      // Clear message after 2 seconds
      setTimeout(() => {
        setSaveMessages((prev: any) => {
          const newMessages = { ...prev };
          delete newMessages[jobId];
          return newMessages;
        });
      }, 2000);

      return newSaved;
    });
  };

  const toggleJobExpansion = (jobId: number): void => {
    setExpandedJobs((prev: any) => {
      const newExpanded = new Set(prev);
      if (newExpanded.has(jobId)) {
        newExpanded.delete(jobId);
      } else {
        newExpanded.add(jobId);
      }
      return newExpanded;
    });
  };

  // Pagination logic
  const totalJobs = jobs.length;
  const totalPages = Math.ceil(totalJobs / jobsPerPage);
  const startIndex = (currentPage - 1) * jobsPerPage;
  const endIndex = startIndex + jobsPerPage;
  const currentJobs = jobs.slice(startIndex, endIndex);

  const goToPage = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const goToPreviousPage = (): void => {
    if (currentPage > 1) {
      goToPage(currentPage - 1);
    }
  };

  const goToNextPage = (): void => {
    if (currentPage < totalPages) {
      goToPage(currentPage + 1);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement search functionality
    console.log("Search:", { searchTerm, location });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-green-900 mb-2">
            Find Your Perfect Match
          </h1>
          <p className="text-green-700">
            Discover opportunities that align with your values and goals
          </p>
        </div>

        {/* Search Interface */}
        <div className="bg-white/70 backdrop-blur-sm rounded-xl shadow-lg border border-green-200 p-6 mb-8">
          <form
            onSubmit={handleSearch}
            className="flex flex-col lg:flex-row gap-4"
          >
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-green-500 w-5 h-5" />
              <input
                type="text"
                placeholder="Job title, company, or keywords..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent text-lg bg-white/80"
              />
            </div>

            <div className="flex-1 relative">
              <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 text-green-500 w-5 h-5" />
              <input
                type="text"
                placeholder="City, State or Remote"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent text-lg bg-white/80"
              />
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className="bg-yellow-100 text-green-700 border border-green-300 px-6 py-3 rounded-lg font-semibold hover:bg-yellow-200 transition-all flex items-center"
              >
                <SlidersHorizontal className="w-5 h-5 mr-2" />
                Filters
              </button>

              <button
                type="submit"
                className="bg-gradient-to-r from-green-600 to-green-700 text-white px-8 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all flex items-center"
              >
                <Search className="w-5 h-5 mr-2" />
                Search Jobs
              </button>
            </div>
          </form>

          {/* Filters Panel */}
          {showFilters && (
            <div className="mt-6 pt-6 border-t border-green-200 relative z-10">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="relative">
                  <label className="block text-sm font-medium text-green-800 mb-2">
                    Job Type
                  </label>
                  <select className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white shadow-md relative z-20">
                    <option>All Types</option>
                    <option>Full-time</option>
                    <option>Part-time</option>
                    <option>Contract</option>
                    <option>Remote</option>
                  </select>
                </div>

                <div className="relative">
                  <label className="block text-sm font-medium text-green-800 mb-2">
                    Salary Range
                  </label>
                  <select className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white shadow-md relative z-20">
                    <option>Any Salary</option>
                    <option>$30k - $45k</option>
                    <option>$45k - $60k</option>
                    <option>$60k - $80k</option>
                    <option>$80k+</option>
                  </select>
                </div>

                <div className="relative">
                  <label className="block text-sm font-medium text-green-800 mb-2">
                    Company Values
                  </label>
                  <select className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white shadow-md relative z-20">
                    <option>Any Values</option>
                    <option>Work-Life Balance</option>
                    <option>Diversity & Inclusion</option>
                    <option>Environmental Responsibility</option>
                    <option>Innovation & Growth</option>
                    <option>Community Impact</option>
                  </select>
                </div>

                <div className="relative">
                  <label className="block text-sm font-medium text-green-800 mb-2">
                    Posted Date
                  </label>
                  <select className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white shadow-md relative z-20">
                    <option>Any Time</option>
                    <option>Last 24 hours</option>
                    <option>Last 3 days</option>
                    <option>Last week</option>
                    <option>Last month</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-green-700">
              <span className="font-semibold">{totalJobs} opportunities</span>{" "}
              found
            </p>
            <p className="text-sm text-green-600">
              Rejections don&apos;t automatically mean you&apos;re a bad candidate. You
              have value.
            </p>
            {totalJobs > 0 && (
              <p className="text-sm text-green-600 mt-1">
                Showing {startIndex + 1}-{Math.min(endIndex, totalJobs)} of{" "}
                {totalJobs} results
              </p>
            )}
          </div>

          <select className="px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 bg-white/80 shadow-lg border-b-2 border-b-green-300">
            <option>Sort by Relevance</option>
            <option>Sort by Date Posted</option>
            <option>Salary (High - Low)</option>
            <option>Salary (Low - High)</option>
          </select>
        </div>

        {/* Job Listings */}
        <div className="space-y-6">
          {currentJobs.length > 0 ? (
            currentJobs.map((job) => (
              <JobListing
                key={job.id}
                job={job}
                isSaved={savedJobs.has(job.id)}
                isExpanded={expandedJobs.has(job.id)}
                saveMessage={saveMessages[job.id]}
                onSave={() => handleSaveJob(job.id)}
                onToggleExpand={() => toggleJobExpansion(job.id)}
              />
            ))
          ) : (
            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-12 text-center">
              <p className="text-green-700 text-lg mb-2">No jobs found</p>
              <p className="text-green-600 text-sm">
                Try adjusting your search criteria or filters
              </p>
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-8 bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
            <div className="flex items-center space-x-4">
              <p className="text-sm text-green-700">
                Page {currentPage} of {totalPages}
              </p>
              <div className="hidden sm:block text-sm text-green-600">
                ({totalJobs} total opportunities)
              </div>
            </div>

            <div className="flex items-center space-x-2">
              {/* Previous Button */}
              <button
                onClick={goToPreviousPage}
                disabled={currentPage === 1}
                className={`flex items-center px-3 py-2 rounded-lg font-medium transition-all ${
                  currentPage === 1
                    ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                    : "bg-yellow-100 text-green-700 border border-green-300 hover:bg-yellow-200"
                }`}
              >
                <ChevronLeft className="w-4 h-4 mr-1" />
                Previous
              </button>

              {/* Page Numbers */}
              <div className="flex items-center space-x-1">
                {/* First page */}
                {currentPage > 3 && (
                  <>
                    <button
                      onClick={() => goToPage(1)}
                      className="px-3 py-2 rounded-lg font-medium text-green-700 hover:bg-green-100 transition-colors"
                    >
                      1
                    </button>
                    {currentPage > 4 && (
                      <span className="text-green-500">...</span>
                    )}
                  </>
                )}

                {/* Pages around current page */}
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNumber;
                  if (totalPages <= 5) {
                    pageNumber = i + 1;
                  } else if (currentPage <= 3) {
                    pageNumber = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    pageNumber = totalPages - 4 + i;
                  } else {
                    pageNumber = currentPage - 2 + i;
                  }

                  if (pageNumber < 1 || pageNumber > totalPages) return null;

                  return (
                    <button
                      key={pageNumber}
                      onClick={() => goToPage(pageNumber)}
                      className={`px-3 py-2 rounded-lg font-medium transition-all ${
                        pageNumber === currentPage
                          ? "bg-gradient-to-r from-green-600 to-green-700 text-white"
                          : "text-green-700 hover:bg-green-100"
                      }`}
                    >
                      {pageNumber}
                    </button>
                  );
                })}

                {/* Last page */}
                {currentPage < totalPages - 2 && totalPages > 5 && (
                  <>
                    {currentPage < totalPages - 3 && (
                      <span className="text-green-500">...</span>
                    )}
                    <button
                      onClick={() => goToPage(totalPages)}
                      className="px-3 py-2 rounded-lg font-medium text-green-700 hover:bg-green-100 transition-colors"
                    >
                      {totalPages}
                    </button>
                  </>
                )}
              </div>

              {/* Next Button */}
              <button
                onClick={goToNextPage}
                disabled={currentPage === totalPages}
                className={`flex items-center px-3 py-2 rounded-lg font-medium transition-all ${
                  currentPage === totalPages
                    ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                    : "bg-gradient-to-r from-green-600 to-green-700 text-white hover:from-green-700 hover:to-green-800"
                }`}
              >
                Next
                <ChevronRight className="w-4 h-4 ml-1" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
