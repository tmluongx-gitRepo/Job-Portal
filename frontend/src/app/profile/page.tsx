"use client";

import { useState, useEffect, type ReactElement } from "react";

import {
  User,
  Mail,
  Phone,
  MapPin,
  FileText,
  Upload,
  Edit3,
  Save,
  Check,
  Star,
  Briefcase,
  GraduationCap,
  Award,
  Heart,
  Zap,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import { api, ApiError, ValidationError } from "../../lib/api";
import type { JobSeekerProfile } from "../../lib/api";
import type { z } from "zod";

// TODO: Replace with API call to fetch user profile data
const initialProfileData = {
  firstName: "Alex",
  lastName: "Johnson",
  email: "alex.johnson@email.com",
  phone: "(555) 123-4567",
  location: "Phoenix, AZ",
  title: "Marketing Professional",
  summary:
    "Passionate marketing professional with 3+ years of experience in digital marketing, content creation, and customer engagement. I believe in building authentic connections between brands and their communities.",
  experience: [
    {
      company: "Digital Marketing Agency",
      role: "Marketing Coordinator",
      duration: "2022 - Present",
      description:
        "Managed social media campaigns, created content calendars, and increased client engagement by 40%.",
    },
  ],
  projects: [
    {
      title: "Community Food Drive Website",
      duration: "2023",
      description:
        "Built a website to coordinate local food donations, helping distribute over 500 meals to families in need.",
      technologies: "HTML, CSS, JavaScript",
    },
  ],
  education: [
    {
      school: "Arizona State University",
      degree: "Bachelor of Arts in Communications",
      year: "2022",
    },
  ],
  skills: [
    "Digital Marketing",
    "Content Creation",
    "Social Media Management",
    "Google Analytics",
    "Project Management",
  ],
};

const _completionItems = [
  {
    label: "Personal Information",
    completed: true,
    description: "Contact details and location",
  },
  {
    label: "Professional Summary",
    completed: true,
    description: "Brief overview of your experience",
  },
  {
    label: "Work Experience",
    completed: true,
    description: "Employment history and achievements",
  },
  {
    label: "Projects & Initiatives",
    completed: true,
    description: "Personal projects and volunteer work",
  },
  { label: "Education", completed: true, description: "Academic background" },
  {
    label: "Skills & Expertise",
    completed: true,
    description: "Technical and soft skills",
  },
  {
    label: "Resume Upload",
    completed: false,
    description: "Current resume document",
  },
];

export default function ProfilePage(): ReactElement {
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState(initialProfileData);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [profileId, setProfileId] = useState<string | null>(null);
  const [apiProfile, setApiProfile] = useState<JobSeekerProfile | null>(null);
  const [skillInputValue, setSkillInputValue] = useState("");

  // ⚠️ TODO: Replace with actual user ID from auth context when authentication is implemented
  // This should come from: useAuth() hook, session, or auth context
  // Example: const { user } = useAuth(); const userId = user?.id;
  // Note: Backend expects MongoDB ObjectId format (24 hex characters)
  // For testing, you can create a user via the API and use that user's ID
  const userId = "507f1f77bcf86cd799439011"; // PLACEHOLDER - Valid ObjectId format for testing

  // Fetch profile on mount
  useEffect(() => {
    const fetchProfile = async (): Promise<void> => {
      setLoading(true);
      setError(null);

      try {
        // Try to get profile by user ID
        const profile: JobSeekerProfile =
          (await api.jobSeekerProfiles.getByUserId(userId)) as JobSeekerProfile;
        setApiProfile(profile);
        setProfileId(profile.id);

        // Transform API profile to form format
        setProfileData({
          firstName: profile.first_name,
          lastName: profile.last_name,
          email: profile.email,
          phone: profile.phone || "",
          location: profile.location || "",
          title: "", // Not in API, could derive from bio
          summary: profile.bio || "",
          experience: [], // Not in API schema yet
          projects: [], // Not in API schema yet
          education: profile.education_level
            ? [
                {
                  school: "",
                  degree: profile.education_level,
                  year: "",
                },
              ]
            : [],
          skills: profile.skills || [],
        });
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) {
          // Profile doesn't exist yet - that's okay, user can create one
          // This is expected behavior, not an error
          console.info(
            "[Profile] No profile found for user - user can create one"
          );
          // Don't set error state - this is normal for new users
        } else {
          console.error("Failed to fetch profile:", err);
          setError("Failed to load profile. Please try again.");
        }
      } finally {
        setLoading(false);
      }
    };

    void fetchProfile();
  }, [userId]);

  // Dynamic completion tracking
  const completionItemsDynamic = [
    {
      label: "Personal Information",
      completed: !!(
        profileData.firstName &&
        profileData.lastName &&
        profileData.email
      ),
      description: "Contact details and location",
    },
    {
      label: "Professional Summary",
      completed: !!profileData.summary,
      description: "Brief overview of your experience",
    },
    {
      label: "Work Experience",
      completed: profileData.experience.length > 0,
      description: "Employment history and achievements",
    },
    {
      label: "Projects & Initiatives",
      completed: profileData.projects.length > 0,
      description: "Personal projects and volunteer work",
    },
    {
      label: "Education",
      completed: profileData.education.length > 0,
      description: "Academic background",
    },
    {
      label: "Skills & Expertise",
      completed: profileData.skills.length > 0,
      description: "Technical and soft skills",
    },
    {
      label: "Resume Upload",
      completed: false, // TODO: Track resume upload
      description: "Current resume document",
    },
  ];

  const completedCount = completionItemsDynamic.filter(
    (item) => item.completed
  ).length;
  const completionPercentage = apiProfile?.profile_completion_percentage
    ? apiProfile.profile_completion_percentage
    : Math.round((completedCount / completionItemsDynamic.length) * 100);

  const handleInputChange = (field: string, value: string): void => {
    setProfileData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const addExperience = (): void => {
    setProfileData((prev) => ({
      ...prev,
      experience: [
        ...prev.experience,
        { company: "", role: "", duration: "", description: "" },
      ],
    }));
  };

  const updateExperience = (
    index: number,
    field: string,
    value: string
  ): void => {
    setProfileData((prev) => ({
      ...prev,
      experience: prev.experience.map((exp, i) =>
        i === index ? { ...exp, [field]: value } : exp
      ),
    }));
  };

  const removeExperience = (index: number): void => {
    setProfileData((prev) => ({
      ...prev,
      experience: prev.experience.filter((_, i) => i !== index),
    }));
  };

  const addEducation = (): void => {
    setProfileData((prev) => ({
      ...prev,
      education: [...prev.education, { school: "", degree: "", year: "" }],
    }));
  };

  const updateEducation = (
    index: number,
    field: string,
    value: string
  ): void => {
    setProfileData((prev) => ({
      ...prev,
      education: prev.education.map((edu, i) =>
        i === index ? { ...edu, [field]: value } : edu
      ),
    }));
  };

  const removeEducation = (index: number): void => {
    setProfileData((prev) => ({
      ...prev,
      education: prev.education.filter((_, i) => i !== index),
    }));
  };

  const addProject = (): void => {
    setProfileData((prev) => ({
      ...prev,
      projects: [
        ...prev.projects,
        { title: "", duration: "", description: "", technologies: "" },
      ],
    }));
  };

  const updateProject = (index: number, field: string, value: string): void => {
    setProfileData((prev) => ({
      ...prev,
      projects: prev.projects.map((project, i) =>
        i === index ? { ...project, [field]: value } : project
      ),
    }));
  };

  const removeProject = (index: number): void => {
    setProfileData((prev) => ({
      ...prev,
      projects: prev.projects.filter((_, i) => i !== index),
    }));
  };

  const addSkill = (skill: string): void => {
    if (skill.trim() && !profileData.skills.includes(skill.trim())) {
      setProfileData((prev) => ({
        ...prev,
        skills: [...prev.skills, skill.trim()],
      }));
    }
  };

  const removeSkill = (skillToRemove: string): void => {
    setProfileData((prev) => ({
      ...prev,
      skills: prev.skills.filter((skill) => skill !== skillToRemove),
    }));
  };

  const handleSave = async (): Promise<void> => {
    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      const updateData = {
        first_name: profileData.firstName,
        last_name: profileData.lastName,
        email: profileData.email,
        phone: profileData.phone || null,
        location: profileData.location || null,
        bio: profileData.summary || null,
        skills: profileData.skills,
        education_level:
          profileData.education.length > 0
            ? profileData.education[0].degree
            : null,
        // Note: experience, projects not in API schema yet
        // Could store in bio or add to schema later
      };

      if (profileId) {
        // Update existing profile
        const updated = await api.jobSeekerProfiles.update(
          profileId,
          updateData
        );
        setApiProfile(updated);
        setSuccess(true);
      } else {
        // Create new profile
        const created: JobSeekerProfile = (await api.jobSeekerProfiles.create({
          ...updateData,
          user_id: userId,
        })) as JobSeekerProfile;
        setApiProfile(created);
        setProfileId(created.id);
        setSuccess(true);
      }

      setIsEditing(false);

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error("Failed to save profile:", err);
      if (err instanceof ValidationError) {
        const errorMessages = err.issues.map((issue: z.ZodIssue) => {
          const field = issue.path.join(".");
          return `${field}: ${issue.message}`;
        });
        setError(`Validation error: ${errorMessages.join(", ")}`);
      } else if (err instanceof ApiError) {
        if (err.status === 403) {
          setError(
            "Authentication required to save profile. Please log in to save your changes."
          );
        } else {
          setError(`Failed to save profile: ${err.message}`);
        }
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-green-900 mb-2">
              Your Profile
            </h1>
            <p className="text-green-700">
              Tell your professional story with confidence
            </p>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex items-center text-green-600">
              <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
              <span>Loading profile...</span>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4 flex items-start">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4 flex items-start">
              <Check className="w-5 h-5 text-green-600 mr-2 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-green-800">
                Profile saved successfully!
              </p>
            </div>
          )}
          <button
            onClick={() => {
              if (isEditing) {
                void handleSave();
              } else {
                setIsEditing(true);
              }
            }}
            disabled={loading || saving}
            className="bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? (
              <>
                <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                Saving...
              </>
            ) : isEditing ? (
              <>
                <Save className="w-5 h-5 mr-2" />
                Save Changes
              </>
            ) : (
              <>
                <Edit3 className="w-5 h-5 mr-2" />
                Edit Profile
              </>
            )}
          </button>
        </div>

        {loading ? (
          <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-12 text-center">
            <RefreshCw className="w-8 h-8 text-green-600 animate-spin mx-auto mb-4" />
            <p className="text-green-700">Loading profile...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column - Profile Completion */}
            <div className="lg:col-span-1 space-y-6">
              {/* Profile Completion Card */}
              <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-green-800">
                    Profile Strength
                  </h3>
                  <span className="text-2xl font-bold text-green-900">
                    {completionPercentage}%
                  </span>
                </div>

                <div className="w-full bg-green-100 rounded-full h-3 mb-6">
                  <div
                    className="bg-gradient-to-r from-green-500 to-green-600 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${completionPercentage}%` }}
                  ></div>
                </div>

                <div className="space-y-3">
                  {completionItemsDynamic.map((item, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div
                        className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center mt-0.5 ${
                          item.completed ? "bg-green-500" : "bg-gray-200"
                        }`}
                      >
                        {item.completed && (
                          <Check className="w-3 h-3 text-white" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p
                          className={`text-sm font-medium ${item.completed ? "text-green-800" : "text-gray-600"}`}
                        >
                          {item.label}
                        </p>
                        <p className="text-xs text-green-600">
                          {item.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-amber-50 rounded-lg border border-green-200">
                  <div className="flex items-center mb-2">
                    <Heart className="w-4 h-4 text-green-600 mr-2" />
                    <span className="font-medium text-green-800">
                      You&apos;re doing great!
                    </span>
                  </div>
                  <p className="text-sm text-green-700">
                    Adding a resume will help employers get to know
                    the amazing professional you are.
                  </p>
                </div>
              </div>

              {/* Resume Upload Card */}
              <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
                <h3 className="text-lg font-semibold text-green-800 mb-4 flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Resume
                </h3>

                <div className="border-2 border-dashed border-green-300 rounded-lg p-6 text-center hover:border-green-400 transition-colors">
                  <Upload className="w-8 h-8 text-green-500 mx-auto mb-3" />
                  <p className="text-sm font-medium text-green-800 mb-1">
                    Upload your resume
                  </p>
                  <p className="text-xs text-green-600 mb-4">
                    PDF, DOC, or DOCX files accepted
                  </p>
                  <button className="bg-yellow-100 text-green-700 border border-green-300 px-4 py-2 rounded-lg font-medium hover:bg-yellow-200 transition-all text-sm">
                    Choose File
                  </button>
                </div>

                <p className="text-xs text-green-600 mt-3">
                  <span className="font-medium">Tip:</span> A well-formatted
                  resume helps employers quickly understand your experience and
                  achievements.
                </p>
              </div>
            </div>

            {/* Right Column - Profile Details */}
            <div className="lg:col-span-2 space-y-6">
              {/* Personal Information */}
              <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-green-900 flex items-center">
                    <User className="w-6 h-6 mr-2" />
                    Personal Information
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-green-800 mb-2">
                      First Name
                    </label>
                    {isEditing ? (
                      <input
                        type="text"
                        value={profileData.firstName}
                        onChange={(e) =>
                          handleInputChange("firstName", e.target.value)
                        }
                        className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                      />
                    ) : (
                      <p className="px-4 py-3 bg-green-50 border border-green-200 rounded-lg text-green-900">
                        {profileData.firstName}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-green-800 mb-2">
                      Last Name
                    </label>
                    {isEditing ? (
                      <input
                        type="text"
                        value={profileData.lastName}
                        onChange={(e) =>
                          handleInputChange("lastName", e.target.value)
                        }
                        className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                      />
                    ) : (
                      <p className="px-4 py-3 bg-green-50 border border-green-200 rounded-lg text-green-900">
                        {profileData.lastName}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="text-sm font-medium text-green-800 mb-2 flex items-center">
                      <Mail className="w-4 h-4 mr-1" />
                      Email
                    </label>
                    {isEditing ? (
                      <input
                        type="email"
                        value={profileData.email}
                        onChange={(e) =>
                          handleInputChange("email", e.target.value)
                        }
                        className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                      />
                    ) : (
                      <p className="px-4 py-3 bg-green-50 border border-green-200 rounded-lg text-green-900">
                        {profileData.email}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="text-sm font-medium text-green-800 mb-2 flex items-center">
                      <Phone className="w-4 h-4 mr-1" />
                      Phone
                    </label>
                    {isEditing ? (
                      <input
                        type="tel"
                        value={profileData.phone}
                        onChange={(e) =>
                          handleInputChange("phone", e.target.value)
                        }
                        className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                      />
                    ) : (
                      <p className="px-4 py-3 bg-green-50 border border-green-200 rounded-lg text-green-900">
                        {profileData.phone}
                      </p>
                    )}
                  </div>

                  <div className="md:col-span-2">
                    <label className="text-sm font-medium text-green-800 mb-2 flex items-center">
                      <MapPin className="w-4 h-4 mr-1" />
                      Location
                    </label>
                    {isEditing ? (
                      <input
                        type="text"
                        value={profileData.location}
                        onChange={(e) =>
                          handleInputChange("location", e.target.value)
                        }
                        className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                        placeholder="City, State"
                      />
                    ) : (
                      <p className="px-4 py-3 bg-green-50 border border-green-200 rounded-lg text-green-900">
                        {profileData.location}
                      </p>
                    )}
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-green-800 mb-2">
                      Professional Title
                    </label>
                    {isEditing ? (
                      <input
                        type="text"
                        value={profileData.title}
                        onChange={(e) =>
                          handleInputChange("title", e.target.value)
                        }
                        className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                        placeholder="e.g. Marketing Professional"
                      />
                    ) : (
                      <p className="px-4 py-3 bg-green-50 border border-green-200 rounded-lg text-green-900">
                        {profileData.title || "Not specified"}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Professional Summary */}
              <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
                <h3 className="text-xl font-bold text-green-900 mb-4 flex items-center">
                  <Star className="w-6 h-6 mr-2" />
                  Professional Summary
                </h3>

                <div>
                  <label className="block text-sm font-medium text-green-800 mb-2">
                    Tell employers what makes you unique
                  </label>
                  {isEditing ? (
                    <textarea
                      value={profileData.summary}
                      onChange={(e) =>
                        handleInputChange("summary", e.target.value)
                      }
                      rows={4}
                      className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                      placeholder="Share your professional story, key strengths, and career goals..."
                    />
                  ) : (
                    <p className="px-4 py-3 bg-green-50 border border-green-200 rounded-lg text-green-900 leading-relaxed">
                      {profileData.summary}
                    </p>
                  )}
                  <p className="text-xs text-green-600 mt-2">
                    <span className="font-medium">Tip:</span> Focus on your
                    strengths, achievements, and what you are passionate about
                    in your career.
                  </p>
                </div>
              </div>

              {/* Experience */}
              <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-green-900 flex items-center">
                    <Briefcase className="w-6 h-6 mr-2" />
                    Work Experience
                  </h3>
                  {isEditing && (
                    <button
                      onClick={addExperience}
                      className="text-green-600 hover:text-green-800 text-sm font-medium"
                    >
                      + Add Experience
                    </button>
                  )}
                </div>

                <div className="space-y-6">
                  {profileData.experience.map((exp, index) => (
                    <div
                      key={index}
                      className="border-l-4 border-green-200 pl-6 pb-6"
                    >
                      {isEditing ? (
                        <div className="space-y-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <input
                              type="text"
                              value={exp.role}
                              onChange={(e) =>
                                updateExperience(index, "role", e.target.value)
                              }
                              placeholder="Job Title"
                              className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                            />
                            <input
                              type="text"
                              value={exp.company}
                              onChange={(e) =>
                                updateExperience(
                                  index,
                                  "company",
                                  e.target.value
                                )
                              }
                              placeholder="Company Name"
                              className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                            />
                          </div>
                          <input
                            type="text"
                            value={exp.duration}
                            onChange={(e) =>
                              updateExperience(
                                index,
                                "duration",
                                e.target.value
                              )
                            }
                            placeholder="Duration (e.g., 2022 - Present)"
                            className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                          />
                          <textarea
                            value={exp.description}
                            onChange={(e) =>
                              updateExperience(
                                index,
                                "description",
                                e.target.value
                              )
                            }
                            placeholder="Describe your key responsibilities and achievements..."
                            rows={3}
                            className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 resize-none"
                          />
                          <button
                            onClick={() => removeExperience(index)}
                            className="text-red-500 text-sm hover:text-red-700"
                          >
                            Remove
                          </button>
                        </div>
                      ) : (
                        <div>
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h4 className="text-lg font-semibold text-green-800">
                                {exp.role || "Untitled Position"}
                              </h4>
                              <p className="text-green-700">
                                {exp.company || "Company not specified"}
                              </p>
                            </div>
                            {exp.duration && (
                              <span className="text-sm text-green-600 bg-green-100 px-3 py-1 rounded-full">
                                {exp.duration}
                              </span>
                            )}
                          </div>
                          {exp.description && (
                            <p className="text-green-700 text-sm leading-relaxed">
                              {exp.description}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                  {profileData.experience.length === 0 && !isEditing && (
                    <p className="text-gray-500 text-center py-4">
                      No work experience added yet
                    </p>
                  )}
                </div>
              </div>

              {/* Education */}
              <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-green-900 flex items-center">
                    <GraduationCap className="w-6 h-6 mr-2" />
                    Education
                  </h3>
                  {isEditing && (
                    <button
                      onClick={addEducation}
                      className="text-green-600 hover:text-green-800 text-sm font-medium"
                    >
                      + Add Education
                    </button>
                  )}
                </div>

                <div className="space-y-6">
                  {profileData.education.map((edu, index) => (
                    <div
                      key={index}
                      className="border-l-4 border-green-200 pl-6 pb-6"
                    >
                      {isEditing ? (
                        <div className="space-y-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <input
                              type="text"
                              value={edu.school}
                              onChange={(e) =>
                                updateEducation(index, "school", e.target.value)
                              }
                              placeholder="School/University Name"
                              className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                            />
                            <input
                              type="text"
                              value={edu.degree}
                              onChange={(e) =>
                                updateEducation(index, "degree", e.target.value)
                              }
                              placeholder="Degree & Major"
                              className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                            />
                          </div>
                          <input
                            type="text"
                            value={edu.year}
                            onChange={(e) =>
                              updateEducation(index, "year", e.target.value)
                            }
                            placeholder="Years (e.g., 2018-2022)"
                            className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                          />
                          <button
                            onClick={() => removeEducation(index)}
                            className="text-red-500 text-sm hover:text-red-700"
                          >
                            Remove
                          </button>
                        </div>
                      ) : (
                        <div>
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h4 className="text-lg font-semibold text-green-800">
                                {edu.degree || "Degree not specified"}
                              </h4>
                              <p className="text-green-700 text-sm">
                                {edu.school || "School not specified"}
                              </p>
                            </div>
                            {edu.year && (
                              <span className="text-sm text-green-600 bg-green-100 px-3 py-1 rounded-full">
                                {edu.year}
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                  {profileData.education.length === 0 && !isEditing && (
                    <p className="text-gray-500 text-center py-4">
                      No education information added yet
                    </p>
                  )}
                </div>
              </div>

              {/* Projects */}
              <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-green-900 flex items-center">
                    <Zap className="w-6 h-6 mr-2" />
                    Projects
                  </h3>
                  {isEditing && (
                    <button
                      onClick={addProject}
                      className="text-green-600 hover:text-green-800 text-sm font-medium"
                    >
                      + Add Project
                    </button>
                  )}
                </div>

                <div className="space-y-6">
                  {profileData.projects.map((project, index) => (
                    <div
                      key={index}
                      className="border-l-4 border-green-200 pl-6 pb-6"
                    >
                      {isEditing ? (
                        <div className="space-y-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <input
                              type="text"
                              value={project.title}
                              onChange={(e) =>
                                updateProject(index, "title", e.target.value)
                              }
                              placeholder="Project Title"
                              className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                            />
                            <input
                              type="text"
                              value={project.duration}
                              onChange={(e) =>
                                updateProject(index, "duration", e.target.value)
                              }
                              placeholder="Timeline (e.g., 2023)"
                              className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                            />
                          </div>
                          <textarea
                            value={project.description}
                            onChange={(e) =>
                              updateProject(
                                index,
                                "description",
                                e.target.value
                              )
                            }
                            placeholder="Describe the project and your achievements..."
                            rows={3}
                            className="w-full px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80 resize-none"
                          />
                          <button
                            onClick={() => removeProject(index)}
                            className="text-red-500 text-sm hover:text-red-700"
                          >
                            Remove
                          </button>
                        </div>
                      ) : (
                        <div>
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h4 className="text-lg font-semibold text-green-800">
                                {project.title || "Untitled Project"}
                              </h4>
                              {project.technologies && (
                                <p className="text-green-600 text-sm">
                                  Technologies: {project.technologies}
                                </p>
                              )}
                            </div>
                            {project.duration && (
                              <span className="text-sm text-green-600 bg-green-100 px-3 py-1 rounded-full">
                                {project.duration}
                              </span>
                            )}
                          </div>
                          {project.description && (
                            <p className="text-green-700 text-sm leading-relaxed">
                              {project.description}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                  {profileData.projects.length === 0 && !isEditing && (
                    <p className="text-gray-500 text-center py-4">
                      No projects added yet
                    </p>
                  )}
                </div>
              </div>

              {/* Skills */}
              <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
                <h3 className="text-xl font-bold text-green-900 mb-4 flex items-center">
                  <Award className="w-6 h-6 mr-2" />
                  Key Skills
                </h3>

                <div className="flex flex-wrap gap-2 mb-4">
                  {profileData.skills.map((skill, index) => (
                    <span
                      key={index}
                      className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm border border-green-200 flex items-center"
                    >
                      {skill}
                      {isEditing && (
                        <button
                          onClick={() => removeSkill(skill)}
                          className="ml-2 text-green-600 hover:text-green-800"
                        >
                          ×
                        </button>
                      )}
                    </span>
                  ))}
                </div>

                {isEditing && (
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={skillInputValue}
                      onChange={(e) => setSkillInputValue(e.target.value)}
                      placeholder="Add a skill"
                      className="flex-1 px-4 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent bg-white/80"
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && skillInputValue.trim()) {
                          e.preventDefault();
                          addSkill(skillInputValue);
                          setSkillInputValue("");
                        }
                      }}
                    />
                    <button
                      onClick={() => {
                        if (skillInputValue.trim()) {
                          addSkill(skillInputValue);
                          setSkillInputValue("");
                        }
                      }}
                      className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-all text-sm"
                    >
                      Add Skills
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
