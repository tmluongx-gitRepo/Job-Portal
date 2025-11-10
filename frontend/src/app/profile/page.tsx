"use client";

import { useState, type ReactElement } from "react";

import {
  User,
  Mail,
  Phone,
  MapPin,
  FileText,
  Upload,
  Camera,
  Edit3,
  Save,
  Check,
  Star,
  Briefcase,
  GraduationCap,
  Award,
  Heart,
  Zap,
} from "lucide-react";

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

const completionItems = [
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
  {
    label: "Profile Photo",
    completed: false,
    description: "Professional headshot",
  },
];

export default function ProfilePage(): ReactElement {
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState(initialProfileData);

  const completedCount = completionItems.filter(
    (item) => item.completed
  ).length;
  const completionPercentage = Math.round(
    (completedCount / completionItems.length) * 100
  );

  const handleInputChange = (field: string, value: string): void => {
    setProfileData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSave = (): void => {
    // TODO: Implement API call to save profile data
    console.log("Saving profile:", profileData);
    setIsEditing(false);
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
          <button
            onClick={() => (isEditing ? handleSave() : setIsEditing(true))}
            className="bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all flex items-center"
          >
            {isEditing ? (
              <Save className="w-5 h-5 mr-2" />
            ) : (
              <Edit3 className="w-5 h-5 mr-2" />
            )}
            {isEditing ? "Save Changes" : "Edit Profile"}
          </button>
        </div>

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
                {completionItems.map((item, index) => (
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
                  Adding a resume and photo will help employers get to know the
                  amazing professional you are.
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

                {/* Profile Photo */}
                <div className="relative">
                  <div className="w-16 h-16 bg-gradient-to-r from-green-100 to-amber-100 rounded-full flex items-center justify-center">
                    <User className="w-8 h-8 text-green-600" />
                  </div>
                  <button className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center hover:bg-green-600 transition-colors">
                    <Camera className="w-3 h-3 text-white" />
                  </button>
                </div>
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
                  <label className="block text-sm font-medium text-green-800 mb-2 flex items-center">
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
                  <label className="block text-sm font-medium text-green-800 mb-2 flex items-center">
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
                  <label className="block text-sm font-medium text-green-800 mb-2 flex items-center">
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
                  strengths, achievements, and what you are passionate about in
                  your career.
                </p>
              </div>
            </div>

            {/* Projects & Initiatives */}
            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
              <h3 className="text-xl font-bold text-green-900 mb-4 flex items-center">
                <Zap className="w-6 h-6 mr-2" />
                Projects & Initiatives
              </h3>

              {profileData.projects.map((project, index) => (
                <div
                  key={index}
                  className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-semibold text-green-900">
                        {project.title}
                      </h4>
                      {project.technologies && (
                        <p className="text-green-600 text-sm">
                          Technologies: {project.technologies}
                        </p>
                      )}
                    </div>
                    <span className="text-sm text-green-600">
                      {project.duration}
                    </span>
                  </div>
                  <p className="text-green-800 text-sm">
                    {project.description}
                  </p>
                </div>
              ))}

              <button className="w-full bg-yellow-100 text-green-700 border border-green-300 py-3 rounded-lg font-medium hover:bg-yellow-200 transition-all flex items-center justify-center">
                <Zap className="w-4 h-4 mr-2" />
                Add Project
              </button>

              <p className="text-xs text-green-600 mt-3">
                <span className="font-medium">Showcase your impact:</span>{" "}
                Include volunteer work, personal projects, community
                initiatives, or creative endeavors that demonstrate your skills
                and values.
              </p>
            </div>

            {/* Experience */}
            <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
              <h3 className="text-xl font-bold text-green-900 mb-4 flex items-center">
                <Briefcase className="w-6 h-6 mr-2" />
                Work Experience
              </h3>

              {profileData.experience.map((exp, index) => (
                <div
                  key={index}
                  className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-semibold text-green-900">
                        {exp.role}
                      </h4>
                      <p className="text-green-700">{exp.company}</p>
                    </div>
                    <span className="text-sm text-green-600">
                      {exp.duration}
                    </span>
                  </div>
                  <p className="text-green-800 text-sm">{exp.description}</p>
                </div>
              ))}

              <button className="w-full bg-yellow-100 text-green-700 border border-green-300 py-3 rounded-lg font-medium hover:bg-yellow-200 transition-all flex items-center justify-center">
                <Briefcase className="w-4 h-4 mr-2" />
                Add Experience
              </button>
            </div>

            {/* Education & Skills */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
                <h3 className="text-lg font-bold text-green-900 mb-4 flex items-center">
                  <GraduationCap className="w-5 h-5 mr-2" />
                  Education
                </h3>

                {profileData.education.map((edu, index) => (
                  <div
                    key={index}
                    className="bg-green-50 border border-green-200 rounded-lg p-4 mb-3"
                  >
                    <h4 className="font-semibold text-green-900">
                      {edu.degree}
                    </h4>
                    <p className="text-green-700 text-sm">{edu.school}</p>
                    <p className="text-green-600 text-sm">{edu.year}</p>
                  </div>
                ))}
              </div>

              <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
                <h3 className="text-lg font-bold text-green-900 mb-4 flex items-center">
                  <Award className="w-5 h-5 mr-2" />
                  Skills
                </h3>

                <div className="flex flex-wrap gap-2 mb-4">
                  {profileData.skills.map((skill, index) => (
                    <span
                      key={index}
                      className="bg-yellow-50 text-green-800 px-3 py-1 rounded-full text-sm border border-green-200"
                    >
                      {skill}
                    </span>
                  ))}
                </div>

                <button className="w-full bg-yellow-100 text-green-700 border border-green-300 py-2 rounded-lg font-medium hover:bg-yellow-200 transition-all text-sm">
                  Add Skills
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
