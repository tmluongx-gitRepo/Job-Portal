/**
 * Dashboard feature type definitions
 */

export interface DashboardStats {
  applicationsThisWeek: number;
  interviewsScheduled: number;
  profileViews: number;
  newMatches: number;
}

export interface UserApplication {
  id: number;
  company: string;
  role: string;
  status: string;
  appliedDate: string;
  nextStep: string;
}

export interface JobRecommendation {
  id: number;
  company: string;
  role: string;
  match: string;
  reason: string;
}
