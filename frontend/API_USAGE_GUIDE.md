# API Usage Guide for Frontend Developers & AI Agents

> **📖 Prerequisites**: Read [ZOD_SETUP.md](./ZOD_SETUP.md) first to understand the architecture.

## 🎯 Quick Start

### Step 1: Import the API
```typescript
import { api } from '@/lib/api';
import type { Job, User, Application } from '@/lib/api';
import { ApiError, ValidationError } from '@/lib/api';
```

### Step 2: Make Your First Request
```typescript
const jobs = await api.jobs.getAll({ limit: 10 });
```

**That's it!** Validation happens automatically.

---

## 🚨 CRITICAL: Error Handling (ALWAYS REQUIRED)

**⚠️ IMPORTANT**: Every API call MUST include proper error handling. Never make API calls without try/catch.

### ✅ Correct Pattern (ALWAYS USE THIS)
```typescript
import { api, ApiError, ValidationError } from '@/lib/api';

try {
  const result = await api.jobs.create(jobData);

  // ✅ Success - handle the result
  console.log('Job created:', result);
  return result;

} catch (error) {
  // ❌ Handle errors properly
  if (error instanceof ValidationError) {
    // Data validation failed (request or response)
    console.error('❌ Validation Error:');
    error.issues.forEach(issue => {
      console.error(`  - ${issue.path.join('.')}: ${issue.message}`);
    });
    // Show user-friendly error
    throw new Error('Invalid data provided');

  } else if (error instanceof ApiError) {
    // Backend returned an error (400, 404, 500, etc.)
    console.error(`❌ API Error (${error.status}):`, error.message);
    console.error('Details:', error.data);

    // Handle specific status codes
    if (error.status === 404) {
      throw new Error('Resource not found');
    } else if (error.status === 409) {
      throw new Error('Duplicate entry');
    } else if (error.status >= 500) {
      throw new Error('Server error, please try again later');
    }
    throw new Error(error.message);

  } else {
    // Network error or unexpected error
    console.error('❌ Unexpected Error:', error);
    throw new Error('An unexpected error occurred');
  }
}
```

### ❌ WRONG Pattern (NEVER DO THIS)
```typescript
// ❌ NO ERROR HANDLING - WILL CRASH YOUR APP
const jobs = await api.jobs.getAll();

// ❌ GENERIC CATCH - DOESN'T HELP USER
try {
  const jobs = await api.jobs.getAll();
} catch (error) {
  console.log('Error'); // ❌ Not helpful!
}
```

---

## 📚 Complete API Reference

### 1. Users API

#### Create User
```typescript
import { api, ApiError, ValidationError } from '@/lib/api';
import type { User, UserCreate } from '@/lib/api';

async function createUser(email: string, accountType: 'job_seeker' | 'employer'): Promise<User> {
  try {
    const userData: UserCreate = {
      email: email,
      account_type: accountType
    };

    const user = await api.users.create(userData);

    // ✅ Success
    console.log('✅ User created:', user.id);
    return user;

  } catch (error) {
    if (error instanceof ValidationError) {
      // Invalid email or account_type
      console.error('❌ Validation failed:', error.issues);
      throw new Error('Invalid user data');

    } else if (error instanceof ApiError) {
      if (error.status === 400) {
        // User already exists
        throw new Error('User with this email already exists');
      }
      throw new Error('Failed to create user');
    }
    throw error;
  }
}

// Usage
const user = await createUser('john@example.com', 'job_seeker');
```

#### Get User by ID
```typescript
async function getUserById(userId: string): Promise<User> {
  try {
    const user = await api.users.getById(userId);
    return user;

  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      throw new Error('User not found');
    }
    throw new Error('Failed to get user');
  }
}
```

#### Update User
```typescript
import type { UserUpdate } from '@/lib/api';

async function updateUserEmail(userId: string, newEmail: string): Promise<User> {
  try {
    const updateData: UserUpdate = {
      email: newEmail
    };

    const user = await api.users.update(userId, updateData);
    console.log('✅ User updated successfully');
    return user;

  } catch (error) {
    if (error instanceof ValidationError) {
      throw new Error('Invalid email format');
    } else if (error instanceof ApiError && error.status === 404) {
      throw new Error('User not found');
    }
    throw new Error('Failed to update user');
  }
}
```

---

### 2. Jobs API

