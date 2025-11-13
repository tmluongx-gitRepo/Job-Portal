"use client";

import { useState, useEffect, type ReactElement } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  Eye,
  Plus,
  X,
  FileText,
  MessageSquare,
  ArrowLeft,
  ArrowRight,
  CheckCircle,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import { api, ApiError } from "../../lib/api";
import type { Job } from "../../lib/api";

interface ApplicationSettings {
  applicationMethod: "Internal" | "External" | "Email";
  externalUrl: string;
  applicationEmail: string;
  requireCoverLetter: boolean;
  screeningQuestions: string[];
  equalOpportunityEnabled: boolean;
}

export default function JobApplicationSetupPage(): ReactElement {
  const searchParams = useSearchParams();
  const router = useRouter();
  const jobId = searchParams.get("jobId");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [saving, setSaving] = useState(false);

  const [applicationSettings, setApplicationSettings] =
    useState<ApplicationSettings>({
      applicationMethod: "Internal",
      externalUrl: "",
      applicationEmail: "",
      requireCoverLetter: true,
      screeningQuestions: [""],
      equalOpportunityEnabled: true,
    });

  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 4;

  // Fetch job data
  useEffect(() => {
    const fetchJob = async (): Promise<void> => {
      if (!jobId) {
        setError("No job ID provided. Please navigate to this page from a job posting.");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const jobData = (await api.jobs.getById(jobId)) as Job;
        setJob(jobData);
      } catch (err) {
        console.error("Failed to fetch job:", err);
        if (err instanceof ApiError) {
          if (err.status === 404) {
            setError(`Job not found. The job ID "${jobId}" does not exist.`);
          } else {
            setError(`Failed to load job: ${err.message}`);
          }
        } else {
          setError("An unexpected error occurred. Please try again.");
        }
      } finally {
        setLoading(false);
      }
    };

    void fetchJob();
  }, [jobId]);

  const handleInputChange = (
    field: keyof ApplicationSettings,
    value: string | boolean
  ): void => {
    setApplicationSettings((prev: ApplicationSettings) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleQuestionChange = (index: number, value: string): void => {
    setApplicationSettings((prev: ApplicationSettings) => ({
      ...prev,
      screeningQuestions: prev.screeningQuestions.map((q, i) =>
        i === index ? value : q
      ),
    }));
  };

  const addScreeningQuestion = (): void => {
    setApplicationSettings((prev: ApplicationSettings) => ({
      ...prev,
      screeningQuestions: [...prev.screeningQuestions, ""],
    }));
  };

  const removeScreeningQuestion = (index: number): void => {
    setApplicationSettings((prev: ApplicationSettings) => ({
      ...prev,
      screeningQuestions: prev.screeningQuestions.filter((_, i) => i !== index),
    }));
  };

  const nextStep = (): void => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = (): void => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSaveSettings = async (): Promise<void> => {
    if (!jobId || !job) {
      setError("Job ID is required to save settings");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      // TODO: When backend supports application settings, update the job with these settings
      // For now, we'll store them in localStorage as a temporary solution
      // In the future, this should be: await api.jobs.update(jobId, { application_settings: ... })
      
      const settingsToSave = {
        jobId,
        ...applicationSettings,
      };
      
      localStorage.setItem(`job_application_settings_${jobId}`, JSON.stringify(settingsToSave));

      // Redirect to job posting page or show success
      router.push(`/job-posting?jobId=${jobId}&settingsSaved=true`);
    } catch (err) {
      console.error("Failed to save application settings:", err);
      if (err instanceof ApiError) {
        setError(`Failed to save settings: ${err.message}`);
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setSaving(false);
    }
  };

  const renderStep = (): ReactElement | null => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-blue-50 to-green-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-green-800 mb-2">
                Application Method
              </h3>
              <p className="text-sm text-green-600 mb-4">
                How do you want candidates to apply for this position?
              </p>

              <div className="space-y-3">
                <label className="flex items-center space-x-3 p-3 border border-green-200 rounded-lg cursor-pointer hover:bg-green-50 transition-colors">
                  <input
                    type="radio"
                    name="applicationMethod"
                    value="Internal"
                    checked={
                      applicationSettings.applicationMethod === "Internal"
                    }
                    onChange={(e) =>
                      handleInputChange(
                        "applicationMethod",
                        e.target.value as "Internal"
                      )
                    }
                    className="w-4 h-4 text-green-600 border-green-300 focus:ring-green-500"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-green-800">
                      Through Career Harmony (Recommended)
                    </div>
                    <div className="text-sm text-green-600">
                      Candidates apply directly on your job posting with our
                      streamlined form
                    </div>
                  </div>
                </label>

                <label className="flex items-center space-x-3 p-3 border border-green-200 rounded-lg cursor-pointer hover:bg-green-50 transition-colors">
                  <input
                    type="radio"
                    name="applicationMethod"
                    value="External"
                    checked={
                      applicationSettings.applicationMethod === "External"
                    }
                    onChange={(e) =>
                      handleInputChange(
                        "applicationMethod",
                        e.target.value as "External"
                      )
                    }
                    className="w-4 h-4 text-green-600 border-green-300 focus:ring-green-500"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-green-800">
                      Redirect to Company Website
                    </div>
                    <div className="text-sm text-green-600">
                      Send candidates to your company&apos;s application page
                    </div>
                  </div>
                </label>

                <label className="flex items-center space-x-3 p-3 border border-green-200 rounded-lg cursor-pointer hover:bg-green-50 transition-colors">
                  <input
                    type="radio"
                    name="applicationMethod"
                    value="Email"
                    checked={applicationSettings.applicationMethod === "Email"}
                    onChange={(e) =>
                      handleInputChange(
                        "applicationMethod",
                        e.target.value as "Email"
                      )
                    }
                    className="w-4 h-4 text-green-600 border-green-300 focus:ring-green-500"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-green-800">
                      Email Applications
                    </div>
                    <div className="text-sm text-green-600">
                      Candidates email their resume and cover letter directly to
                      you
                    </div>
                  </div>
                </label>
              </div>
            </div>

            {applicationSettings.applicationMethod === "External" && (
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  External Application URL *
                </label>
                <input
                  type="url"
                  value={applicationSettings.externalUrl}
                  onChange={(e) =>
                    handleInputChange("externalUrl", e.target.value)
                  }
                  className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                  placeholder="https://yourcompany.com/careers/apply"
                />
                <p className="text-xs text-green-600 mt-2">
                  Candidates will be redirected here when they click
                  &quot;Apply&quot;
                </p>
              </div>
            )}

            {applicationSettings.applicationMethod === "Email" && (
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                  Application Email Address *
                </label>
                <input
                  type="email"
                  value={applicationSettings.applicationEmail}
                  onChange={(e) =>
                    handleInputChange("applicationEmail", e.target.value)
                  }
                  className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                  placeholder="careers@yourcompany.com"
                />
                <p className="text-xs text-green-600 mt-2">
                  Candidates will be shown this email address and instructed to
                  send their application materials
                </p>
              </div>
            )}

            {applicationSettings.applicationMethod === "Internal" && (
              <div className="space-y-4">
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-amber-800">
                      Application Options
                    </h4>
                    <span className="text-xs text-amber-600">
                      Customize your application process
                    </span>
                  </div>

                  <div className="space-y-3">
                    <label className="flex items-center space-x-3 p-2 rounded hover:bg-amber-100/50 transition-colors">
                      <input
                        type="checkbox"
                        checked={applicationSettings.requireCoverLetter}
                        onChange={(e) =>
                          handleInputChange(
                            "requireCoverLetter",
                            e.target.checked
                          )
                        }
                        className="w-4 h-4 text-green-600 border-green-300 rounded focus:ring-green-500"
                      />
                      <div className="flex-1">
                        <span className="text-sm font-medium text-amber-800">
                          Require cover letter
                        </span>
                        <p className="text-xs text-amber-600 mt-0.5">
                          Candidates must include a cover letter with their
                          application
                        </p>
                      </div>
                    </label>
                  </div>

                  <div className="mt-3 pt-3 border-t border-amber-300">
                    <p className="text-xs text-amber-600">
                      💡 <span className="font-medium">Tip:</span> Cover letters
                      help you understand candidate motivation, but making them
                      optional can increase application rates.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        );

      case 2:
        // Don't show this step if not using Internal applications
        if (applicationSettings.applicationMethod !== "Internal") {
          return (
            <div className="space-y-6">
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
                <MessageSquare className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-semibold text-gray-700 mb-2">
                  Custom Questions Not Available
                </h3>
                <p className="text-gray-600 mb-4">
                  Custom screening questions are only available when candidates
                  apply &quot;Through Career Harmony&quot;
                </p>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-700">
                    💡 To add custom questions, go back and select{" "}
                    <strong>
                      &quot;Through Career Harmony (Recommended)&quot;
                    </strong>{" "}
                    as your application method.
                  </p>
                </div>
              </div>
            </div>
          );
        }

        return (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-purple-50 to-green-50 border border-purple-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-green-800 mb-2">
                Custom Screening Questions
              </h3>
              <p className="text-sm text-green-600 mb-4">
                Add specific questions to help you screen candidates. Keep
                questions clear and job-relevant.
              </p>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-green-800">Your Questions</h4>
                <span className="text-xs text-green-600">
                  {
                    applicationSettings.screeningQuestions.filter((q) =>
                      q.trim()
                    ).length
                  }{" "}
                  questions added
                </span>
              </div>

              {applicationSettings.screeningQuestions.map((question, index) => (
                <div key={index} className="space-y-2">
                  <label className="block text-sm font-medium text-green-700">
                    Question {index + 1}
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={question}
                      onChange={(e) =>
                        handleQuestionChange(index, e.target.value)
                      }
                      className="flex-1 px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                      placeholder="e.g., Do you have experience with social media advertising?"
                    />
                    {applicationSettings.screeningQuestions.length > 1 && (
                      <button
                        onClick={() => removeScreeningQuestion(index)}
                        className="px-3 py-3 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              ))}

              <button
                onClick={addScreeningQuestion}
                className="flex items-center px-4 py-2 text-green-600 hover:text-green-800 hover:bg-green-50 rounded-lg transition-colors text-sm"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Another Question
              </button>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h5 className="font-medium text-blue-800 mb-2">
                  💡 Question Tips
                </h5>
                <ul className="text-xs text-blue-700 space-y-1">
                  <li>
                    • Ask about specific skills or experience relevant to the
                    role
                  </li>
                  <li>• Keep questions clear and easy to understand</li>
                  <li>
                    • Avoid questions about protected characteristics (age,
                    race, etc.)
                  </li>
                  <li>
                    • Consider what would help you quickly identify qualified
                    candidates
                  </li>
                </ul>
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-green-50 to-amber-50 border border-green-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-green-800 mb-2">
                Equal Opportunity & Compliance
              </h3>
              <p className="text-sm text-green-600 mb-4">
                Configure compliance settings for your application process
              </p>
            </div>

            <div className="space-y-4">
              <div className="bg-white border border-green-200 rounded-lg p-4">
                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={applicationSettings.equalOpportunityEnabled}
                    onChange={(e) =>
                      handleInputChange(
                        "equalOpportunityEnabled",
                        e.target.checked
                      )
                    }
                    className="w-4 h-4 text-green-600 border-green-300 rounded focus:ring-green-500"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-green-800">
                      Include Equal Opportunity Disclosure Page
                    </div>
                    <div className="text-sm text-green-600 mt-1">
                      Required for most employers. Collects voluntary
                      demographic information for compliance reporting.
                    </div>
                  </div>
                </label>
              </div>

              {applicationSettings.equalOpportunityEnabled && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h5 className="font-medium text-gray-800 mb-3">
                    Information Collected (All Optional):
                  </h5>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Race and ethnicity identification</li>
                    <li>• Veteran status</li>
                    <li>• Disability status</li>
                    <li>• Gender identity (where legally required)</li>
                  </ul>
                  <p className="text-xs text-gray-500 mt-3">
                    This information is used for compliance reporting only and
                    will not affect hiring decisions. All responses are
                    voluntary and kept separate from application materials.
                  </p>
                </div>
              )}

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <h5 className="font-medium text-amber-800 mb-2">
                  ⚖️ Legal Note
                </h5>
                <p className="text-xs text-amber-700">
                  Equal opportunity data collection helps ensure compliance with
                  federal regulations. Consult with your HR or legal team if you
                  have questions about requirements for your organization.
                </p>
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-blue-50 to-green-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-green-800 mb-2">
                Review & Preview
              </h3>
              <p className="text-sm text-green-600 mb-4">
                Review your application setup and preview how candidates will
                see your job application
              </p>
            </div>

            {/* Application Setup Summary */}
            <div className="bg-white border border-green-200 rounded-lg p-6">
              <h4 className="font-semibold text-green-800 mb-4">
                Application Setup Summary
              </h4>

              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-green-700">Application Method:</span>
                  <span className="font-medium text-green-900">
                    {applicationSettings.applicationMethod}
                  </span>
                </div>

                {applicationSettings.applicationMethod === "Internal" && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-green-700">Cover Letter:</span>
                      <span className="font-medium text-green-900">
                        {applicationSettings.requireCoverLetter
                          ? "Required"
                          : "Optional"}
                      </span>
                    </div>

                    <div className="flex justify-between">
                      <span className="text-green-700">Custom Questions:</span>
                      <span className="font-medium text-green-900">
                        {
                          applicationSettings.screeningQuestions.filter((q) =>
                            q.trim()
                          ).length
                        }{" "}
                        questions
                      </span>
                    </div>
                  </>
                )}

                {applicationSettings.externalUrl && (
                  <div className="flex justify-between">
                    <span className="text-green-700">External URL:</span>
                    <span className="font-medium text-green-900 truncate">
                      {applicationSettings.externalUrl}
                    </span>
                  </div>
                )}

                {applicationSettings.applicationEmail && (
                  <div className="flex justify-between">
                    <span className="text-green-700">Application Email:</span>
                    <span className="font-medium text-green-900">
                      {applicationSettings.applicationEmail}
                    </span>
                  </div>
                )}

                <div className="flex justify-between">
                  <span className="text-green-700">Equal Opportunity:</span>
                  <span className="font-medium text-green-900">
                    {applicationSettings.equalOpportunityEnabled
                      ? "Enabled"
                      : "Disabled"}
                  </span>
                </div>
              </div>
            </div>

            {/* Preview Section */}
            <div className="bg-white border border-green-200 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-green-800">
                  Application Preview
                </h4>
                <Link
                  href={jobId ? `/apply/${jobId}` : "#"}
                  onClick={(e) => {
                    if (!jobId) {
                      e.preventDefault();
                    }
                  }}
                  className={`flex items-center px-4 py-2 bg-green-50 text-green-700 border border-green-300 rounded-lg font-medium hover:bg-green-100 transition-all text-sm ${
                    !jobId ? "pointer-events-none opacity-50 cursor-not-allowed" : ""
                  }`}
                >
                  <Eye className="w-4 h-4 mr-2" />
                  Preview Application Form
                </Link>
              </div>

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-center py-8">
                  <div className="text-center">
                    <FileText className="w-12 h-12 mx-auto text-gray-400 mb-3" />
                    <p className="text-gray-600 text-sm">
                      Application preview will show here
                    </p>
                    <p className="text-gray-500 text-xs mt-1">
                      Click &quot;Preview Application Form&quot; to see how
                      candidates will experience your application
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center text-sm text-green-600 mb-2">
            <span>Job Posting</span>
            <ArrowRight className="w-4 h-4 mx-2" />
            <span className="font-medium">Application Setup</span>
          </div>
          <h1 className="text-3xl font-bold text-green-900 mb-2">
            Configure Job Applications
          </h1>
          <p className="text-green-700">
            {job
              ? `Set up how candidates will apply for your "${job.title}" position`
              : "Set up how candidates will apply for this position"}
          </p>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {loading && (
          <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-12 text-center mb-8">
            <RefreshCw className="w-8 h-8 text-green-600 animate-spin mx-auto mb-4" />
            <p className="text-green-700">Loading job information...</p>
          </div>
        )}

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center">
            {[1, 2, 3, 4].map((step) => (
              <div key={step} className="flex items-center">
                <div
                  className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                    currentStep === step
                      ? "bg-green-600 text-white"
                      : currentStep > step
                        ? "bg-green-500 text-white"
                        : step === 2 &&
                            applicationSettings.applicationMethod !== "Internal"
                          ? "bg-gray-200 text-gray-400"
                          : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {currentStep > step ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : (
                    step
                  )}
                </div>
                {step < 4 && (
                  <div
                    className={`w-12 h-0.5 ${
                      currentStep > step
                        ? "bg-green-500"
                        : step === 2 &&
                            applicationSettings.applicationMethod !== "Internal"
                          ? "bg-gray-200"
                          : "bg-gray-200"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-center mt-2 text-xs text-green-600">
            <div className="flex items-center space-x-1">
              <span className={currentStep === 1 ? "font-medium" : ""}>
                Method
              </span>
              <span className="text-gray-300">•</span>
              <span
                className={`${currentStep === 2 ? "font-medium" : ""} ${
                  applicationSettings.applicationMethod !== "Internal"
                    ? "text-gray-400 line-through"
                    : ""
                }`}
              >
                Questions
              </span>
              <span className="text-gray-300">•</span>
              <span className={currentStep === 3 ? "font-medium" : ""}>
                Legal
              </span>
              <span className="text-gray-300">•</span>
              <span className={currentStep === 4 ? "font-medium" : ""}>
                Review
              </span>
            </div>
          </div>
        </div>

        {/* Step Content */}
        {!loading && job && (
          <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 shadow-sm p-6 mb-8">
            {renderStep()}
          </div>
        )}

        {/* Navigation */}
        {!loading && job && (
          <div className="flex justify-between">
            <button
              onClick={prevStep}
              disabled={currentStep === 1}
              className={`flex items-center px-6 py-3 rounded-lg font-medium transition-all ${
                currentStep === 1
                  ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                  : "bg-green-50 text-green-700 border border-green-300 hover:bg-green-100"
              }`}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Previous
            </button>

            {currentStep < totalSteps ? (
              <button
                onClick={nextStep}
                className="flex items-center px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all"
              >
                Next
                <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            ) : (
              <button
                onClick={() => {
                  void handleSaveSettings();
                }}
                disabled={saving}
                className={`flex items-center px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {saving ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4 mr-2" />
                    Save Application Settings
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
