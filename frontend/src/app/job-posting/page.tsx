"use client";

import { useState, useEffect, type ReactElement } from "react";
import { useRouter } from "next/navigation";

import {
  Save,
  Eye,
  Plus,
  X,
  DollarSign,
  Sparkles,
  Copy,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Users,
} from "lucide-react";
import { api, ApiError, ValidationError } from "../../lib/api";
import { getCurrentUserId } from "../../lib/auth";
import type { JobCreate, EmployerProfile } from "../../lib/api";

// TODO: Replace with API call to fetch employer info
const employerInfo = {
  name: "Sarah Martinez",
  companies: [
    { id: "techflow", name: "TechFlow Solutions" },
    { id: "innovate", name: "InnovateNow Corp" },
    { id: "datacore", name: "DataCore Industries" },
  ],
};

// Job description templates to help overwhelmed hiring teams
const jobTemplates: Record<
  string,
  {
    title: string;
    department: string;
    description: string;
    requirements: string[];
    responsibilities: string[];
    niceToHave: string[];
  }
> = {
  "marketing-coordinator": {
    title: "Marketing Coordinator",
    department: "Marketing",
    description: `• Start with what makes this role meaningful and exciting
• Describe the team they'll join and company culture
• Explain how this position contributes to larger goals
• Highlight growth and learning opportunities
• Mention any unique benefits or perks of working here
• Keep it authentic and avoid corporate buzzwords`,
    requirements: [
      "2+ years of marketing experience",
      "Experience with social media management",
      "Strong written communication skills",
      "Proficiency with marketing tools (Google Analytics, social platforms)",
    ],
    responsibilities: [
      "Develop and execute social media campaigns that engage our community",
      "Create compelling content across multiple channels",
      "Collaborate with cross-functional teams on integrated campaigns",
      "Analyze campaign performance and provide insights for optimization",
    ],
    niceToHave: [
      "Experience with marketing automation platforms",
      "Basic graphic design skills",
      "Previous experience in our industry",
      "Bilingual capabilities",
    ],
  },
  "software-developer": {
    title: "Software Developer",
    department: "Engineering",
    description: `• Describe the main purpose and impact of this role
• Explain the team structure and collaboration style  
• Highlight technical challenges and learning opportunities
• Mention development culture and growth paths
• Include information about code quality and best practices
• Note any interesting technologies or projects they'll work on`,
    requirements: [
      "3+ years of software development experience",
      "Proficiency in JavaScript, Python, or similar languages",
      "Experience with modern web frameworks",
      "Understanding of database design and optimization",
    ],
    responsibilities: [
      "Design and implement new features that delight our users",
      "Write clean, maintainable code with comprehensive tests",
      "Participate in code reviews and mentor junior developers",
      "Collaborate with product and design teams on user experience",
    ],
    niceToHave: [
      "Experience with cloud platforms (AWS, Azure, GCP)",
      "Mobile development experience",
      "Open source contributions",
      "Experience with agile development methodologies",
    ],
  },
  "customer-success": {
    title: "Customer Success Manager",
    department: "Customer Success",
    description: `• Explain how this role helps customers succeed
• Describe the customer base and typical challenges
• Highlight the collaborative nature with internal teams
• Mention metrics and success measurement approaches
• Include information about customer journey and lifecycle
• Note any tools, systems, or processes they'll use`,
    requirements: [
      "2+ years in customer-facing roles",
      "Excellent communication and problem-solving skills",
      "Experience with CRM systems",
      "Ability to understand and explain technical concepts",
    ],
    responsibilities: [
      "Onboard new customers and ensure successful product adoption",
      "Proactively identify opportunities to help customers succeed",
      "Serve as primary point of contact for assigned customer accounts",
      "Gather customer feedback and work with product team on improvements",
    ],
    niceToHave: [
      "Previous experience in SaaS or technology companies",
      "Project management certification",
      "Experience with data analysis and reporting",
      "Multilingual capabilities for diverse customer base",
    ],
  },
};