#### Search Jobs (Most Common Use Case)
```typescript
import type { Job } from '@/lib/api';

async function searchJobs(
  searchQuery: string,
  filters?: {
    location?: string;
    remote?: boolean;
    skills?: string[];
    minSalary?: number;
  }
): Promise<Job[]> {
  try {
    const jobs = await api.jobs.search({
      query: searchQuery,
      location: filters?.location,
      remote_ok: filters?.remote,
      skills: filters?.skills,
      min_salary: filters?.minSalary,
      is_active: true,
      limit: 20
    });

    console.log(`✅ Found ${jobs.length} jobs`);
    return jobs;

  } catch (error) {
    if (error instanceof ValidationError) {
      console.error('❌ Invalid search parameters:', error.issues);
      throw new Error('Invalid search parameters');
    }
    throw new Error('Failed to search jobs');
  }
}

// Usage
const jobs = await searchJobs('software engineer', {
  location: 'San Francisco',
  remote: true,
  skills: ['TypeScript', 'React'],
  minSalary: 100000
});
```

#### Create Job Posting
```typescript
import type { JobCreate, Job } from '@/lib/api';

async function createJobPosting(jobData: JobCreate, employerId: string): Promise<Job> {
  try {
    const job = await api.jobs.create(jobData, employerId);

    console.log('✅ Job posted successfully:', job.id);
    return job;

  } catch (error) {
    if (error instanceof ValidationError) {
      // Show which fields are invalid
      console.error('❌ Invalid job data:');
      error.issues.forEach(issue => {
        console.error(`  - ${issue.path.join('.')}: ${issue.message}`);
      });
      throw new Error('Please fix the invalid fields');

    } else if (error instanceof ApiError && error.status === 404) {
      throw new Error('Employer not found');
    }
    throw new Error('Failed to create job posting');
  }
}

// Usage
const newJob = await createJobPosting({
  title: 'Senior TypeScript Developer',
  company: 'Tech Corp',
  description: 'We are looking for...',
  location: 'San Francisco, CA',
  job_type: 'Full-time',
  remote_ok: true,
  salary_min: 120000,
  salary_max: 180000,
  skills_required: ['TypeScript', 'React', 'Node.js'],
  responsibilities: ['Build features', 'Review code'],
  benefits: ['Health insurance', '401k']
}, 'employer-user-id-123');
```

#### Get Job with View Count
```typescript
async function getJobDetails(jobId: string, trackView: boolean = true): Promise<Job> {
  try {
    // incrementViews=true will track this as a view
    const job = await api.jobs.getById(jobId, trackView);

    console.log(`✅ Job: ${job.title}`);
    console.log(`   Views: ${job.view_count}`);
    return job;

  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      throw new Error('Job not found');
    }
    throw new Error('Failed to get job details');
  }
}
```

---

### 3. Applications API

#### Apply to Job
```typescript
import type { ApplicationCreate, Application } from '@/lib/api';

async function applyToJob(
  jobSeekerId: string,
  jobId: string,
  coverLetter?: string
): Promise<Application> {
  try {
    const applicationData: ApplicationCreate = {
      job_seeker_id: jobSeekerId,
      job_id: jobId,
      notes: coverLetter
    };

    const application = await api.applications.create(applicationData);

    console.log('✅ Application submitted successfully!');
    console.log(`   Status: ${application.status}`);
    console.log(`   Applied: ${application.applied_date.toLocaleDateString()}`);
    return application;

  } catch (error) {
    if (error instanceof ApiError) {
      if (error.status === 409) {
        // Already applied
        throw new Error('You have already applied to this job');
      } else if (error.status === 404) {
        throw new Error('Job or profile not found');
      } else if (error.status === 400) {
        // Job might be inactive
        throw new Error('Cannot apply to this job');
      }
    }
    throw new Error('Failed to submit application');
  }
}
```

#### Get User's Applications
```typescript
async function getMyApplications(jobSeekerId: string): Promise<Application[]> {
  try {
    const applications = await api.applications.getAll({
      job_seeker_id: jobSeekerId,
      limit: 50
    });

    console.log(`✅ Found ${applications.length} applications`);

    // Group by status
    const byStatus = applications.reduce((acc, app) => {
      acc[app.status] = (acc[app.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    console.log('   Status breakdown:', byStatus);
    return applications;

  } catch (error) {
    throw new Error('Failed to get applications');
  }
}
```

