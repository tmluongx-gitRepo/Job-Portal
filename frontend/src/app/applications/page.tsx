"use client";

import { useState, type ReactElement } from "react";

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
} from "lucide-react";

// TODO: Replace with API call to fetch job info
const jobInfo = {
  title: "Marketing Coordinator",
  company: "TechFlow Solutions",
  location: "Phoenix, AZ",
  type: "Full-time",
  posted: "2 weeks ago",
  salary: "$45,000 - $55,000",
};

// TODO: Replace with API call to fetch applicants
const sampleApplicants = [
  {
    id: 1,
    name: "Sarah Chen",
    email: "sarah.chen@email.com",
    phone: "(555) 123-4567",
    location: "Phoenix, AZ",
    appliedDate: "2024-11-01",
    status: "unreviewed",
    experience: "3 years",
    education: "Bachelor's in Marketing",
    currentRole: "Marketing Assistant at Creative Agency",
    skills: [
      "Social Media Marketing",
      "Content Creation",
      "Adobe Creative Suite",
      "Google Analytics",
      "Email Marketing",
      "Brand Strategy",
      "Copywriting",
      "Photoshop",
      "Video Editing",
      "SEO Optimization",
    ],
    resumeUrl: "/resumes/sarah-chen.pdf",
    coverLetterExcerpt:
      "I&apos;m excited to bring my creative marketing experience to TechFlow Solutions...",
    matchScore: 92,
    volunteerWork: [
      "Local Animal Shelter - Marketing Volunteer (2+ years): Created social media campaigns that increased adoptions by 40%",
      "Community Garden Coordinator - Phoenix Urban Farm (1 year): Organized events and managed Instagram account",
      "Habitat for Humanity - Communications Team (6 months): Designed promotional materials for fundraising events",
      "Arizona Food Bank - Marketing Assistant (1 year): Developed email campaigns reaching 5,000+ donors",
      "Local Library Reading Program - Social Media Manager (8 months): Grew followers from 200 to 1,500",
      "Youth Mentorship Program - Workshop Leader (2 years): Taught digital marketing skills to high school students",
      "Environmental Coalition - Graphic Designer (1 year): Created awareness campaigns for sustainability initiatives",
    ],
    personalProjects: [
      "Sustainable Living Blog (2022-present): Built Instagram account from 0 to 12K followers focused on eco-friendly lifestyle tips",
      "Freelance Graphic Design Business: Created brand identities for 15+ local small businesses",
      "Community Art Festival Website: Designed and developed responsive website that increased ticket sales by 60%",
      "Photography Portfolio: Self-taught photographer with work featured in 3 local exhibitions",
      'Podcast "Creative Minds" (2023): Interviewed 25+ local artists and entrepreneurs, 2K+ monthly downloads',
      "Volunteer Coordination App: Developed mobile app prototype to streamline volunteer scheduling for nonprofits",
    ],
  },
  {
    id: 2,
    name: "Marcus Rodriguez",
    email: "marcus.r@email.com",
    phone: "(555) 987-6543",
    location: "Scottsdale, AZ",
    appliedDate: "2024-10-30",
    status: "reviewed",
    experience: "5 years",
    education: "MBA in Marketing",
    currentRole: "Senior Marketing Specialist at Digital Corp",
    skills: [
      "Campaign Management",
      "Data Analysis",
      "Brand Strategy",
      "SEO/SEM",
      "Marketing Automation",
      "A/B Testing",
      "Customer Segmentation",
      "CRM Management",
      "Lead Generation",
      "Conversion Optimization",
      "Google Ads",
      "Facebook Ads",
    ],
    resumeUrl: "/resumes/marcus-rodriguez.pdf",
    coverLetterExcerpt:
      "With my extensive background in digital marketing campaigns...",
    matchScore: 88,
    volunteerWork: [
      "St. Mary's Food Bank - Digital Marketing Lead (3 years): Increased online donations by 150% through targeted campaigns",
      "Big Brothers Big Sisters - Mentorship Program (2 years): Mentored at-risk youth in business and technology skills",
      "Phoenix Children's Hospital - Fundraising Committee (1 year): Organized charity events raising $50K+ annually",
      "Local Chamber of Commerce - Marketing Advisory Board (2 years): Provided pro-bono marketing consulting for small businesses",
      "Arizona Hispanic Chamber - Bilingual Marketing Volunteer (18 months): Developed Spanish-language marketing materials",
      "United Way Campaign - Team Leader (1 year): Led workplace giving campaign exceeding goals by 25%",
    ],
    personalProjects: [
      "Marketing Automation Consultancy: Built SaaS tool helping small businesses automate email sequences, 50+ clients",
      "Data Visualization Dashboard: Created real-time analytics platform used by 3 local marketing agencies",
      "Spanish-English Marketing Blog: Educational content reaching 5K+ monthly readers in Latino business community",
      "E-commerce Store Analytics: Developed custom Google Analytics setup increasing client conversion rates by 35%",
      "Local Restaurant Marketing Case Study: Volunteer project that tripled social media engagement in 6 months",
      'Marketing Podcast Co-host: "Digital Marketing Decoded" with 10K+ monthly downloads and 50+ episodes',
      "AI Marketing Tools Research: Testing and reviewing emerging AI tools, findings shared with 2K+ LinkedIn followers",
    ],
  },
  {
    id: 3,
    name: "Emily Thompson",
    email: "emily.thompson@email.com",
    phone: "(555) 456-7890",
    location: "Tempe, AZ",
    appliedDate: "2024-10-29",
    status: "shortlisted",
    experience: "2 years",
    education: "Bachelor's in Communications",
    currentRole: "Junior Marketing Coordinator at StartupCo",
    skills: [
      "Email Marketing",
      "Social Media Management",
      "Event Planning",
      "Content Writing",
      "Customer Service",
      "Project Management",
      "Canva Design",
      "WordPress",
      "Mailchimp",
      "Hootsuite",
      "Google Workspace",
    ],
    resumeUrl: "/resumes/emily-thompson.pdf",
    coverLetterExcerpt:
      "I would love to contribute my enthusiasm and fresh perspective...",
    matchScore: 85,
    volunteerWork: [
      "Youth Mentorship Program - Program Coordinator (3 years): Organized workshops for 100+ high school students annually",
      "Tempe Arts Festival - Marketing Committee (2 years): Managed social media and increased attendance by 30%",
      "Local Women's Shelter - Communications Volunteer (18 months): Created awareness campaigns and donor newsletters",
      "Environmental Club - Events Manager (1 year): Planned sustainability workshops and community clean-up events",
      "Animal Rescue Network - Social Media Coordinator (2 years): Managed adoption campaigns and fundraising events",
      "Senior Center - Technology Instructor (1 year): Taught social media and digital communication skills to seniors",
      "Food Distribution Center - Volunteer Coordinator (6 months): Organized weekly volunteer schedules for 40+ people",
    ],
    personalProjects: [
      'Sustainable Living Blog "Green Valley Life": 500+ posts about eco-friendly practices, 3K+ monthly readers',
      "Community Cleanup Initiative: Organized monthly neighborhood cleanups, removed 2 tons of trash in 2023",
      "Local Business Directory Website: Built WordPress site featuring 200+ Tempe small businesses",
      "Digital Scrapbooking Service: Helped 30+ families create digital photo albums and memory books",
      "Farmers Market Social Media: Volunteer social media manager increasing vendor participation by 45%",
      "Personal Finance Workshop Series: Created and taught budgeting workshops for young adults at community center",
    ],
  },
  {
    id: 4,
    name: "David Kim",
    email: "david.kim@email.com",
    phone: "(555) 321-0987",
    location: "Phoenix, AZ",
    appliedDate: "2024-10-28",
    status: "interview_scheduled",
    experience: "4 years",
    education: "Bachelor's in Business Administration",
    currentRole: "Marketing Coordinator at TechStart",
    skills: [
      "Project Management",
      "Digital Marketing",
      "Team Collaboration",
      "Presentation Skills",
      "Agile Methodology",
      "Stakeholder Management",
      "Budget Planning",
      "Market Research",
      "Content Strategy",
      "Cross-functional Leadership",
    ],
    resumeUrl: "/resumes/david-kim.pdf",
    coverLetterExcerpt:
      "I&apos;m particularly drawn to TechFlow's innovative approach...",
    matchScore: 90,
    volunteerWork: [
      "Habitat for Humanity - Build Team Leader (4 years): Led construction teams of 15+ volunteers on weekend builds",
      "STEM Education Foundation - Workshop Facilitator (3 years): Taught business and entrepreneurship to middle school students",
      "Korean Community Center - Marketing Director (2 years): Increased community event attendance by 200%",
      "Local Food Bank - Operations Volunteer (2 years): Managed inventory and coordinated distribution schedules",
      "Phoenix Marathon - Social Media Coordinator (1 year): Managed race day communications and participant engagement",
      "Small Business Development Center - Mentor (18 months): Provided marketing guidance to 10+ startup founders",
    ],
    personalProjects: [
      "Startup Marketing Strategy Consulting: Helped 5 friends launch businesses with comprehensive marketing plans",
      "Photography Portfolio Website: Self-built responsive site showcasing landscape and portrait work",
      "Korean-English Business Translation Service: Freelance work helping Korean businesses expand to US markets",
      "Local Hiking Group Organizer: Built community of 200+ hiking enthusiasts through social media and events",
      "Real Estate Investment Analysis Tool: Excel-based calculator used by 3 local real estate agents",
      'Community Newsletter "Phoenix Rising": Monthly digital publication reaching 1,500+ neighborhood residents',
      "Small Business Podcast Guest: Featured on 8 podcasts sharing marketing insights and entrepreneurship tips",
    ],
  },
  {
    id: 5,
    name: "Jessica Miller",
    email: "jessica.m@email.com",
    phone: "(555) 654-3210",
    location: "Mesa, AZ",
    appliedDate: "2024-10-27",
    status: "rejected",
    experience: "1 year",
    education: "Associate's in Marketing",
    currentRole: "Marketing Intern at LocalBiz",
    skills: [
      "Social Media",
      "Basic Analytics",
      "Customer Service",
      "Microsoft Office",
      "Entry-level Design",
      "Communication",
    ],
    resumeUrl: "/resumes/jessica-miller.pdf",
    coverLetterExcerpt:
      "Although I&apos;m early in my career, I&apos;m eager to learn...",
    matchScore: 72,
    volunteerWork: [
      "Mesa Public Library - Reading Program Assistant (2 years): Helped organize summer reading programs for children",
      "Local Elementary School - After-school Tutor (1 year): Provided homework help and mentorship to students",
      "Community Recreation Center - Event Helper (6 months): Assisted with setup and coordination of community events",
      "Animal Shelter - Weekend Volunteer (1 year): Helped with animal care and adoption event setup",
    ],
    personalProjects: [
      "Family Restaurant Social Media: Created Instagram and Facebook content for family's small restaurant business",
      'Personal Blog "Life After College": Shared experiences and tips for recent graduates, 50+ followers',
      "Neighborhood Babysitting Service: Built client base of 8 families through word-of-mouth referrals",
    ],
  },
];

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
    { value: "shortlisted", label: "Shortlisted" },
    { value: "interview_scheduled", label: "Interview Scheduled" },
    { value: "rejected", label: "Rejected" },
  ];

  return allStatuses.filter((status) => status.value !== currentStatus);
};

