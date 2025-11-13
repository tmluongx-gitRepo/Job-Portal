"use client";

import React, { useState, useEffect, type ReactElement } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle,
  User,
  FileText,
  MessageSquare,
  Scale,
  Eye,
  Upload,
  MapPin,
  Phone,
  Mail,
  Briefcase,
  Star,
  AlertCircle,
  Heart,
  RefreshCw,
} from "lucide-react";
import { api, ApiError } from "../../../lib/api";
import type {
  Job,
  JobSeekerProfile,
  ApplicationCreate,
} from "../../../lib/api";

// ⚠️ TODO: Replace with actual user ID from auth context when authentication is implemented
const userId = "507f1f77bcf86cd799439011"; // PLACEHOLDER

interface ApplicationFormData {
  // Page 1: Basic Profile Information
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  location: string;
  zipCode: string;

  // Page 2: Resume & Experience
  resumeFile: File | null;
  resumeFilename: string;
  experiences: Array<{
    id: number;
    company: string;
    role: string;
    duration: string;
    description: string;
  }>;
  noExperience: boolean;
  keySkills: string[];

  // Page 3: Job-Specific Questions
  screeningResponses: Record<string, string>;
  coverLetter: string;

  // Page 4: Equal Opportunity
  raceEthnicity: string;
  veteranStatus: string;
  disabilityStatus: string;

  // Page 5: Review flags
  agreedToTerms: boolean;
  allowContactFromEmployer: boolean;
}

interface ApplicationSettings {
  applicationMethod: "Internal" | "External" | "Email";
  externalUrl: string;
  applicationEmail: string;
  requireCoverLetter: boolean;
  screeningQuestions: string[];
  equalOpportunityEnabled: boolean;
}