#### Update Application Status (Employer Action)
```typescript
import type { ApplicationUpdate } from '@/lib/api';

async function updateApplicationStatus(
  applicationId: string,
  status: string,
  notes?: string,
  changedBy?: string
): Promise<Application> {
  try {
    const updateData: ApplicationUpdate = {
      status: status,
      notes: notes
    };

    const application = await api.applications.update(
      applicationId,
      updateData,
      changedBy
    );

    console.log('✅ Application status updated');
    console.log(`   New status: ${application.status}`);

    // Status history is automatically tracked
    console.log('   History:');
    application.status_history.forEach(entry => {
      console.log(`     - ${entry.status} at ${entry.changed_at.toLocaleString()}`);
    });

    return application;

  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      throw new Error('Application not found');
    }
    throw new Error('Failed to update application');
  }
}
```

---

### 4. Job Seeker Profiles API

#### Create Profile
```typescript
import type { JobSeekerProfileCreate, JobSeekerProfile } from '@/lib/api';

async function createJobSeekerProfile(
  userId: string,
  profileData: Omit<JobSeekerProfileCreate, 'user_id'>
): Promise<JobSeekerProfile> {
  try {
    const profile = await api.jobSeekerProfiles.create({
      user_id: userId,
      ...profileData
    });

    console.log('✅ Profile created successfully');
    console.log(`   Completion: ${profile.profile_completion_percentage}%`);
    return profile;

  } catch (error) {
    if (error instanceof ValidationError) {
      console.error('❌ Invalid profile data:');
      error.issues.forEach(issue => {
        console.error(`  - ${issue.path.join('.')}: ${issue.message}`);
      });
      throw new Error('Please provide valid profile information');

    } else if (error instanceof ApiError && error.status === 400) {
      throw new Error('Profile already exists for this user');
    }
    throw new Error('Failed to create profile');
  }
}

// Usage
const profile = await createJobSeekerProfile('user-123', {
  first_name: 'John',
  last_name: 'Doe',
  email: 'john@example.com',
  phone: '+1-555-0123',
  location: 'San Francisco, CA',
  bio: 'Experienced software engineer...',
  skills: ['TypeScript', 'React', 'Node.js'],
  experience_years: 5,
  education_level: "Bachelor's Degree",
  preferences: {
    desired_salary_min: 100000,
    desired_salary_max: 150000,
    job_types: ['Full-time'],
    remote_ok: true,
    preferred_locations: ['San Francisco', 'Remote']
  }
});
```

#### Search Profiles (Employer Use Case)
```typescript
async function searchCandidates(
  requiredSkills: string[],
  location?: string,
  minExperience?: number
): Promise<JobSeekerProfile[]> {
  try {
    const profiles = await api.jobSeekerProfiles.search({
      skills: requiredSkills,
      location: location,
      min_experience: minExperience,
      limit: 20
    });

    console.log(`✅ Found ${profiles.length} matching candidates`);
    return profiles;

  } catch (error) {
    throw new Error('Failed to search candidates');
  }
}

// Usage
const candidates = await searchCandidates(
  ['React', 'TypeScript'],
  'San Francisco',
  3
);
```

---

### 5. Recommendations API

#### Get Job Recommendations for User
```typescript
async function getJobRecommendations(
  jobSeekerId: string,
  minMatchPercentage: number = 70
): Promise<any[]> {
  try {
    const recommendations = await api.recommendations.getForJobSeeker(
      jobSeekerId,
      {
        min_match: minMatchPercentage,
        include_viewed: false, // Only show new recommendations
        include_dismissed: false,
        include_applied: false,
        limit: 10
      }
    );

    console.log(`✅ Found ${recommendations.length} job recommendations`);

    recommendations.forEach((rec: any) => {
      console.log(`\n🎯 ${rec.job_title} at ${rec.job_company}`);
      console.log(`   Match: ${rec.match_percentage}%`);
      console.log(`   Why: ${rec.reasoning}`);
    });

    return recommendations;

  } catch (error) {
    throw new Error('Failed to get recommendations');
  }
}
```

#### Mark Recommendation as Viewed
```typescript
async function trackRecommendationView(recommendationId: string): Promise<void> {
  try {
    await api.recommendations.markViewed(recommendationId);
    console.log('✅ Recommendation view tracked');

  } catch (error) {
    // Non-critical error, just log it
    console.warn('Failed to track recommendation view');
  }
}
```

---

## 🎨 React Component Examples

