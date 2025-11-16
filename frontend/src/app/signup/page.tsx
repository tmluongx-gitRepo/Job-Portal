"use client";

import {
  useState,
  type FormEvent,
  type ChangeEvent,
  type ReactElement,
} from "react";

import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  Heart,
  Users,
  ArrowRight,
  ArrowLeft,
  Check,
} from "lucide-react";
import { authApi, api, type ApiError } from "@/lib/api";
import type { EmailConfirmationResponse } from "@/lib/api";

interface FormErrors {
  accountType?: string;
  firstName?: string;
  lastName?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  agreeToTerms?: string;
  company_name?: string;
  description?: string;
  industry?: string;
  company_size?: string;
  location?: string;
  job_title?: string;
}

interface CompanyProfile {
  company_name: string;
  description: string;
  industry: string;
  company_size: string;
  location: string;
  website: string;
  phone: string;
  job_title: string;
  founded_year: string;
  remote_policy: string;
  work_environment: string[];
  benefits: string[];
}

export default function SignupPage(): ReactElement {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
    accountType: "jobseeker" as "jobseeker" | "employer",
    agreeToTerms: false,
  });

  const [companyProfile, setCompanyProfile] = useState<CompanyProfile>({
    company_name: "",
    description: "",
    industry: "",
    company_size: "",
    location: "",
    website: "",
    phone: "",
    job_title: "",
    founded_year: "",
    remote_policy: "flexible",
    work_environment: [],
    benefits: [],
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [showErrorToast, setShowErrorToast] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>): void => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleCompanyProfileChange = (
    field: keyof CompanyProfile,
    value: string | string[]
  ): void => {
    setCompanyProfile((prev) => ({ ...prev, [field]: value }));
  };

  const handleCheckboxChange = (
    field: "work_environment" | "benefits",
    value: string,
    checked: boolean
  ): void => {
    setCompanyProfile((prev) => {
      const currentValues = prev[field];
      const newValues = checked
        ? [...currentValues, value]
        : currentValues.filter((v) => v !== value);
      return { ...prev, [field]: newValues };
    });
  };

  const validateStep1 = (): boolean => {
    const newErrors: FormErrors = {};

    // Account type defaults to "jobseeker", so validation is only needed if it's somehow invalid
    // This should never happen in normal use, but we check for safety
    if (formData.accountType !== "jobseeker" && formData.accountType !== "employer") {
      newErrors.accountType = "Please select an account type";
    }
    if (!formData.firstName.trim()) {
      newErrors.firstName = "First name is required";
    }
    if (!formData.lastName.trim()) {
      newErrors.lastName = "Last name is required";
    }
    if (!formData.email.trim()) {
      newErrors.email = "Email address is required";
    } else {
      // More strict email validation to match backend EmailStr validation
      // EmailStr uses email-validator which is stricter than basic regex
      const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      if (!emailRegex.test(formData.email.trim())) {
        newErrors.email = "Please enter a valid email address";
      }
    }
    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters long";
    }
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }
    if (!formData.agreeToTerms) {
      newErrors.agreeToTerms = "You must agree to the Terms of Service";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = (): boolean => {
    const newErrors: FormErrors = {};

    if (!companyProfile.company_name.trim()) {
      newErrors.company_name = "Company name is required";
    }
    if (!companyProfile.description.trim()) {
      newErrors.description = "Company description is required";
    }
    if (!companyProfile.industry) {
      newErrors.industry = "Please select an industry";
    }
    if (!companyProfile.company_size) {
      newErrors.company_size = "Please select a company size";
    }
    if (!companyProfile.location.trim()) {
      newErrors.location = "Company location is required";
    }
    if (!companyProfile.job_title.trim()) {
      newErrors.job_title = "Your job title is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNextStep = (): void => {
    if (currentStep === 1) {
      if (validateStep1()) {
        if (formData.accountType === "employer") {
          setCurrentStep(2);
        } else {
          handleSubmit();
        }
      } else {
        setShowErrorToast(true);
        setTimeout(() => setShowErrorToast(false), 4000);
      }
    } else if (currentStep === 2) {
      if (validateStep2()) {
        handleSubmit();
      } else {
        setShowErrorToast(true);
        setTimeout(() => setShowErrorToast(false), 4000);
      }
    }
  };

  const handleSubmit = async (e?: React.FormEvent): Promise<void> => {
    // Prevent default form submission
    if (e) {
    e.preventDefault();
    }
    
    // Validate before submitting
    if (currentStep === 1 && !validateStep1()) {
      setShowErrorToast(true);
      setTimeout(() => setShowErrorToast(false), 4000);
      return;
    }
    if (currentStep === 2 && !validateStep2()) {
      setShowErrorToast(true);
      setTimeout(() => setShowErrorToast(false), 4000);
      return;
    }
    
    setIsSubmitting(true);
    try {
      const fullName = `${formData.firstName} ${formData.lastName}`.trim();
      const accountType =
        formData.accountType === "jobseeker" ? "job_seeker" : "employer";

      const registrationData = {
        email: formData.email.trim(),
        password: formData.password,
        account_type: accountType as "job_seeker" | "employer",
        full_name: fullName || null,
      };

      // Log registration data for debugging
      if (process.env.NODE_ENV === "development") {
        console.log("[Signup] Registration data:", {
          ...registrationData,
          password: "***hidden***",
        });
      }

      const response = await authApi.register(registrationData);

      // Check if email confirmation is required
      if ("email_confirmation_required" in response && response.email_confirmation_required) {
        // Show success message - email confirmation is required, not an error
        // Clear any field errors since registration was successful
        setErrors({});
        // Show info toast (we'll use the error toast styling but with a success message)
        // TODO: Create a separate success toast component for better UX
        setShowErrorToast(true);
        setTimeout(() => {
          setShowErrorToast(false);
          // Redirect to login page after showing message
          router.push("/login?message=Please check your email to confirm your account before logging in.");
        }, 6000);
        setIsSubmitting(false);
        return;
      }

      // If we got tokens, user is logged in - create profile and redirect
      if ("access_token" in response) {
        const user = response.user;
        const userId = user.id;

        try {
          // Create profile based on account type
          if (formData.accountType === "employer") {
            // Create employer profile with company information
            await api.employerProfiles.create({
              user_id: userId,
              company_name: companyProfile.company_name,
              description: companyProfile.description || null,
              location: companyProfile.location || null,
              industry: companyProfile.industry || null,
              company_size: companyProfile.company_size || null,
              contact_email: formData.email,
            });
          } else {
            // Create job seeker profile with name
            await api.jobSeekerProfiles.create({
              user_id: userId,
              first_name: formData.firstName,
              last_name: formData.lastName,
              email: formData.email,
            });
          }
        } catch (profileError) {
          // Log error but don't block redirect - profile can be created later
          console.error("Failed to create profile:", profileError);
          // Continue with redirect - user can complete profile later
        }

        // Redirect immediately to appropriate dashboard
        const redirectPath =
          formData.accountType === "employer"
            ? "/employer-dashboard"
            : "/dashboard";
        router.push(redirectPath);
      }
    } catch (error) {
      console.error("Registration error:", error);
      const apiError = error as ApiError;
      
      // Log detailed error information
      if (process.env.NODE_ENV === "development") {
        console.error("[Signup] API Error details:", {
          status: apiError.status,
          message: apiError.message,
          data: apiError.data,
        });
      }
      
      // Show user-friendly error message
      let errorMessage = "Registration failed. Please try again.";
      if (apiError.status === 400) {
        const errorDetail = apiError.data?.detail || apiError.message || "";
        const errorLower = errorDetail.toLowerCase();
        
        // Check if it's a rate limit error
        if (errorLower.includes("rate limit") || errorLower.includes("rate_limit")) {
          errorMessage = "Too many signup attempts. Please wait a few minutes and try again, or use a different email address.";
        }
        // Check if it's an email already exists error
        else if (errorLower.includes("already") || errorLower.includes("registered")) {
          errorMessage = "This email is already registered. Please use a different email or try logging in.";
        } 
        // Check if it's an email validation error
        else if (errorLower.includes("email") && (errorLower.includes("invalid") || errorLower.includes("value error"))) {
          errorMessage = "Please enter a valid email address. Some email formats (like aliases with +) may not be supported.";
        } 
        // Check if it's a password validation error
        else if (errorLower.includes("password") || errorLower.includes("length")) {
          errorMessage = "Password must be at least 8 characters long.";
        }
        // Use the backend error message if available
        else {
          errorMessage = errorDetail || apiError.message || errorMessage;
        }
      }
      
      setErrors({
        email: errorMessage,
      });
      setShowErrorToast(true);
      setTimeout(() => setShowErrorToast(false), 4000);
    } finally {
      setIsSubmitting(false);
    }
  };

  const goBackStep = (): void => {
    setCurrentStep(1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
        {/* Background decorative elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-green-200/20 rounded-full blur-3xl"></div>
          <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-amber-200/20 rounded-full blur-3xl"></div>
        </div>

      {/* Error Toast Notification */}
      {showErrorToast && Object.keys(errors).length > 0 && (
        <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 animate-slide-down">
          <div className="bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg">
            <span className="font-medium">
              Please fix {Object.keys(errors).length} issue
              {Object.keys(errors).length > 1 ? "s" : ""} above
            </span>
          </div>
        </div>
      )}
      
      {/* Success/Info Toast Notification (for email confirmation) */}
      {showErrorToast && Object.keys(errors).length === 0 && (
        <div className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 animate-slide-down">
          <div className="bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg">
            <span className="font-medium">
              Registration successful! Please check your email to confirm your account before logging in.
            </span>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8 relative z-10">
          {/* Progress Indicator for Employers */}
              {formData.accountType === "employer" && (
                <div className="flex items-center justify-center mb-6">
                  <div className="flex items-center space-x-4">
                    <div
                      className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all ${
                        currentStep >= 1
                          ? "bg-green-600 border-green-600 text-white shadow-lg"
                          : "border-green-300 text-green-500"
                      }`}
                    >
                      {currentStep > 1 ? <Check className="w-5 h-5" /> : "1"}
                    </div>
                    <div
                      className={`h-1 w-16 rounded-full transition-all ${
                        currentStep > 1 ? "bg-green-600" : "bg-green-200"
                      }`}
                    ></div>
                    <div
                      className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all ${
                        currentStep >= 2
                          ? "bg-green-600 border-green-600 text-white shadow-lg"
                          : "border-green-300 text-green-500"
                      }`}
                    >
                      2
                    </div>
                  </div>
                </div>
              )}

              {/* Page Header */}
          <div className="text-center">
                <h2 className="text-2xl font-bold text-green-900 mb-2">
                  {currentStep === 1
                    ? "Join Our Community"
                    : "Tell Us About Your Company"}
            </h2>
            <p className="text-green-700 mb-8">
                  {currentStep === 1
                    ? "Start cultivating a career that honors your whole self"
                    : "Help job seekers understand your culture and values"}
            </p>
          </div>

              {/* Form Card */}
              <form 
                onSubmit={(e) => {
                  e.preventDefault();
                  if (currentStep === 1) {
                    handleNextStep();
                  } else {
                    handleSubmit(e);
                  }
                }}
                className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg border border-green-200 p-8"
              >
                {/* Step 1: Basic Registration */}
                {currentStep === 1 && (
                  <div className="space-y-6">
              {/* Account Type Selection */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-3">
                        I&apos;m looking to... <span className="text-red-500">*</span>
                </label>
                      {errors.accountType && (
                        <p className="mb-2 text-sm text-red-600">
                          {errors.accountType}
                        </p>
                      )}
                <div className="grid grid-cols-2 gap-3">
                  <label
                    className={`relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      formData.accountType === "jobseeker"
                        ? "border-green-500 bg-gradient-to-br from-green-50 to-amber-50"
                        : "border-green-200 bg-white/50"
                    }`}
                  >
                    <input
                      type="radio"
                      name="accountType"
                      value="jobseeker"
                      checked={formData.accountType === "jobseeker"}
                      onChange={handleInputChange}
                      className="sr-only"
                    />
                          <div className="flex flex-col items-center text-center">
                      <User className="w-6 h-6 text-green-600 mb-2" />
                      <span className="font-medium text-green-800">
                        Find Work
                      </span>
                            <span className="text-xs text-green-600">
                              Job Seeker
                            </span>
                    </div>
                  </label>
                  <label
                    className={`relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      formData.accountType === "employer"
                        ? "border-green-500 bg-gradient-to-br from-green-50 to-amber-50"
                        : "border-green-200 bg-white/50"
                    }`}
                  >
                    <input
                      type="radio"
                      name="accountType"
                      value="employer"
                      checked={formData.accountType === "employer"}
                      onChange={handleInputChange}
                      className="sr-only"
                    />
                          <div className="flex flex-col items-center text-center">
                      <Users className="w-6 h-6 text-green-600 mb-2" />
                      <span className="font-medium text-green-800">
                        Hire Talent
                      </span>
                            <span className="text-xs text-green-600">
                              Employer
                            </span>
                    </div>
                  </label>
                </div>
              </div>

              {/* Name Fields */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-green-800 mb-2">
                          First Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    name="firstName"
                    type="text"
                    value={formData.firstName}
                    onChange={handleInputChange}
                          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all ${
                            errors.firstName
                              ? "border-red-500"
                              : "border-green-300"
                          }`}
                    placeholder="Your first name"
                    required
                  />
                        {errors.firstName && (
                          <p className="mt-1 text-sm text-red-600">
                            {errors.firstName}
                          </p>
                        )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-green-800 mb-2">
                          Last Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    name="lastName"
                    type="text"
                    value={formData.lastName}
                    onChange={handleInputChange}
                          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all ${
                            errors.lastName
                              ? "border-red-500"
                              : "border-green-300"
                          }`}
                    placeholder="Your last name"
                    required
                  />
                        {errors.lastName && (
                          <p className="mt-1 text-sm text-red-600">
                            {errors.lastName}
                          </p>
                        )}
                </div>
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                        Email Address <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <Mail className="h-5 w-5 text-green-400" />
                  </div>
                  <input
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                          className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all ${
                            errors.email
                              ? "border-red-500"
                              : "border-green-300"
                          }`}
                          placeholder="your.email@example.com"
                    required
                  />
                </div>
                      {errors.email && (
                        <p className="mt-1 text-sm text-red-600">
                          {errors.email}
                        </p>
                      )}
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                        Password <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <Lock className="h-5 w-5 text-green-400" />
                  </div>
                  <input
                    name="password"
                    type={showPassword ? "text" : "password"}
                    value={formData.password}
                    onChange={handleInputChange}
                          className={`w-full pl-10 pr-12 py-3 border rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all ${
                            errors.password
                              ? "border-red-500"
                              : "border-green-300"
                          }`}
                          placeholder="At least 8 characters"
                    required
                  />
                  <button
                    type="button"
                          onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    {showPassword ? (
                            <EyeOff className="h-5 w-5 text-green-500" />
                    ) : (
                            <Eye className="h-5 w-5 text-green-500" />
                    )}
                  </button>
                </div>
                      {errors.password && (
                        <p className="mt-1 text-sm text-red-600">
                          {errors.password}
                        </p>
                      )}
              </div>

              {/* Confirm Password */}
              <div>
                <label className="block text-sm font-medium text-green-800 mb-2">
                        Confirm Password <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <Lock className="h-5 w-5 text-green-400" />
                  </div>
                  <input
                    name="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                          className={`w-full pl-10 pr-12 py-3 border rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all ${
                            errors.confirmPassword
                              ? "border-red-500"
                              : "border-green-300"
                          }`}
                    placeholder="Confirm your password"
                    required
                  />
                  <button
                    type="button"
                          onClick={() =>
                            setShowConfirmPassword(!showConfirmPassword)
                          }
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    {showConfirmPassword ? (
                            <EyeOff className="h-5 w-5 text-green-500" />
                    ) : (
                            <Eye className="h-5 w-5 text-green-500" />
                    )}
                  </button>
                </div>
                      {errors.confirmPassword && (
                        <p className="mt-1 text-sm text-red-600">
                          {errors.confirmPassword}
                        </p>
                      )}
              </div>

                    {/* Terms Checkbox */}
                    <div>
                <label className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    name="agreeToTerms"
                    checked={formData.agreeToTerms}
                    onChange={handleInputChange}
                          className={`mt-1 w-4 h-4 text-green-600 rounded focus:ring-green-400 ${
                            errors.agreeToTerms
                              ? "border-red-500"
                              : "border-green-300"
                          }`}
                    required
                  />
                  <span className="text-sm text-green-700">
                    I agree to the{" "}
                          <button
                            type="button"
                      className="text-green-800 underline hover:text-green-900"
                    >
                      Terms of Service
                          </button>{" "}
                    and{" "}
                          <button
                            type="button"
                      className="text-green-800 underline hover:text-green-900"
                    >
                      Privacy Policy
                          </button>{" "}
                          <span className="text-red-500">*</span>
                        </span>
                      </label>
                      {errors.agreeToTerms && (
                        <p className="mt-1 text-sm text-red-600">
                          {errors.agreeToTerms}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Step 2: Company Profile (only for employers) */}
                {currentStep === 2 && formData.accountType === "employer" && (
                  <div className="space-y-6">
                    {/* Company Details */}
                    <div>
                      <label className="block text-sm font-medium text-green-800 mb-2">
                        Company Name
                      </label>
                      <input
                        type="text"
                        value={companyProfile.company_name}
                        onChange={(e) =>
                          handleCompanyProfileChange(
                            "company_name",
                            e.target.value
                          )
                        }
                        placeholder="Your Company Name"
                        className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all ${
                          errors.company_name
                            ? "border-red-500"
                            : "border-green-300"
                        }`}
                        required
                      />
                      {errors.company_name && (
                        <p className="mt-1 text-sm text-red-600">
                          {errors.company_name}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-green-800 mb-2">
                        Company Description <span className="text-red-500">*</span>
                      </label>
                      <textarea
                        value={companyProfile.description}
                        onChange={(e) =>
                          handleCompanyProfileChange(
                            "description",
                            e.target.value
                          )
                        }
                        placeholder="Tell us about your company mission, values, and what makes you unique..."
                        className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all min-h-[100px] resize-y ${
                          errors.description
                            ? "border-red-500"
                            : "border-green-300"
                        }`}
                        required
                      />
                      {errors.description && (
                        <p className="mt-1 text-sm text-red-600">
                          {errors.description}
                        </p>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-green-800 mb-2">
                          Industry <span className="text-red-500">*</span>
                        </label>
                        <select
                          value={companyProfile.industry}
                          onChange={(e) =>
                            handleCompanyProfileChange(
                              "industry",
                              e.target.value
                            )
                          }
                          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all ${
                            errors.industry
                              ? "border-red-500"
                              : "border-green-300"
                          }`}
                          required
                        >
                          <option value="">Select industry</option>
                          <option value="technology">Technology</option>
                          <option value="healthcare">Healthcare</option>
                          <option value="education">Education</option>
                          <option value="finance">Finance</option>
                          <option value="manufacturing">Manufacturing</option>
                          <option value="retail">Retail</option>
                          <option value="nonprofit">Non-Profit</option>
                          <option value="other">Other</option>
                        </select>
                        {errors.industry && (
                          <p className="mt-1 text-sm text-red-600">
                            {errors.industry}
                          </p>
                        )}
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-green-800 mb-2">
                          Company Size <span className="text-red-500">*</span>
                        </label>
                        <select
                          value={companyProfile.company_size}
                          onChange={(e) =>
                            handleCompanyProfileChange(
                              "company_size",
                              e.target.value
                            )
                          }
                          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all ${
                            errors.company_size
                              ? "border-red-500"
                              : "border-green-300"
                          }`}
                          required
                        >
                          <option value="">Select size</option>
                          <option value="startup">Startup (1-10)</option>
                          <option value="small">Small (11-50)</option>
                          <option value="medium">Medium (51-200)</option>
                          <option value="large">Large (201-1000)</option>
                          <option value="enterprise">Enterprise (1000+)</option>
                        </select>
                        {errors.company_size && (
                          <p className="mt-1 text-sm text-red-600">
                            {errors.company_size}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-green-800 mb-2">
                          Location <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={companyProfile.location}
                          onChange={(e) =>
                            handleCompanyProfileChange(
                              "location",
                              e.target.value
                            )
                          }
                          placeholder="City, State"
                          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all ${
                            errors.location
                              ? "border-red-500"
                              : "border-green-300"
                          }`}
                          required
                        />
                        {errors.location && (
                          <p className="mt-1 text-sm text-red-600">
                            {errors.location}
                          </p>
                        )}
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-green-800 mb-2">
                          Website
                        </label>
                        <input
                          type="url"
                          value={companyProfile.website}
                          onChange={(e) =>
                            handleCompanyProfileChange(
                              "website",
                              e.target.value
                            )
                          }
                          placeholder="https://yourcompany.com"
                          className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-green-800 mb-2">
                          Your Job Title <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={companyProfile.job_title}
                          onChange={(e) =>
                            handleCompanyProfileChange(
                              "job_title",
                              e.target.value
                            )
                          }
                          placeholder="e.g., HR Manager, Recruiter"
                          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all ${
                            errors.job_title
                              ? "border-red-500"
                              : "border-green-300"
                          }`}
                          required
                        />
                        {errors.job_title && (
                          <p className="mt-1 text-sm text-red-600">
                            {errors.job_title}
                          </p>
                        )}
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-green-800 mb-2">
                          Phone Number
                        </label>
                        <input
                          type="tel"
                          value={companyProfile.phone}
                          onChange={(e) =>
                            handleCompanyProfileChange("phone", e.target.value)
                          }
                          placeholder="+1 (555) 000-0000"
                          className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-green-800 mb-3">
                        Work Environment
                      </label>
                      <div className="flex flex-wrap gap-3">
                        {[
                          "collaborative",
                          "innovative",
                          "supportive",
                          "flexible",
                          "diverse",
                        ].map((env) => (
                          <label
                            key={env}
                            className="flex items-center space-x-2"
                          >
                            <input
                              type="checkbox"
                              checked={companyProfile.work_environment.includes(
                                env
                              )}
                              onChange={(e) =>
                                handleCheckboxChange(
                                  "work_environment",
                                  env,
                                  e.target.checked
                                )
                              }
                              className="w-4 h-4 text-green-600 border-green-300 rounded focus:ring-green-400"
                            />
                            <span className="text-sm text-green-700 capitalize">
                              {env}
                  </span>
                </label>
                        ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-green-800 mb-2">
                          Remote Work Policy
                        </label>
                        <select
                          value={companyProfile.remote_policy}
                          onChange={(e) =>
                            handleCompanyProfileChange(
                              "remote_policy",
                              e.target.value
                            )
                          }
                          className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all"
                        >
                          <option value="remote">Fully Remote</option>
                          <option value="hybrid">Hybrid</option>
                          <option value="onsite">On-Site</option>
                          <option value="flexible">Flexible</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-green-800 mb-2">
                          Founded Year
                        </label>
                        <input
                          type="number"
                          value={companyProfile.founded_year}
                          onChange={(e) =>
                            handleCompanyProfileChange(
                              "founded_year",
                              e.target.value
                            )
                          }
                          placeholder="2020"
                          min="1800"
                          max="2025"
                          className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 transition-all"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-green-800 mb-3">
                        Benefits & Perks
                      </label>
                      <div className="grid grid-cols-2 gap-3">
                        {[
                          { value: "health_insurance", label: "Health Insurance" },
                          { value: "dental", label: "Dental & Vision" },
                          { value: "401k", label: "401(k) Matching" },
                          { value: "pto", label: "Generous PTO" },
                          { value: "wellness", label: "Wellness Programs" },
                          {
                            value: "learning",
                            label: "Learning & Development",
                          },
                          { value: "equity", label: "Equity/Stock Options" },
                          { value: "parental", label: "Parental Leave" },
                        ].map((benefit) => (
                          <label
                            key={benefit.value}
                            className="flex items-center space-x-2"
                          >
                  <input
                    type="checkbox"
                              checked={companyProfile.benefits.includes(
                                benefit.value
                              )}
                              onChange={(e) =>
                                handleCheckboxChange(
                                  "benefits",
                                  benefit.value,
                                  e.target.checked
                                )
                              }
                              className="w-4 h-4 text-green-600 border-green-300 rounded focus:ring-green-400"
                  />
                  <span className="text-sm text-green-700">
                              {benefit.label}
                  </span>
                </label>
                        ))}
                      </div>
                    </div>
              </div>
                )}

                {/* Navigation Buttons */}
                <div className="pt-6">
                  <div className="flex justify-between items-center">
                    {currentStep > 1 && (
                      <button
                        type="button"
                        onClick={goBackStep}
                        className="flex items-center px-6 py-3 text-green-700 font-medium hover:text-green-800 transition-all"
                      >
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back
                      </button>
                    )}

              <button
                type="submit"
                      disabled={isSubmitting}
                      className={`flex items-center px-8 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white font-semibold rounded-lg hover:from-green-700 hover:to-green-800 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                        currentStep === 1 ? "ml-auto" : ""
                      }`}
              >
                <Heart className="w-5 h-5 mr-2" />
                      {currentStep === 1 && formData.accountType === "employer"
                        ? "Continue"
                        : "Join Career Harmony"}
                      {currentStep === 1 &&
                        formData.accountType === "employer" && (
                          <ArrowRight className="w-4 h-4 ml-2" />
                        )}
              </button>
                  </div>
                </div>
            </form>

            {/* Sign-in link */}
              <div className="text-center">
              <p className="text-sm text-green-700">
                Already have an account?{" "}
                <Link
                  href="/login"
                    className="text-green-800 underline hover:text-green-900 font-semibold"
                >
                  Sign in here
                </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