export default function JobApplicationPage(): ReactElement | null {
  const params = useParams();
  const router = useRouter();
  const jobId = params?.jobId as string;

  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = 5;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [profile, setProfile] = useState<JobSeekerProfile | null>(null);
  const [jobSeekerProfileId, setJobSeekerProfileId] = useState<string | null>(
    null
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [applicationSettings, setApplicationSettings] =
    useState<ApplicationSettings | null>(null);

  const [applicationData, setApplicationData] = useState<ApplicationFormData>({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    location: "",
    zipCode: "",
    resumeFile: null,
    resumeFilename: "",
    experiences: [
      {
        id: 1,
        company: "",
        role: "",
        duration: "",
        description: "",
      },
    ],
    noExperience: false,
    keySkills: [],
    screeningResponses: {},
    coverLetter: "",
    raceEthnicity: "Prefer not to answer",
    veteranStatus: "Prefer not to answer",
    disabilityStatus: "Prefer not to answer",
    agreedToTerms: false,
    allowContactFromEmployer: true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");

  // Fetch job and profile data
  useEffect(() => {
    const fetchData = async (): Promise<void> => {
      if (!jobId) {
        setError("No job ID provided");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        // Fetch job details
        const jobData = (await api.jobs.getById(jobId)) as Job;
        setJob(jobData);

        // Load application settings from localStorage (set by job-application-setup)
        // TODO: When backend supports application settings, fetch from API instead
        const settingsKey = `job_application_settings_${jobId}`;
        const savedSettings = localStorage.getItem(settingsKey);
        if (savedSettings) {
          try {
            const parsed = JSON.parse(savedSettings) as ApplicationSettings & {
              jobId: string;
            };
            setApplicationSettings({
              applicationMethod: parsed.applicationMethod || "Internal",
              externalUrl: parsed.externalUrl || "",
              applicationEmail: parsed.applicationEmail || "",
              requireCoverLetter: parsed.requireCoverLetter ?? true,
              screeningQuestions: parsed.screeningQuestions || [],
              equalOpportunityEnabled: parsed.equalOpportunityEnabled ?? true,
            });
          } catch (parseErr) {
            console.warn("Failed to parse application settings:", parseErr);
          }
        } else {
          // Default settings if none configured
          setApplicationSettings({
            applicationMethod: "Internal",
            externalUrl: "",
            applicationEmail: "",
            requireCoverLetter: true,
            screeningQuestions: [],
            equalOpportunityEnabled: true,
          });
        }

        // Try to fetch user's job seeker profile
        try {
          const userProfile = (await api.jobSeekerProfiles.getByUserId(
            userId
          )) as JobSeekerProfile;
          setProfile(userProfile);
          setJobSeekerProfileId(userProfile.id);

          // Pre-fill form with profile data
          setApplicationData((prev) => ({
            ...prev,
            firstName: userProfile.first_name || "",
            lastName: userProfile.last_name || "",
            email: userProfile.email || "",
            phone: userProfile.phone || "",
            location: userProfile.location || "",
            keySkills: userProfile.skills || [],
          }));
        } catch (_err) {
          // Profile doesn't exist yet - that's okay
          console.info("[Application] No profile found - user can still apply");
        }
      } catch (err) {
        console.error("Failed to fetch application data:", err);
        if (err instanceof ApiError) {
          if (err.status === 404) {
            setError(`Job not found. The job ID "${jobId}" does not exist.`);
          } else {
            setError(`Failed to load application: ${err.message}`);
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

  const handleInputChange = (
    field: keyof ApplicationFormData,
    value: string | boolean | File | string[] | null
  ): void => {
    setApplicationData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleScreeningResponse = (
    questionId: string,
    response: string
  ): void => {
    setApplicationData((prev) => ({
      ...prev,
      screeningResponses: {
        ...prev.screeningResponses,
        [questionId]: response,
      },
    }));
  };

  const addExperience = (): void => {
    const newExperience = {
      id: Date.now(),
      company: "",
      role: "",
      duration: "",
      description: "",
    };
    setApplicationData((prev) => ({
      ...prev,
      experiences: [...prev.experiences, newExperience],
    }));
  };

  const updateExperience = (id: number, field: string, value: string): void => {
    setApplicationData((prev) => ({
      ...prev,
      experiences: prev.experiences.map((exp) =>
        exp.id === id ? { ...exp, [field]: value } : exp
      ),
    }));
  };

  const removeExperience = (id: number): void => {
    setApplicationData((prev) => ({
      ...prev,
      experiences: prev.experiences.filter((exp) => exp.id !== id),
    }));
  };

  const addSkill = (skillInput: string): void => {
    const skill = skillInput.trim();
    if (skill && !applicationData.keySkills.includes(skill)) {
      handleInputChange("keySkills", [...applicationData.keySkills, skill]);
    }
  };

  const removeSkill = (skillToRemove: string): void => {
    handleInputChange(
      "keySkills",
      applicationData.keySkills.filter((skill) => skill !== skillToRemove)
    );
  };

  const handleResumeUpload = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const file = e.target.files?.[0];
    if (file) {
      handleInputChange("resumeFile", file);
      handleInputChange("resumeFilename", file.name);
    }
  };

  // Basic validation functions
  const validatePage = (
    pageNumber: number
  ): {
    isValid: boolean;
    errorCount: number;
  } => {
    const newErrors: Record<string, string> = {};

    switch (pageNumber) {
      case 1:
        if (!applicationData.firstName.trim())
          newErrors.firstName = "First name is required";
        if (!applicationData.lastName.trim())
          newErrors.lastName = "Last name is required";
        if (!applicationData.email.trim())
          newErrors.email = "Email is required";
        else if (!/\S+@\S+\.\S+/.test(applicationData.email))
          newErrors.email = "Please enter a valid email";
        if (!applicationData.phone.trim())
          newErrors.phone = "Phone number is required";
        if (!applicationData.location.trim())
          newErrors.location = "Location is required";
        if (!applicationData.zipCode.trim())
          newErrors.zipCode = "ZIP code is required";
        break;

      case 2:
        if (
          !applicationData.noExperience &&
          applicationData.experiences.every((exp) => !exp.role.trim())
        ) {
          newErrors.experience =
            "Please add at least one experience or check 'I don't have experiences to share'";
        }
        break;

      case 3:
        // Cover letter validation would depend on job requirements
        // For now, we'll make it optional unless the job requires it
        break;

      case 5:
        if (!applicationData.agreedToTerms) {
          newErrors.agreedToTerms =
            "You must agree to the terms and conditions";
        }
        break;
    }

    setErrors(newErrors);
    return {
      isValid: Object.keys(newErrors).length === 0,
      errorCount: Object.keys(newErrors).length,
    };
  };

  const nextPage = (): void => {
    const validationResult = validatePage(currentPage);

    if (validationResult.isValid && currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
      setShowToast(false);
    } else {
      if (!validationResult.isValid) {
        setToastMessage(
          `Please fix ${validationResult.errorCount} issue${
            validationResult.errorCount > 1 ? "s" : ""
          } above to continue`
        );
        setShowToast(true);
        setTimeout(() => setShowToast(false), 4000);
      }
    }
  };

  const prevPage = (): void => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
      setErrors({});
    }
  };

  const handleSubmit = async (): Promise<void> => {
    if (!jobSeekerProfileId) {
      setError(
        "Please create a job seeker profile before applying. You can do this from your profile page."
      );
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Combine cover letter and screening responses into notes
      const notesParts: string[] = [];
      if (applicationData.coverLetter) {
        notesParts.push(`Cover Letter:\n${applicationData.coverLetter}`);
      }
      if (Object.keys(applicationData.screeningResponses).length > 0) {
        notesParts.push(
          `\nScreening Questions:\n${Object.entries(
            applicationData.screeningResponses
          )
            .map(([q, a]) => `Q: ${q}\nA: ${a}`)
            .join("\n\n")}`
        );
      }

      const applicationPayload: ApplicationCreate = {
        job_id: jobId,
        job_seeker_id: jobSeekerProfileId,
        notes: notesParts.length > 0 ? notesParts.join("\n\n") : null,
      };

      await api.applications.create(applicationPayload);

      // Redirect to success page or dashboard
      router.push("/dashboard?applicationSuccess=true");
    } catch (err) {
      console.error("Failed to submit application:", err);
      if (err instanceof ApiError) {
        if (err.status === 403) {
          setError(
            "Authentication required to submit application. Please log in to apply for this job."
          );
        } else if (err.status === 404) {
          setError(
            "Job or profile not found. Please ensure you have created a job seeker profile."
          );
        } else if (err.status === 409) {
          setError("You have already applied to this job.");
        } else {
          setError(`Failed to submit application: ${err.message}`);
        }
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderPage = (): ReactElement | null => {
    switch (currentPage) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <div className="bg-gradient-to-r from-green-100 to-amber-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <User className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-green-900 mb-2">
                Let&apos;s Get to Know You
              </h2>
              <p className="text-green-700">
                We&apos;ve pre-filled as much information from your profile as
                we can. Please feel free to update and fill out any missing
                fields in this application.
              </p>
            </div>

            <div className="bg-gradient-to-r from-blue-50 to-green-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-center">
                <Heart className="w-5 h-5 text-green-600 mr-2" />
                <span className="text-sm text-green-800 font-medium">
                  Your information helps interested employers to reach out to
                  you and judge if you are a good fit for location dependent
                  roles.
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  First Name *
                </label>
                <input
                  type="text"
                  value={applicationData.firstName}
                  onChange={(e) =>
                    handleInputChange("firstName", e.target.value)
                  }
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:border-transparent bg-white/80 ${
                    errors.firstName
                      ? "border-red-300 focus:ring-red-400"
                      : "border-green-300 focus:ring-green-400"
                  }`}
                  required
                />
                {errors.firstName && (
                  <p className="text-red-600 text-sm mt-1">
                    {errors.firstName}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Last Name *
                </label>
                <input
                  type="text"
                  value={applicationData.lastName}
                  onChange={(e) =>
                    handleInputChange("lastName", e.target.value)
                  }
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:border-transparent bg-white/80 ${
                    errors.lastName
                      ? "border-red-300 focus:ring-red-400"
                      : "border-green-300 focus:ring-green-400"
                  }`}
                  required
                />
                {errors.lastName && (
                  <p className="text-red-600 text-sm mt-1">{errors.lastName}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Email Address *
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-green-500 w-4 h-4" />
                  <input
                    type="email"
                    value={applicationData.email}
                    onChange={(e) => handleInputChange("email", e.target.value)}
                    className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:border-transparent bg-white/80 ${
                      errors.email
                        ? "border-red-300 focus:ring-red-400"
                        : "border-green-300 focus:ring-green-400"
                    }`}
                    required
                  />
                </div>
                {errors.email && (
                  <p className="text-red-600 text-sm mt-1">{errors.email}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Phone Number *
                </label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-green-500 w-4 h-4" />
                  <input
                    type="tel"
                    value={applicationData.phone}
                    onChange={(e) => handleInputChange("phone", e.target.value)}
                    className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:border-transparent bg-white/80 ${
                      errors.phone
                        ? "border-red-300 focus:ring-red-400"
                        : "border-green-300 focus:ring-green-400"
                    }`}
                    required
                  />
                </div>
                {errors.phone && (
                  <p className="text-red-600 text-sm mt-1">{errors.phone}</p>
                )}
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Location *
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-green-500 w-4 h-4" />
                  <input
                    type="text"
                    value={applicationData.location}
                    onChange={(e) =>
                      handleInputChange("location", e.target.value)
                    }
                    className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:border-transparent bg-white/80 ${
                      errors.location
                        ? "border-red-300 focus:ring-red-400"
                        : "border-green-300 focus:ring-green-400"
                    }`}
                    placeholder="City, State"
                    required
                  />
                </div>
                {errors.location && (
                  <p className="text-red-600 text-sm mt-1">{errors.location}</p>
                )}
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-green-800 mb-2">
                  ZIP Code *
                </label>
                <input
                  type="text"
                  value={applicationData.zipCode}
                  onChange={(e) => handleInputChange("zipCode", e.target.value)}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:border-transparent bg-white/80 ${
                    errors.zipCode
                      ? "border-red-300 focus:ring-red-400"
                      : "border-green-300 focus:ring-green-400"
                  }`}
                  placeholder="5-digit zip code"
                  pattern="[0-9]{5}(-[0-9]{4})?"
                  required
                />
                {errors.zipCode && (
                  <p className="text-red-600 text-sm mt-1">{errors.zipCode}</p>
                )}
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <div className="bg-gradient-to-r from-green-100 to-amber-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-green-900 mb-2">
                Share Your Experience
              </h2>
              <p className="text-green-700">
                Help us understand your background and what you bring to the
                team.
              </p>
            </div>

            {/* Resume Upload */}
            <div className="bg-white border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-800 mb-4">
                Resume Upload
              </h3>

              <div className="border-2 border-dashed border-green-300 rounded-lg p-8 text-center hover:border-green-400 transition-colors">
                <Upload className="w-12 h-12 text-green-500 mx-auto mb-4" />
                <div className="mb-4">
                  <label className="bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-2 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all cursor-pointer inline-block">
                    Choose File
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleResumeUpload}
                      className="hidden"
                    />
                  </label>
                  <p className="text-sm text-green-600 mt-2">
                    or drag and drop your resume here
                  </p>
                </div>
                <p className="text-xs text-green-500">
                  PDF, DOC, or DOCX • Max 5MB
                </p>
              </div>

              {applicationData.resumeFilename && (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center">
                  <FileText className="w-4 h-4 text-green-600 mr-2" />
                  <span className="text-sm text-green-800">
                    {applicationData.resumeFilename}
                  </span>
                </div>
              )}
            </div>

            {/* Experience Summary */}
            <div className="bg-white border border-green-200 rounded-lg p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-green-800">
                  Work Experience
                </h3>
                <label className="flex items-center text-sm text-green-700">
                  <input
                    type="checkbox"
                    checked={applicationData.noExperience}
                    onChange={(e) =>
                      handleInputChange("noExperience", e.target.checked)
                    }
                    className="w-4 h-4 text-green-600 border-green-300 rounded focus:ring-green-500 mr-2"
                  />
                  I don&apos;t have experiences to share
                </label>
              </div>

              {!applicationData.noExperience && (
                <div className="space-y-6">
                  {applicationData.experiences.map((experience, index) => (
                    <div
                      key={experience.id}
                      className="border border-green-100 rounded-lg p-4"
                    >
                      <div className="flex justify-between items-start mb-4">
                        <h4 className="font-medium text-green-800">
                          Experience {index + 1}
                        </h4>
                        {applicationData.experiences.length > 1 && (
                          <button
                            onClick={() => removeExperience(experience.id)}
                            className="text-red-500 text-sm hover:text-red-700"
                          >
                            Remove
                          </button>
                        )}
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-green-800 mb-2">
                            Company
                          </label>
                          <input
                            type="text"
                            value={experience.company}
                            onChange={(e) =>
                              updateExperience(
                                experience.id,
                                "company",
                                e.target.value
                              )
                            }
                            className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                            placeholder="e.g. ABC Marketing Agency"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-green-800 mb-2">
                            Job Title
                          </label>
                          <div className="relative">
                            <Briefcase className="absolute left-3 top-1/2 transform -translate-y-1/2 text-green-500 w-4 h-4" />
                            <input
                              type="text"
                              value={experience.role}
                              onChange={(e) =>
                                updateExperience(
                                  experience.id,
                                  "role",
                                  e.target.value
                                )
                              }
                              className="w-full pl-10 pr-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                              placeholder="e.g. Marketing Specialist"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-green-800 mb-2">
                            Duration
                          </label>
                          <input
                            type="text"
                            value={experience.duration}
                            onChange={(e) =>
                              updateExperience(
                                experience.id,
                                "duration",
                                e.target.value
                              )
                            }
                            className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                            placeholder="e.g. 2022 - Present"
                          />
                        </div>
                      </div>

                      <div className="mt-4">
                        <label className="block text-sm font-medium text-green-800 mb-2">
                          Role Description
                        </label>
                        <textarea
                          value={experience.description}
                          onChange={(e) =>
                            updateExperience(
                              experience.id,
                              "description",
                              e.target.value
                            )
                          }
                          rows={3}
                          className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 resize-none"
                          placeholder="Briefly describe your key responsibilities and achievements..."
                        />
                      </div>
                    </div>
                  ))}

                  <button
                    onClick={addExperience}
                    className="w-full py-3 border-2 border-dashed border-green-300 rounded-lg text-green-600 hover:border-green-400 hover:text-green-700 transition-colors font-medium"
                  >
                    + Add Another Experience
                  </button>
                </div>
              )}

              {applicationData.noExperience && (
                <div className="text-center py-8">
                  <Heart className="w-12 h-12 text-green-500 mx-auto mb-3" />
                  <h4 className="font-medium text-green-800 mb-2">
                    Everyone Starts Somewhere!
                  </h4>
                  <p className="text-sm text-green-700">
                    No worries about lacking work experience. Focus on your
                    education, volunteer work, personal projects, or
                    transferable skills that show your potential.
                  </p>
                </div>
              )}
            </div>

            {/* Key Skills */}
            <div>
              <label className="block text-sm font-medium text-green-800 mb-2">
                Key Skills
              </label>
              <div className="flex flex-wrap gap-2 mb-3">
                {applicationData.keySkills.map((skill, index) => (
                  <span
                    key={index}
                    className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm border border-green-200 flex items-center"
                  >
                    {skill}
                    <button
                      type="button"
                      onClick={() => removeSkill(skill)}
                      className="ml-2 text-green-600 hover:text-green-800 w-4 h-4 flex items-center justify-center"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  id="skillInput"
                  className="flex-1 px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                  placeholder="Add a skill"
                  onKeyDown={(e) => {
                    if (
                      e.key === "Enter" &&
                      (e.target as HTMLInputElement).value.trim()
                    ) {
                      e.preventDefault();
                      addSkill((e.target as HTMLInputElement).value);
                      (e.target as HTMLInputElement).value = "";
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={() => {
                    const input = document.getElementById(
                      "skillInput"
                    ) as HTMLInputElement;
                    if (input && input.value.trim()) {
                      addSkill(input.value);
                      input.value = "";
                    }
                  }}
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium whitespace-nowrap"
                >
                  Add
                </button>
              </div>
              <p className="text-xs text-green-600 mt-2">
                Add skills relevant to this position. Press Enter or click
                &quot;Add&quot; to include each skill.
              </p>
            </div>
          </div>
        );

      case 3:
        // Show screening questions and cover letter based on settings
        const hasScreeningQuestions =
          applicationSettings?.screeningQuestions &&
          applicationSettings.screeningQuestions.filter((q) => q.trim())
            .length > 0;
        const showCoverLetter = applicationSettings?.requireCoverLetter ?? true;

        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <div className="bg-gradient-to-r from-green-100 to-amber-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageSquare className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-green-900 mb-2">
                Tell Us More
              </h2>
              <p className="text-green-700">
                {hasScreeningQuestions || showCoverLetter
                  ? "Help us understand why you're interested and answer a few specific questions."
                  : "Help us understand why you're interested in this role."}
              </p>
            </div>

            {/* Cover Letter - only show if required */}
            {showCoverLetter && (
              <div className="bg-white border border-green-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-green-800 mb-4">
                  Cover Letter {applicationSettings?.requireCoverLetter && "*"}
                </h3>
                <textarea
                  value={applicationData.coverLetter}
                  onChange={(e) =>
                    handleInputChange("coverLetter", e.target.value)
                  }
                  rows={6}
                  className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 resize-none"
                  placeholder="Tell us why you're excited about this role and what you'd bring to the team..."
                  required={applicationSettings?.requireCoverLetter}
                />
                <p className="text-xs text-green-600 mt-2">
                  Share what excites you about this opportunity and how your
                  experience aligns with the role.
                </p>
              </div>
            )}

            {/* Screening Questions */}
            {hasScreeningQuestions && (
              <div className="bg-white border border-green-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-green-800 mb-4">
                  Screening Questions
                </h3>
                <div className="space-y-6">
                  {applicationSettings.screeningQuestions
                    .filter((q) => q.trim())
                    .map((question, index) => (
                      <div key={index}>
                        <label className="block text-sm font-medium text-green-800 mb-2">
                          {question} *
                        </label>
                        <textarea
                          value={
                            applicationData.screeningResponses[question] || ""
                          }
                          onChange={(e) =>
                            handleScreeningResponse(question, e.target.value)
                          }
                          rows={3}
                          className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 resize-none"
                          placeholder="Your answer..."
                          required
                        />
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Encouraging Message */}
            <div className="bg-gradient-to-r from-green-50 to-amber-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center">
                <Star className="w-5 h-5 text-amber-500 mr-2" />
                <span className="text-sm text-green-800">
                  You&apos;re doing great! Your authentic responses help us find
                  the right fit for everyone.
                </span>
              </div>
            </div>
          </div>
        );

      case 4:
        // Skip EEO page if disabled
        if (!applicationSettings?.equalOpportunityEnabled) {
          // Auto-advance to review page
          if (currentPage === 4) {
            setTimeout(() => {
              setCurrentPage(5);
            }, 0);
          }
          return <></>;
        }

        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <div className="bg-gradient-to-r from-green-100 to-amber-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Scale className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-green-900 mb-2">
                Equal Opportunity Information
              </h2>
              <p className="text-green-700">
                This information is voluntary and used only for compliance
                reporting.
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-blue-800 mb-2">Why We Ask</h3>
              <p className="text-sm text-blue-700">
                This information helps ensure we&apos;re providing equal
                opportunities to all candidates. Your responses are completely
                voluntary and won&apos;t affect hiring decisions.
              </p>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-green-800 mb-3">
                  Race/Ethnicity (Optional)
                </label>
                <div className="space-y-2">
                  {[
                    "American Indian or Alaska Native",
                    "Asian",
                    "Black or African American",
                    "Hispanic or Latino",
                    "Native Hawaiian or Other Pacific Islander",
                    "White",
                    "Two or More Races",
                    "Prefer not to answer",
                  ].map((option) => (
                    <label key={option} className="flex items-center">
                      <input
                        type="radio"
                        name="raceEthnicity"
                        value={option}
                        checked={applicationData.raceEthnicity === option}
                        onChange={(e) =>
                          handleInputChange("raceEthnicity", e.target.value)
                        }
                        className="w-4 h-4 text-green-600 border-green-300 focus:ring-green-500"
                      />
                      <span className="ml-2 text-sm text-green-700">
                        {option}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-green-800 mb-3">
                  Veteran Status (Optional)
                </label>
                <div className="space-y-2">
                  {[
                    "I am a veteran",
                    "I am not a veteran",
                    "Prefer not to answer",
                  ].map((option) => (
                    <label key={option} className="flex items-center">
                      <input
                        type="radio"
                        name="veteranStatus"
                        value={option}
                        checked={applicationData.veteranStatus === option}
                        onChange={(e) =>
                          handleInputChange("veteranStatus", e.target.value)
                        }
                        className="w-4 h-4 text-green-600 border-green-300 focus:ring-green-500"
                      />
                      <span className="ml-2 text-sm text-green-700">
                        {option}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-green-800 mb-3">
                  Disability Status (Optional)
                </label>
                <div className="space-y-2">
                  {[
                    "Yes, I have a disability",
                    "No, I do not have a disability",
                    "Prefer not to answer",
                  ].map((option) => (
                    <label key={option} className="flex items-center">
                      <input
                        type="radio"
                        name="disabilityStatus"
                        value={option}
                        checked={applicationData.disabilityStatus === option}
                        onChange={(e) =>
                          handleInputChange("disabilityStatus", e.target.value)
                        }
                        className="w-4 h-4 text-green-600 border-green-300 focus:ring-green-500"
                      />
                      <span className="ml-2 text-sm text-green-700">
                        {option}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <p className="text-xs text-gray-600">
                <strong>Legal Notice:</strong> This information is kept separate
                from your application materials and is used solely for
                compliance with federal equal opportunity regulations. All
                responses are voluntary.
              </p>
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <div className="bg-gradient-to-r from-green-100 to-amber-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Eye className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-green-900 mb-2">
                Review & Submit
              </h2>
              <p className="text-green-700">
                Take a moment to review your application before submitting.
              </p>
            </div>

            {/* Application Summary */}
            <div className="bg-white border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-800 mb-4">
                Application Summary
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h4 className="font-medium text-green-800 mb-2">
                    Personal Information
                  </h4>
                  <div className="text-sm text-green-700 space-y-1">
                    <p>
                      {applicationData.firstName} {applicationData.lastName}
                    </p>
                    <p>{applicationData.email}</p>
                    <p>{applicationData.phone}</p>
                    <p>
                      {applicationData.location} {applicationData.zipCode}
                    </p>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-green-800 mb-2">
                    Experience
                  </h4>
                  <div className="text-sm text-green-700 space-y-1">
                    {applicationData.noExperience ? (
                      <p>New to workforce</p>
                    ) : (
                      <>
                        <p>
                          <strong>Positions:</strong>{" "}
                          {applicationData.experiences.length}
                        </p>
                        <p>
                          <strong>Skills:</strong>{" "}
                          {applicationData.keySkills.join(", ")}
                        </p>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <div className="border-t border-green-200 pt-4">
                <h4 className="font-medium text-green-800 mb-2">
                  Documents & Responses
                </h4>
                <div className="text-sm text-green-700 space-y-1">
                  {applicationData.resumeFilename ? (
                    <p>✓ Resume uploaded</p>
                  ) : (
                    <p>○ Resume not uploaded</p>
                  )}
                  {applicationData.coverLetter && (
                    <p>✓ Cover letter provided</p>
                  )}
                </div>
              </div>
            </div>

            {/* Final Consent */}
            <div className="bg-white border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-800 mb-4">
                Final Steps
              </h3>

              <div className="space-y-4">
                <label className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    checked={applicationData.agreedToTerms}
                    onChange={(e) =>
                      handleInputChange("agreedToTerms", e.target.checked)
                    }
                    className="w-4 h-4 text-green-600 border-green-300 rounded focus:ring-green-500 mt-0.5"
                    required
                  />
                  <span className="text-sm text-green-700">
                    I confirm that the information provided is accurate and I
                    agree to the{" "}
                    <button className="text-green-600 underline hover:text-green-800">
                      terms and conditions
                    </button>
                    .
                  </span>
                </label>

                <label className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    checked={applicationData.allowContactFromEmployer}
                    onChange={(e) =>
                      handleInputChange(
                        "allowContactFromEmployer",
                        e.target.checked
                      )
                    }
                    className="w-4 h-4 text-green-600 border-green-300 rounded focus:ring-green-500 mt-0.5"
                  />
                  <span className="text-sm text-green-700">
                    I&apos;m open to being contacted about this position and
                    similar opportunities at this company.
                  </span>
                </label>
              </div>
            </div>

            {/* Encouraging Final Message */}
            <div className="bg-gradient-to-r from-green-50 to-amber-50 border border-green-200 rounded-lg p-6 text-center">
              <Heart className="w-8 h-8 text-green-600 mx-auto mb-3" />
              <h4 className="font-semibold text-green-800 mb-2">
                You&apos;ve Got This! 🌟
              </h4>
              <p className="text-sm text-green-700">
                Your application shows your unique value and experience.
                Regardless of the outcome, you&apos;ve taken a positive step in
                your career journey.
              </p>
            </div>
          </div>
        );

      default:
        return <div>Invalid page</div>;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 mx-auto text-green-600 animate-spin mb-4" />
          <p className="text-green-800">Loading application form...</p>
        </div>
      </div>
    );
  }

  if (error && !job) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="w-12 h-12 mx-auto text-red-500 mb-4" />
          <p className="text-red-800 font-semibold mb-2">
            Error loading application
          </p>
          <p className="text-red-600">{error}</p>
          <Link
            href="/jobs"
            className="mt-4 inline-block text-green-600 hover:text-green-800"
          >
            ← Back to Jobs
          </Link>
        </div>
      </div>
    );
  }

  if (!job) {
    return null;
  }

  // Handle External/Email application methods
  if (applicationSettings?.applicationMethod === "External") {
    if (applicationSettings.externalUrl) {
      // Redirect to external URL
      if (typeof window !== "undefined") {
        window.location.href = applicationSettings.externalUrl;
      }
      return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100 flex items-center justify-center">
          <div className="text-center">
            <RefreshCw className="w-12 h-12 mx-auto text-green-600 animate-spin mb-4" />
            <p className="text-green-800">Redirecting to application page...</p>
          </div>
        </div>
      );
    }
  }

  if (applicationSettings?.applicationMethod === "Email") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100 flex items-center justify-center">
        <div className="text-center max-w-md bg-white/80 backdrop-blur-sm rounded-xl border border-green-200 p-8">
          <Mail className="w-16 h-16 mx-auto text-green-600 mb-4" />
          <h2 className="text-2xl font-bold text-green-900 mb-4">
            Apply via Email
          </h2>
          <p className="text-green-700 mb-6">
            This employer prefers to receive applications via email. Please send
            your resume and cover letter to:
          </p>
          {applicationSettings.applicationEmail && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <p className="text-lg font-semibold text-green-800">
                {applicationSettings.applicationEmail}
              </p>
            </div>
          )}
          <Link
            href={`/jobs/${jobId}`}
            className="inline-block px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all"
          >
            ← Back to Job Listing
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      {/* Job Header */}
      <div className="bg-white/70 backdrop-blur-sm border-b border-green-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-green-900 mb-1">
              Apply for {job.title}
            </h1>
            <p className="text-green-700">
              {job.company} • {job.remote_ok ? "Remote" : job.location} •{" "}
              {job.job_type}
            </p>
            {job.salary_min || job.salary_max ? (
              <p className="text-green-600 text-sm mt-1">
                ${job.salary_min?.toLocaleString() || "?"} - $
                {job.salary_max?.toLocaleString() || "?"}
              </p>
            ) : null}
          </div>
        </div>
      </div>

      {/* Progress Indicator */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-center mb-2">
          {[
            { page: 1, label: "Profile" },
            { page: 2, label: "Experience" },
            { page: 3, label: "Questions" },
            { page: 4, label: "EEO" },
            { page: 5, label: "Review" },
          ].map((step, index) => (
            <React.Fragment key={step.page}>
              <div className="flex flex-col items-center">
                <div
                  className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                    currentPage === step.page
                      ? "bg-green-600 text-white"
                      : currentPage > step.page
                        ? "bg-green-500 text-white"
                        : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {currentPage > step.page ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : (
                    step.page
                  )}
                </div>
              </div>
              {index < 4 && (
                <div
                  className={`w-16 h-0.5 ${
                    currentPage > step.page ? "bg-green-500" : "bg-gray-200"
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>
        <div className="flex items-center justify-center">
          {[
            { page: 1, label: "Profile" },
            { page: 2, label: "Experience" },
            { page: 3, label: "Questions" },
            { page: 4, label: "EEO" },
            { page: 5, label: "Review" },
          ].map((step, index) => (
            <React.Fragment key={step.page}>
              <div className="flex flex-col items-center">
                <span
                  className={`text-xs text-green-600 text-center ${
                    currentPage === step.page ? "font-medium" : ""
                  }`}
                >
                  {step.label}
                </span>
              </div>
              {index < 4 && <div className="w-16" />}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 shadow-sm p-6 mb-8">
          {renderPage()}
        </div>

        {/* Navigation */}
        <div className="flex justify-between relative">
          {/* Toast Notification */}
          {showToast && (
            <div className="absolute bottom-16 left-1/2 transform -translate-x-1/2 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center space-x-2 z-10 animate-pulse">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm font-medium">{toastMessage}</span>
            </div>
          )}

          <button
            onClick={prevPage}
            disabled={currentPage === 1}
            className={`flex items-center px-6 py-3 rounded-lg font-medium transition-all ${
              currentPage === 1
                ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                : "bg-green-50 text-green-700 border border-green-300 hover:bg-green-100"
            }`}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Previous
          </button>

          {currentPage < totalPages ? (
            <button
              onClick={nextPage}
              className="flex items-center px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all"
            >
              Continue
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          ) : (
            <button
              onClick={() => {
                void handleSubmit();
              }}
              disabled={!applicationData.agreedToTerms || isSubmitting}
              className={`flex items-center px-6 py-3 rounded-lg font-semibold transition-all ${
                applicationData.agreedToTerms && !isSubmitting
                  ? "bg-gradient-to-r from-green-600 to-green-700 text-white hover:from-green-700 hover:to-green-800"
                  : "bg-gray-300 text-gray-500 cursor-not-allowed"
              }`}
            >
              {isSubmitting ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  Submit Application
                  <CheckCircle className="w-4 h-4 ml-2" />
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