interface StatusDropdownProps {
  applicant: (typeof sampleApplicants)[0];
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

export default function ApplicationsPage(): ReactElement {
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("newest");
  const [selectedApplicants, setSelectedApplicants] = useState<Set<number>>(
    new Set()
  );
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set());
  const [openStatusDropdowns, setOpenStatusDropdowns] = useState<Set<number>>(
    new Set()
  );

  // TODO: Replace with API call
  const applicants = sampleApplicants;

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

  const handleSelectApplicant = (applicantId: number): void => {
    setSelectedApplicants((prev: Set<number>) => {
      const newSelected = new Set(prev);
      if (newSelected.has(applicantId)) {
        newSelected.delete(applicantId);
      } else {
        newSelected.add(applicantId);
      }
      return newSelected;
    });
  };

  const toggleCardExpansion = (applicantId: number): void => {
    setExpandedCards((prev: Set<number>) => {
      const newExpanded = new Set(prev);
      if (newExpanded.has(applicantId)) {
        newExpanded.delete(applicantId);
      } else {
        newExpanded.add(applicantId);
      }
      return newExpanded;
    });
  };

  const toggleStatusDropdown = (applicantId: number): void => {
    setOpenStatusDropdowns((prev: Set<number>) => {
      const newOpen = new Set(prev);
      if (newOpen.has(applicantId)) {
        newOpen.delete(applicantId);
      } else {
        newOpen.add(applicantId);
      }
      return newOpen;
    });
  };

