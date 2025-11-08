'use client';

import { useState } from 'react';
import Link from 'next/link';
import { 
  Leaf, Heart, Search, FileText, Star, Calendar, TrendingUp, Plus, 
  Briefcase, Clock, CheckCircle, RefreshCw, Sparkles 
} from 'lucide-react';

// TODO: Replace with API call to fetch user applications
const sampleApplications = [
  { 
    id: 1, 
    company: "TechFlow Solutions", 
    role: "Marketing Coordinator", 
    status: "Interview Scheduled", 
    appliedDate: "2 days ago", 
    nextStep: "Video interview tomorrow at 2 PM" 
  },
  { 
    id: 2, 
    company: "DataCore Industries", 
    role: "Business Analyst", 
    status: "Under Review", 
    appliedDate: "1 week ago", 
    nextStep: "Waiting for initial response" 
  },
  { 
    id: 3, 
    company: "Summit Financial", 
    role: "Customer Success Associate", 
    status: "Application Submitted", 
    appliedDate: "3 days ago", 
    nextStep: "Application in queue for review" 
  }
];

// TODO: Replace with API call to fetch job recommendations
const sampleRecommendations = [
  { 
    id: 1, 
    company: "InnovateNow Corp", 
    role: "Project Manager", 
    match: "94%", 
    reason: "Perfect match for your project coordination experience" 
  },
  { 
    id: 2, 
    company: "Metro Healthcare Group", 
    role: "Administrative Assistant", 
    match: "89%", 
    reason: "Aligns with your organizational and communication skills" 
  },
  { 
    id: 3, 
    company: "BlueTech Systems", 
    role: "Sales Representative", 
    match: "85%", 
    reason: "Great fit for your customer service background" 
  }
];

const healthyReminders = [
  "Remember: Every 'no' brings you closer to your perfect 'yes'.",
  "Your worth isn't determined by application responses.",
  "It's okay to take breaks from job searching when you need them.",
  "Quality applications matter more than quantity.",
  "You're allowed to have standards for how you want to be treated.",
  "Job hunting is temporary - your resilience is permanent."
];