interface JobData {
  title: string;
  department: string;
  description: string;
  requirements: string[];
  responsibilities: string[];
  niceToHave: string[];
  location: string;
  workArrangement: string;
  jobType: string;
  experienceLevel: string;
  salaryMin: string;
  salaryMax: string;
  salaryDisclosed: boolean;
  compensationAdditional: string;
  aboutCompany: string;
  applicationDeadline: string;
  industry?: string;
}

export default function JobPostingPage(): ReactElement {
  const router = useRouter();
  const userId = getCurrentUserId();
  const [selectedCompany, setSelectedCompany] = useState("");
  const [jobData, setJobData] = useState<JobData>({
    title: "",
    department: "",
    description: "",
    requirements: [""],
    responsibilities: [""],
    niceToHave: [""],
    location: "",
    workArrangement: "On-site",
    jobType: "Full-time",
    experienceLevel: "Mid Level",
    salaryMin: "",
    salaryMax: "",
    salaryDisclosed: true,
    compensationAdditional: "",
    aboutCompany: "",
    applicationDeadline: "",
  });

  const [currentTemplate, setCurrentTemplate] = useState("");
  const [autoSaveStatus, setAutoSaveStatus] = useState<
    "saving" | "saved" | "error"
  >("saved");
  const [showPreview, setShowPreview] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  // Auto-save functionality (simulated)
  useEffect(() => {
    const autoSave = setTimeout(() => {
      if (jobData.title || jobData.description) {
        setAutoSaveStatus("saving");
        // TODO: Replace with actual API call
        setTimeout(() => {
          setAutoSaveStatus("saved");
        }, 1000);
      }
    }, 2000);

    return () => clearTimeout(autoSave);
  }, [jobData]);

  const handleInputChange = (
    field: keyof JobData,
    value: string | boolean
  ): void => {
    setJobData((prev: JobData) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleArrayField = (
    field: "requirements" | "responsibilities" | "niceToHave",
    index: number,
    value: string
  ): void => {
    setJobData((prev: JobData) => ({
      ...prev,
      [field]: prev[field].map((item, i) => (i === index ? value : item)),
    }));
  };

  const addArrayField = (
    field: "requirements" | "responsibilities" | "niceToHave"
  ): void => {
    setJobData((prev: JobData) => ({
      ...prev,
      [field]: [...prev[field], ""],
    }));
  };

  const removeArrayField = (
    field: "requirements" | "responsibilities" | "niceToHave",
    index: number
  ): void => {
    setJobData((prev: JobData) => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index),
    }));
  };

  const applyTemplate = (templateKey: string): void => {
    const template = jobTemplates[templateKey];
    if (template) {
      setJobData((prev: JobData) => ({
        ...prev,
        ...template,
      }));
      setCurrentTemplate(templateKey);
    }
  };

  // Transform form data to API format
  const transformToApiFormat = (data: JobData): JobCreate => {
    // Combine requirements and niceToHave into a single requirements string
    const allRequirements = [
      ...data.requirements.filter((r) => r.trim()),
      ...data.niceToHave
        .filter((r) => r.trim())
        .map((r) => `Nice to have: ${r}`),
    ].join("\n");

    // Parse salary values with validation
    const parseSalary = (value: string | undefined): number | null => {
      if (!value || !data.salaryDisclosed) return null;
      const cleaned = value.replace(/[^0-9]/g, "");
      if (!cleaned) return null;
      const parsed = parseInt(cleaned, 10);
      return isNaN(parsed) ? null : parsed;
    };

    const salaryMin = parseSalary(data.salaryMin);
    const salaryMax = parseSalary(data.salaryMax);

    // Parse application deadline
    const applicationDeadline = data.applicationDeadline
      ? new Date(data.applicationDeadline)
      : null;

    // Determine remote_ok from workArrangement
    const remote_ok =
      data.workArrangement === "Remote" || data.workArrangement === "Hybrid";

    // Get company name from selected company or typed value
    const companyName =
      employerInfo.companies.find((c) => c.id === selectedCompany)?.name ||
      selectedCompany;

    return {
      title: data.title,
      company: companyName,
      description: data.description,
      requirements: allRequirements || null,
      responsibilities: data.responsibilities.filter((r) => r.trim()),
      location: data.location,
      job_type: data.jobType,
      remote_ok,
      salary_min: salaryMin,
      salary_max: salaryMax,
      experience_required: data.experienceLevel || null,
      education_required: null, // Not in form yet
      industry: data.industry || null,
      company_size: null, // Not in form yet
      benefits: data.compensationAdditional
        ? [data.compensationAdditional]
        : [],
      skills_required: [], // Could extract from requirements later
      application_deadline: applicationDeadline,
    };
  };

  const handlePublishJob = async (): Promise<void> => {
    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);
    setFieldErrors({});

    // Check authentication
    if (!userId) {
      setSubmitError("You must be logged in to post a job.");
      setIsSubmitting(false);
      return;
    }

    // Validate each field individually
    const errors: Record<string, string> = {};

    if (!jobData.title?.trim()) {
      errors.title = "Job title is required";
    }

    if (!jobData.description?.trim()) {
      errors.description = "Job description is required";
    }

    if (!jobData.location?.trim()) {
      errors.location = "Location is required";
    }

    // Company validation - allow either selected company or typed name
    const companyName =
      employerInfo.companies.find((c) => c.id === selectedCompany)?.name ||
      selectedCompany;

    if (!companyName?.trim() || companyName === "Your Company") {
      errors.company = "Please select or enter a company name";
    }

    // If there are validation errors, show them and stop
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      const missingFields = Object.keys(errors).join(", ");
      setSubmitError(`Please fix the following fields: ${missingFields}`);
      setIsSubmitting(false);
      return;
    }

    try {
      // Get MongoDB ObjectId from /api/auth/me (backend converts Supabase UUID to MongoDB ObjectId)
      // The userId from getCurrentUserId() is the Supabase UUID, but backend expects MongoDB ObjectId
      const currentUserInfo = await api.auth.getCurrentUser();
      const mongoUserId = currentUserInfo.id; // This is the MongoDB ObjectId

      // Get or create employer profile
      let employerProfileId: string;
      try {
        // Try to get existing employer profile
        const existingProfile: EmployerProfile =
          (await api.employerProfiles.getByUserId(
            mongoUserId
          )) as EmployerProfile;
        employerProfileId = existingProfile.id;
      } catch (err) {
        // Profile doesn't exist, create one
        if (err instanceof ApiError && err.status === 404) {
          // Get company name from form (same logic as transformToApiFormat)
          const companyName =
            employerInfo.companies.find((c) => c.id === selectedCompany)
              ?.name || selectedCompany;

          if (!companyName || companyName.trim() === "") {
            throw new Error(
              "Company name is required to create employer profile"
            );
          }

          const newProfile: EmployerProfile =
            (await api.employerProfiles.create({
              user_id: mongoUserId,
              company_name: companyName,
            })) as EmployerProfile;
          employerProfileId = newProfile.id;
        } else {
          throw err;
        }
      }

      // Create job with employer profile ID
      const apiData = transformToApiFormat(jobData);
      const createdJob = await api.jobs.create(apiData, employerProfileId);

      console.log("Job created successfully:", createdJob);
      setSubmitSuccess(true);

      // Redirect to jobs page after a short delay
      setTimeout(() => {
        router.push("/jobs");
      }, 1500);
    } catch (err) {
      console.error("Failed to create job:", err);
      if (err instanceof ValidationError) {
        const errorMessages = err.issues.map((issue) => {
          const field = issue.path.join(".");
          return `${field}: ${issue.message}`;
        });
        setSubmitError(`Validation error: ${errorMessages.join(", ")}`);
      } else if (err instanceof ApiError) {
        setSubmitError(`Failed to create job: ${err.message}`);
      } else {
        setSubmitError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveDraft = async (): Promise<void> => {
    // For now, draft saving is the same as publishing
    // In the future, we could add an is_active: false flag
    await handlePublishJob();
  };

  const getAutoSaveIndicator = (): ReactElement | null => {
    switch (autoSaveStatus) {
      case "saving":
        return <RefreshCw className="w-4 h-4 animate-spin text-amber-500" />;
      case "saved":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-green-900 mb-2">
                Create Job Posting
              </h1>
              <p className="text-green-700 mb-3">
                Our templates and smart defaults help you create effective job
                postings quickly, even with a busy schedule.
              </p>
            </div>
            <div className="flex items-center space-x-2 text-sm text-green-600">
              {getAutoSaveIndicator()}
              <span>
                {autoSaveStatus === "saving" && "Saving..."}
                {autoSaveStatus === "saved" && "Draft saved"}
                {autoSaveStatus === "error" && "Save failed"}
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-sm text-green-600">
            <span className="text-red-500">*</span>
            <span>Required fields</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Form */}
          <div className="lg:col-span-2">
            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 shadow-sm p-6 space-y-8">
              {/* Template Selector */}
              <div className="bg-gradient-to-r from-amber-50 to-green-50 border border-amber-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-green-800 mb-3 flex items-center">
                  <Sparkles className="w-5 h-5 mr-2" />
                  Quick Start Templates
                </h3>
                <p className="text-sm text-green-600 mb-4">
                  Save time with pre-written job descriptions you can customize
                </p>
                <div className="flex flex-wrap gap-2">
                  {Object.keys(jobTemplates).map((key) => (
                    <button
                      key={key}
                      onClick={() => applyTemplate(key)}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        currentTemplate === key
                          ? "bg-green-600 text-white"
                          : "bg-white/80 text-green-700 hover:bg-green-100 border border-green-300"
                      }`}
                    >
                      {jobTemplates[key].title}
                    </button>
                  ))}
                  <button className="px-3 py-2 bg-white/80 text-green-700 hover:bg-green-100 border border-green-300 rounded-lg text-sm font-medium transition-all">
                    <Copy className="w-4 h-4 mr-1 inline" />
                    Copy from Previous Job
                  </button>
                </div>
              </div>

              {/* Company & Basic Info */}
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-green-800 mb-2">
                    Posting for Company *
                  </label>
                  <select
                    value={selectedCompany}
                    onChange={(e) => {
                      setSelectedCompany(e.target.value);
                      // Clear error when user selects
                      if (fieldErrors.company) {
                        setFieldErrors((prev) => {
                          const newErrors = { ...prev };
                          delete newErrors.company;
                          return newErrors;
                        });
                      }
                    }}
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:border-transparent bg-white/80 ${
                      fieldErrors.company
                        ? "border-red-400 focus:ring-red-400"
                        : "border-green-300 focus:ring-green-400"
                    }`}
                  >
                    <option value="">Select a company...</option>
                    {employerInfo.companies.map((company) => (
                      <option key={company.id} value={company.id}>
                        {company.name}
                      </option>
                    ))}
                  </select>
                  {fieldErrors.company && (
                    <p className="mt-1 text-sm text-red-600">
                      {fieldErrors.company}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-green-800 mb-2">
                    Industry *
                  </label>
                  <select
                    value={jobData.industry || ""}
                    onChange={(e) =>
                      handleInputChange("industry", e.target.value)
                    }
                    className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                  >
                    <option value="">Select industry...</option>
                    <option value="Technology">Technology</option>
                    <option value="Healthcare">Healthcare</option>
                    <option value="Finance">Finance</option>
                    <option value="Marketing & Advertising">
                      Marketing & Advertising
                    </option>
                    <option value="Education">Education</option>
                    <option value="Manufacturing">Manufacturing</option>
                    <option value="Retail">Retail</option>
                    <option value="Construction">Construction</option>
                    <option value="Hospitality">Hospitality</option>
                    <option value="Non-profit">Non-profit</option>
                    <option value="Government">Government</option>
                    <option value="Consulting">Consulting</option>
                    <option value="Real Estate">Real Estate</option>
                    <option value="Transportation">Transportation</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-green-800 mb-2">
                      Job Title *
                    </label>
                    <input
                      type="text"
                      value={jobData.title}
                      onChange={(e) => {
                        handleInputChange("title", e.target.value);
                        // Clear error when user types
                        if (fieldErrors.title) {
                          setFieldErrors((prev) => {
                            const newErrors = { ...prev };
                            delete newErrors.title;
                            return newErrors;
                          });
                        }
                      }}
                      className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:border-transparent bg-white/80 ${
                        fieldErrors.title
                          ? "border-red-400 focus:ring-red-400"
                          : "border-green-300 focus:ring-green-400"
                      }`}
                      placeholder="e.g. Senior Marketing Coordinator"
                    />
                    {fieldErrors.title && (
                      <p className="mt-1 text-sm text-red-600">
                        {fieldErrors.title}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-green-800 mb-2">
                      Department
                    </label>
                    <input
                      type="text"
                      value={jobData.department}
                      onChange={(e) =>
                        handleInputChange("department", e.target.value)
                      }
                      className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                      placeholder="e.g. Marketing, Engineering"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-green-800 mb-2">
                      Job Type
                    </label>
                    <select
                      value={jobData.jobType}
                      onChange={(e) =>
                        handleInputChange("jobType", e.target.value)
                      }
                      className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                    >
                      <option value="Full-time">Full-time</option>
                      <option value="Part-time">Part-time</option>
                      <option value="Contract">Contract</option>
                      <option value="Internship">Internship</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-green-800 mb-2">
                      Experience Level
                    </label>
                    <select
                      value={jobData.experienceLevel}
                      onChange={(e) =>
                        handleInputChange("experienceLevel", e.target.value)
                      }
                      className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                    >
                      <option value="Entry Level">Entry Level</option>
                      <option value="Mid Level">Mid Level</option>
                      <option value="Senior Level">Senior Level</option>
                      <option value="Executive">Executive</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-green-800 mb-2">
                      Work Arrangement
                    </label>
                    <select
                      value={jobData.workArrangement}
                      onChange={(e) =>
                        handleInputChange("workArrangement", e.target.value)
                      }
                      className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                    >
                      <option value="On-site">On-site</option>
                      <option value="Remote">Remote</option>
                      <option value="Hybrid">Hybrid</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-green-800 mb-2">
                    Location *
                  </label>
                  <input
                    type="text"
                    value={jobData.location}
                    onChange={(e) => {
                      handleInputChange("location", e.target.value);
                      // Clear error when user types
                      if (fieldErrors.location) {
                        setFieldErrors((prev) => {
                          const newErrors = { ...prev };
                          delete newErrors.location;
                          return newErrors;
                        });
                      }
                    }}
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:border-transparent bg-white/80 ${
                      fieldErrors.location
                        ? "border-red-400 focus:ring-red-400"
                        : "border-green-300 focus:ring-green-400"
                    }`}
                    placeholder="e.g. Phoenix, AZ or Remote"
                  />
                  {fieldErrors.location && (
                    <p className="mt-1 text-sm text-red-600">
                      {fieldErrors.location}
                    </p>
                  )}
                </div>
              </div>

              {/* Job Description */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Job Description *
                </label>
                <p className="text-xs text-green-600 mb-3">
                  A clear description helps you attract the right candidates and
                  reduces screening time
                </p>
                <textarea
                  value={jobData.description}
                  onChange={(e) => {
                    handleInputChange("description", e.target.value);
                    // Clear error when user types
                    if (fieldErrors.description) {
                      setFieldErrors((prev) => {
                        const newErrors = { ...prev };
                        delete newErrors.description;
                        return newErrors;
                      });
                    }
                  }}
                  rows={8}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:border-transparent bg-white/80 resize-none ${
                    fieldErrors.description
                      ? "border-red-400 focus:ring-red-400"
                      : "border-green-300 focus:ring-green-400"
                  }`}
                  placeholder="Describe the role, the team, and what makes this opportunity special. Focus on growth, impact, and culture fit rather than just tasks..."
                />
                {fieldErrors.description && (
                  <p className="mt-1 text-sm text-red-600">
                    {fieldErrors.description}
                  </p>
                )}
              </div>

              {/* Requirements */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Requirements *
                </label>
                <p className="text-xs text-green-600 mb-3">
                  Focus on must-haves to get qualified applicants and streamline
                  your review process
                </p>
                <div className="space-y-3">
                  {jobData.requirements.map((requirement, index) => (
                    <div key={index} className="flex gap-2">
                      <input
                        type="text"
                        value={requirement}
                        onChange={(e) =>
                          handleArrayField(
                            "requirements",
                            index,
                            e.target.value
                          )
                        }
                        className="flex-1 px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                        placeholder="e.g. 2+ years of marketing experience"
                      />
                      {jobData.requirements.length > 1 && (
                        <button
                          onClick={() =>
                            removeArrayField("requirements", index)
                          }
                          className="px-3 py-3 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    onClick={() => addArrayField("requirements")}
                    className="flex items-center px-4 py-2 text-green-600 hover:text-green-800 hover:bg-green-50 rounded-lg transition-colors text-sm"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Requirement
                  </button>
                </div>
              </div>

              {/* Responsibilities */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Key Responsibilities
                </label>
                <p className="text-xs text-green-600 mb-3">
                  Key day-to-day tasks help candidates understand the role
                  quickly
                </p>
                <div className="space-y-3">
                  {jobData.responsibilities.map((responsibility, index) => (
                    <div key={index} className="flex gap-2">
                      <input
                        type="text"
                        value={responsibility}
                        onChange={(e) =>
                          handleArrayField(
                            "responsibilities",
                            index,
                            e.target.value
                          )
                        }
                        className="flex-1 px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                        placeholder="e.g. Develop and execute social media campaigns"
                      />
                      {jobData.responsibilities.length > 1 && (
                        <button
                          onClick={() =>
                            removeArrayField("responsibilities", index)
                          }
                          className="px-3 py-3 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    onClick={() => addArrayField("responsibilities")}
                    className="flex items-center px-4 py-2 text-green-600 hover:text-green-800 hover:bg-green-50 rounded-lg transition-colors text-sm"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Responsibility
                  </button>
                </div>
              </div>

              {/* Nice to Have */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Nice to Have
                </label>
                <p className="text-xs text-green-600 mb-3">
                  Bonus skills that would be great but aren&apos;t deal-breakers
                </p>
                <div className="space-y-3">
                  {jobData.niceToHave.map((item, index) => (
                    <div key={index} className="flex gap-2">
                      <input
                        type="text"
                        value={item}
                        onChange={(e) =>
                          handleArrayField("niceToHave", index, e.target.value)
                        }
                        className="flex-1 px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                        placeholder="e.g. Experience with marketing automation"
                      />
                      {jobData.niceToHave.length > 1 && (
                        <button
                          onClick={() => removeArrayField("niceToHave", index)}
                          className="px-3 py-3 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    onClick={() => addArrayField("niceToHave")}
                    className="flex items-center px-4 py-2 text-green-600 hover:text-green-800 hover:bg-green-50 rounded-lg transition-colors text-sm"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Nice to Have
                  </button>
                </div>
              </div>

              {/* Compensation */}
              <div className="space-y-4">
                <div>
                  <label className="flex items-center space-x-2 mb-4">
                    <input
                      type="checkbox"
                      checked={jobData.salaryDisclosed}
                      onChange={(e) =>
                        handleInputChange("salaryDisclosed", e.target.checked)
                      }
                      className="w-4 h-4 text-green-600 border-green-300 rounded focus:ring-green-500"
                    />
                    <span className="text-sm font-medium text-green-800">
                      Include salary range (recommended - attracts more
                      qualified candidates)
                    </span>
                  </label>

                  {jobData.salaryDisclosed && (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-medium text-green-700 mb-2">
                          Minimum Salary
                        </label>
                        <div className="relative">
                          <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-green-500 w-4 h-4" />
                          <input
                            type="number"
                            value={jobData.salaryMin}
                            onChange={(e) =>
                              handleInputChange("salaryMin", e.target.value)
                            }
                            className="w-full pl-10 pr-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                            placeholder="45000"
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-green-700 mb-2">
                          Maximum Salary
                        </label>
                        <div className="relative">
                          <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-green-500 w-4 h-4" />
                          <input
                            type="number"
                            value={jobData.salaryMax}
                            onChange={(e) =>
                              handleInputChange("salaryMax", e.target.value)
                            }
                            className="w-full pl-10 pr-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                            placeholder="65000"
                          />
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-green-800 mb-2">
                    Additional Compensation & Benefits
                  </label>
                  <textarea
                    value={jobData.compensationAdditional}
                    onChange={(e) =>
                      handleInputChange(
                        "compensationAdditional",
                        e.target.value
                      )
                    }
                    rows={3}
                    className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 resize-none"
                    placeholder="e.g. Health insurance, 401k matching, flexible PTO, professional development budget..."
                  />
                </div>
              </div>

              {/* About the Company */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  About the Company (Optional)
                </label>
                <p className="text-xs text-green-600 mb-3">
                  Share what makes your company special - culture, mission,
                  values, or recent achievements
                </p>
                <textarea
                  value={jobData.aboutCompany}
                  onChange={(e) =>
                    handleInputChange("aboutCompany", e.target.value)
                  }
                  rows={4}
                  className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 resize-none"
                  placeholder="Tell candidates about your company culture, mission, recent growth, awards, or what makes working here special..."
                />
              </div>

              {/* Job Listing Expiration Date */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Job Listing Expiration Date (Optional)
                </label>
                <p className="text-xs text-green-600 mb-3">
                  When should this job posting automatically close? Leave blank
                  to keep it active indefinitely
                </p>
                <input
                  type="date"
                  value={jobData.applicationDeadline}
                  onChange={(e) =>
                    handleInputChange("applicationDeadline", e.target.value)
                  }
                  className="px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                />
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Actions */}
            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 shadow-sm p-6">
              <h3 className="text-lg font-semibold text-green-800 mb-4">
                Actions
              </h3>

              {/* Error Message */}
              {submitError && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-800">{submitError}</p>
                </div>
              )}

              {/* Success Message */}
              {submitSuccess && (
                <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm text-green-800 flex items-center">
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Job posted successfully! Redirecting...
                  </p>
                </div>
              )}

              <div className="space-y-3">
                <button
                  onClick={() => setShowPreview(!showPreview)}
                  disabled={isSubmitting}
                  className="w-full bg-green-50 text-green-700 border border-green-300 py-3 px-4 rounded-lg font-medium hover:bg-green-100 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  Preview Job Posting
                </button>

                <button
                  onClick={() => {
                    void handleSaveDraft();
                  }}
                  disabled={isSubmitting}
                  className="w-full bg-amber-50 text-amber-700 border border-amber-300 py-3 px-4 rounded-lg font-medium hover:bg-amber-100 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      Save as Draft
                    </>
                  )}
                </button>

                <button
                  onClick={() => {
                    void handlePublishJob();
                  }}
                  disabled={isSubmitting}
                  className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-3 px-4 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Publishing...
                    </>
                  ) : (
                    <>
                      <Users className="w-4 h-4 mr-2" />
                      Publish Job
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Progress Indicator */}
            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 shadow-sm p-6">
              <h3 className="text-lg font-semibold text-green-800 mb-4">
                Completion Status
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span>Company Selected</span>
                  <span
                    className={
                      selectedCompany ? "text-green-600" : "text-gray-400"
                    }
                  >
                    {selectedCompany ? "✓" : "○"}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Job Title</span>
                  <span
                    className={
                      jobData.title ? "text-green-600" : "text-gray-400"
                    }
                  >
                    {jobData.title ? "✓" : "○"}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Description</span>
                  <span
                    className={
                      jobData.description.length > 50
                        ? "text-green-600"
                        : "text-gray-400"
                    }
                  >
                    {jobData.description.length > 50 ? "✓" : "○"}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Requirements</span>
                  <span
                    className={
                      jobData.requirements.filter((r) => r.trim()).length > 0
                        ? "text-green-600"
                        : "text-gray-400"
                    }
                  >
                    {jobData.requirements.filter((r) => r.trim()).length > 0
                      ? "✓"
                      : "○"}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Location</span>
                  <span
                    className={
                      jobData.location ? "text-green-600" : "text-gray-400"
                    }
                  >
                    {jobData.location ? "✓" : "○"}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