  const updateApplicantStatus = (
    applicantId: number,
    newStatus: string
  ): void => {
    // TODO: Implement API call to update status
    console.log(`Updating applicant ${applicantId} status to ${newStatus}`);
    setOpenStatusDropdowns((prev: Set<number>) => {
      const newOpen = new Set(prev);
      newOpen.delete(applicantId);
      return newOpen;
    });
  };

  const defaultSkillsLimit = 4;
  const defaultVolunteerLimit = 2;
  const defaultProjectsLimit = 2;
  const expandedVolunteerLimit = 5;
  const expandedProjectsLimit = 5;

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
                {jobInfo.title}
              </h1>
              <div className="flex flex-col sm:flex-row sm:flex-wrap sm:items-center gap-2 sm:gap-4 text-green-700 mb-4">
                <span className="flex items-center min-w-0">
                  <Building2 className="w-4 h-4 mr-2 flex-shrink-0" />
                  <span className="truncate">{jobInfo.company}</span>
                </span>
                <span className="flex items-center min-w-0">
                  <MapPin className="w-4 h-4 mr-2 flex-shrink-0" />
                  <span className="truncate">{jobInfo.location}</span>
                </span>
                <span className="flex items-center">
                  <Clock className="w-4 h-4 mr-2 flex-shrink-0" />
                  {jobInfo.type}
                </span>
                <span className="flex items-center">
                  <Briefcase className="w-4 h-4 mr-2 flex-shrink-0" />
                  {jobInfo.salary}
                </span>
              </div>
              <p className="text-green-600 text-sm">
                Posted {jobInfo.posted} • {applicants.length} applications
                received
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
                            onUpdateStatus={(newStatus) =>
                              updateApplicantStatus(applicant.id, newStatus)
                            }
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
                            {applicant.experience} exp
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
                          onUpdateStatus={(newStatus) =>
                            updateApplicantStatus(applicant.id, newStatus)
                          }
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
                        Applied{" "}
                        {(() => {
                          const date = new Date(
                            applicant.appliedDate + "T00:00:00"
                          );
                          const months = [
                            "Jan",
                            "Feb",
                            "Mar",
                            "Apr",
                            "May",
                            "Jun",
                            "Jul",
                            "Aug",
                            "Sep",
                            "Oct",
                            "Nov",
                            "Dec",
                          ];
                          return `${months[date.getMonth()]} ${date.getDate()}`;
                        })()}
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