export default function DashboardPage() {
  // TODO: Replace with actual user data from auth context
  const userName = "Alex";
  
  const [currentReminder, setCurrentReminder] = useState(healthyReminders[0]);

  const generateReminder = () => {
    const randomIndex = Math.floor(Math.random() * healthyReminders.length);
    setCurrentReminder(healthyReminders[randomIndex]);
  };

  // TODO: Replace with API call to fetch stats
  const stats = {
    applicationsThisWeek: 3,
    interviewsScheduled: 1,
    profileViews: 12,
    newMatches: 5
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-amber-50 to-green-100">
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-green-900 mb-2 flex items-center">
            Good morning, {userName}! 
            <Leaf className="w-8 h-8 ml-3 text-green-600" />
          </h1>
          <p className="text-green-700">Ready to continue nurturing your career growth?</p>
        </div>

        {/* Daily Reminder */}
        <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-green-800 flex items-center">
              <Heart className="w-5 h-5 mr-2" />
              Your Daily Reminder
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
            <p className="text-green-800 font-medium italic">&quot;{currentReminder}&quot;</p>
          </div>
        </div>

        {/* Quick Stats with Integrated Actions */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-green-700">Applications This Week</h3>
              <Briefcase className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-green-900">{stats.applicationsThisWeek}</p>
            <p className="text-xs text-green-600 mb-4 flex items-center">
              Quality over quantity 
              <Heart className="w-3 h-3 ml-1 text-green-500" />
            </p>
            <div className="space-y-2">
              <Link href="/jobs" className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm">
                <Search className="w-4 h-4 mr-2" />
                Search New Jobs
              </Link>
              <Link href="/applications" className="w-full bg-green-50 text-green-700 border border-green-300 py-2 px-4 rounded-lg font-medium hover:bg-green-100 transition-all flex items-center justify-center text-sm">
                <Briefcase className="w-4 h-4 mr-2" />
                View Applications
              </Link>
            </div>
          </div>
          
          <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-green-700">Interviews Scheduled</h3>
              <Calendar className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-green-900">{stats.interviewsScheduled}</p>
            <p className="text-xs text-green-600 mb-4 flex items-center">
              You've got this!
              <Calendar className="w-3 h-3 ml-1 text-green-500" />
            </p>
            <Link href="/applications" className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm">
              <Calendar className="w-4 h-4 mr-2" />
              Manage Interviews
            </Link>
          </div>
          
          <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-green-700">Profile Views</h3>
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-green-900">{stats.profileViews}</p>
            <p className="text-xs text-green-600 mb-4 flex items-center">
              People notice you 
              <Star className="w-3 h-3 ml-1 text-amber-500" />
            </p>
            <Link href="/profile" className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm">
              <FileText className="w-4 h-4 mr-2" />
              Update Profile
            </Link>
          </div>
          
          <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-green-700">New Matches</h3>
              <Star className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-green-900">{stats.newMatches}</p>
            <p className="text-xs text-green-600 mb-4 flex items-center">
              Great opportunities waiting!
              <TrendingUp className="w-3 h-3 ml-1 text-green-500" />
            </p>
            <div className="space-y-2">
              <Link href="/profile" className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-2 px-4 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center text-sm">
                <FileText className="w-4 h-4 mr-2" />
                Update Resume
              </Link>
              <a 
                href="#recommendations-section"
                className="w-full bg-green-50 text-green-700 border border-green-300 py-2 px-4 rounded-lg font-medium hover:bg-green-100 transition-all flex items-center justify-center text-sm"
              >
                <Star className="w-4 h-4 mr-2" />
                View Matches
              </a>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Applications */}
          <div id="applications-section" className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-green-900">Your Applications</h2>
              <Link href="/applications" className="text-green-700 hover:text-green-800 font-medium transition-colors">
                View All
              </Link>
            </div>
            
            <div className="space-y-4">
              {sampleApplications.map((app) => (
                <div key={app.id} className="bg-white/60 rounded-lg p-4 border border-green-100">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-semibold text-green-900">{app.role}</h3>
                      <p className="text-sm text-green-700">{app.company}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      {app.status === 'Interview Scheduled' && <Calendar className="w-4 h-4 text-amber-600" />}
                      {app.status === 'Under Review' && <Clock className="w-4 h-4 text-blue-600" />}
                      {app.status === 'Application Submitted' && <CheckCircle className="w-4 h-4 text-green-600" />}
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        app.status === 'Interview Scheduled' ? 'bg-amber-100 text-amber-800' :
                        app.status === 'Under Review' ? 'bg-blue-100 text-blue-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {app.status}
                      </span>
                    </div>
                  </div>
                  <p className="text-xs text-green-600 mb-2">Applied {app.appliedDate}</p>
                  <p className="text-sm text-green-700">{app.nextStep}</p>
                </div>
              ))}
            </div>
            
            <Link href="/applications" className="w-full mt-4 bg-gradient-to-r from-green-600 to-green-700 text-white py-3 rounded-lg font-semibold hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center">
              <Plus className="w-5 h-5 mr-2" />
              Track New Application
            </Link>
          </div>

          {/* Recommendations */}
          <div id="recommendations-section" className="bg-white/70 backdrop-blur-sm rounded-xl border border-green-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-green-900">Recommended for You</h2>
              <Link href="/jobs" className="text-green-700 hover:text-green-800 font-medium transition-colors">
                See More
              </Link>
            </div>
            
            <div className="space-y-4">
              {sampleRecommendations.map((rec) => (
                <div key={rec.id} className="bg-white/60 rounded-lg p-4 border border-green-100">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-semibold text-green-900">{rec.role}</h3>
                      <p className="text-sm text-green-700">{rec.company}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Star className="w-4 h-4 text-amber-500" />
                      <span className="text-sm font-medium text-green-800">{rec.match} match</span>
                    </div>
                  </div>
                  <p className="text-sm text-green-600 mb-3 flex items-start">
                    <span className="flex items-center mr-2">
                      <span className="font-medium">Harmony says</span>
                      <Sparkles className="w-3 h-3 ml-1 text-amber-500" />
                    </span>
                    <span className="italic">&quot;{rec.reason}&quot;</span>
                  </p>
                  <Link href="/jobs" className="text-green-700 hover:text-green-800 font-medium text-sm transition-colors">
                    View Details →
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