### Server Component (Next.js App Router)
```typescript
import { api } from '@/lib/api';
import { ApiError } from '@/lib/api';

export default async function JobsPage() {
  let jobs;
  let error;

  try {
    jobs = await api.jobs.getAll({
      is_active: true,
      limit: 20
    });
  } catch (err) {
    if (err instanceof ApiError) {
      error = `Failed to load jobs: ${err.message}`;
    } else {
      error = 'An unexpected error occurred';
    }
  }

  if (error) {
    return (
      <div className="error">
        <h1>Error</h1>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div>
      <h1>Available Jobs</h1>
      {jobs?.map((job) => (
        <div key={job.id}>
          <h2>{job.title}</h2>
          <p>{job.company} - {job.location}</p>
          <p>Views: {job.view_count}</p>
        </div>
      ))}
    </div>
  );
}
```

### Client Component with Form
```typescript
'use client';

import { useState } from 'react';
import { api, ApiError, ValidationError } from '@/lib/api';
import type { Job } from '@/lib/api';

export function JobSearchForm() {
  const [query, setQuery] = useState('');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const results = await api.jobs.search({
        query: query,
        is_active: true,
        limit: 20
      });

      setJobs(results);
      console.log(`✅ Found ${results.length} jobs`);

    } catch (err) {
      if (err instanceof ValidationError) {
        setError('Invalid search query');
        console.error('Validation errors:', err.issues);

      } else if (err instanceof ApiError) {
        setError(`Search failed: ${err.message}`);
        console.error(`API error (${err.status}):`, err.data);

      } else {
        setError('An unexpected error occurred');
        console.error('Unexpected error:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search jobs..."
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && (
        <div className="error">❌ {error}</div>
      )}

      <div>
        {jobs.map((job) => (
          <div key={job.id}>
            <h3>{job.title}</h3>
            <p>{job.company} - {job.location}</p>
            {job.remote_ok && <span>🏠 Remote</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Client Component with Mutations
```typescript
'use client';

import { useState } from 'react';
import { api, ApiError, ValidationError } from '@/lib/api';
import type { JobCreate } from '@/lib/api';

export function CreateJobForm({ employerId }: { employerId: string }) {
  const [formData, setFormData] = useState<JobCreate>({
    title: '',
    company: '',
    description: '',
    location: '',
    job_type: 'Full-time',
    remote_ok: false,
    skills_required: [],
    responsibilities: [],
    benefits: []
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setFieldErrors({});

    try {
      const job = await api.jobs.create(formData, employerId);

      console.log('✅ Job created successfully:', job.id);
      alert('Job posted successfully!');

      // Reset form or redirect
      // router.push(`/jobs/${job.id}`);

    } catch (err) {
      if (err instanceof ValidationError) {
        // Show field-specific errors
        const errors: Record<string, string> = {};
        err.issues.forEach(issue => {
          const field = issue.path.join('.');
          errors[field] = issue.message;
        });
        setFieldErrors(errors);
        setError('Please fix the validation errors');

        console.error('❌ Validation errors:', err.issues);

      } else if (err instanceof ApiError) {
        setError(`Failed to create job: ${err.message}`);
        console.error(`❌ API error (${err.status}):`, err.data);

      } else {
        setError('An unexpected error occurred');
        console.error('❌ Unexpected error:', err);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div className="error">❌ {error}</div>
      )}

      <div>
        <label>Job Title *</label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
        />
        {fieldErrors.title && (
          <span className="field-error">{fieldErrors.title}</span>
        )}
      </div>

      <div>
        <label>Company *</label>
        <input
          type="text"
          value={formData.company}
          onChange={(e) => setFormData({ ...formData, company: e.target.value })}
        />
        {fieldErrors.company && (
          <span className="field-error">{fieldErrors.company}</span>
        )}
      </div>

      {/* Add more fields... */}

      <button type="submit" disabled={submitting}>
        {submitting ? 'Creating...' : 'Create Job'}
      </button>
    </form>
  );
}
```

---

## ⚡ Best Practices Checklist

### ✅ DO
- **Always use try/catch** for error handling
- **Check error types** (ValidationError vs ApiError)
- **Log errors** with console.error for debugging
- **Show user-friendly messages** to users
- **Handle specific HTTP status codes** (404, 409, 500, etc.)
- **Use TypeScript types** from the API
- **Validate on the client** before submitting (better UX)
- **Show loading states** during API calls
- **Test error scenarios** in development

### ❌ DON'T
- **Don't ignore errors** or use empty catch blocks
- **Don't expose raw error messages** to users
- **Don't make API calls without error handling**
- **Don't mutate shared state** without proper React patterns
- **Don't forget to handle loading/error states** in UI
- **Don't hardcode API URLs** (use environment variables)
- **Don't bypass TypeScript** with `any` types

---

## 🐛 Debugging & Troubleshooting

### Issue: "Request validation failed"
```typescript
// ❌ Error: ValidationError
// Cause: Data doesn't match schema

// Fix: Check the validation errors
catch (error) {
  if (error instanceof ValidationError) {
    console.error('Validation issues:');
    error.issues.forEach(issue => {
      console.error(`  Field: ${issue.path.join('.')}`);
      console.error(`  Error: ${issue.message}`);
      console.error(`  Received: ${issue.received}`);
    });
  }
}
```

### Issue: "Response validation failed"
```typescript
// This means the backend sent unexpected data
// 1. Check if backend schema matches frontend schema
// 2. Check backend response in Network tab
// 3. Update frontend schemas if backend changed
```

### Issue: "API Error 404"
```typescript
// Resource not found
catch (error) {
  if (error instanceof ApiError && error.status === 404) {
    // Handle missing resource
    console.error('Resource not found');
  }
}
```

### Issue: CORS errors
```typescript
// Make sure NEXT_PUBLIC_API_URL is set correctly
// Check .env file:
NEXT_PUBLIC_API_URL=http://localhost:8000

// In docker-compose.yml, backend should allow frontend origin
```

---

## 🧪 Testing Your API Calls

### Test in Browser Console
```typescript
// Open browser console on your Next.js page
import('/lib/api').then(({ api }) => {
  api.jobs.getAll({ limit: 5 })
    .then(jobs => console.log('✅ Jobs:', jobs))
    .catch(err => console.error('❌ Error:', err));
});
```

### Test Error Scenarios
```typescript
// Test validation error
api.users.create({
  email: 'invalid-email', // ❌ Will fail validation
  account_type: 'hacker' // ❌ Invalid enum
});

// Test 404 error
api.jobs.getById('non-existent-id');

// Test duplicate error
// Create user, then try creating same user again
```

---

## 📖 Additional Resources

- **Architecture Guide**: [ZOD_SETUP.md](./ZOD_SETUP.md)
- **Backend API Docs**: Check `backend/app/api/routes/`
- **Zod Documentation**: https://zod.dev
- **Next.js Data Fetching**: https://nextjs.org/docs/app/building-your-application/data-fetching

---

## 🤖 Instructions for AI Agents

When a human asks you to make API calls in this project:

1. **Read this guide first** to understand the API structure
2. **Always import**: `import { api, ApiError, ValidationError } from '@/lib/api';`
3. **Always use try/catch** with proper error handling
4. **Check available methods** in the API Reference section above
5. **Use TypeScript types** for all data
6. **Log errors clearly** for debugging
7. **Show loading states** in UI components
8. **Reference ZOD_SETUP.md** for architecture details

### Example Task: "Create a component that searches jobs"

**Step 1**: Import dependencies
```typescript
import { api, ApiError, ValidationError } from '@/lib/api';
import type { Job } from '@/lib/api';
```

**Step 2**: Add state
```typescript
const [jobs, setJobs] = useState<Job[]>([]);
const [error, setError] = useState<string | null>(null);
```

**Step 3**: Make API call with error handling
```typescript
try {
  const results = await api.jobs.search({ query: 'engineer' });
  setJobs(results);
} catch (err) {
  if (err instanceof ValidationError) {
    setError('Invalid search parameters');
  } else if (err instanceof ApiError) {
    setError(`Search failed: ${err.message}`);
  } else {
    setError('An unexpected error occurred');
  }
}
```

**Step 4**: Render with error/loading states
```typescript
if (error) return <div>Error: {error}</div>;
return <div>{jobs.map(job => ...)}</div>;
```

---

## ✅ Quick Reference Card

```typescript
// Import
import { api, ApiError, ValidationError } from '@/lib/api';
import type { Job, User, Application } from '@/lib/api';

// Error Handling Template
try {
  const result = await api.MODULE.METHOD(params);
  // ✅ Success
} catch (error) {
  if (error instanceof ValidationError) {
    // Data validation failed
  } else if (error instanceof ApiError) {
    // Backend error (check error.status)
  } else {
    // Network/unexpected error
  }
}

// Common Patterns
api.jobs.search({ query: '...' })           // Search
api.users.create(data)                      // Create
api.applications.getAll({ job_id: '...' }) // Filter
api.jobSeekerProfiles.update(id, data)     // Update
api.jobs.delete(id)                         // Delete
```

---

**Happy coding! 🚀**

For questions or issues, refer to the complete architecture documentation in [ZOD_SETUP.md](./ZOD_SETUP.md).
