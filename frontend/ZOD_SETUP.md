# Zod Validation Setup - Feature-Based Architecture

## ✅ What's Been Set Up

A **production-ready, feature-based architecture** for type-safe API validation:

```
src/lib/api/
├── client.ts                      # Base utilities (apiRequest, errors)
│
├── users/
│   ├── schemas.ts                 # User Zod schemas
│   ├── api.ts                     # User API functions
│   ├── types.ts                   # TypeScript types
│   └── index.ts                   # Barrel export
│
├── jobs/
│   ├── schemas.ts
│   ├── api.ts
│   ├── types.ts
│   └── index.ts
│
├── applications/
│   ├── schemas.ts
│   ├── api.ts
│   ├── types.ts
│   └── index.ts
│
├── job-seeker-profiles/
│   ├── schemas.ts
│   ├── api.ts
│   ├── types.ts
│   └── index.ts
│
├── employer-profiles/
│   ├── schemas.ts
│   ├── api.ts
│   ├── types.ts
│   └── index.ts
│
├── recommendations/
│   ├── schemas.ts
│   ├── api.ts
│   ├── types.ts
│   └── index.ts
│
└── index.ts                       # Main export
```

## 🏗️ Architecture Benefits

### ✅ Scalability
- Each domain can grow independently
- Add new features without touching existing code
- Easy to split into micro-frontends later

### ✅ Maintainability
- Clear domain boundaries
- Easy to find user-related code vs job-related code
- Single Responsibility Principle

### ✅ Performance
- Better tree-shaking (only import what you need)
- Smaller bundle sizes
- Code-splitting friendly

### ✅ Team Collaboration
- Multiple developers can work on different domains
- Fewer merge conflicts
- Clear code ownership

### ✅ Testing
- Test each domain in isolation
- Mock dependencies easily
- Better test organization

## 🚀 Installation

Since you're using Docker with Bun, install Zod by running:

```bash
# From your host machine
docker exec job-portal-frontend bun install

# OR restart the frontend container (it will auto-install from package.json)
docker compose restart frontend
```

## 📦 Usage

### Import Everything from One Place

```typescript
// Import the API client and types
import { api } from '@/lib/api';
import type { Job, User, Application } from '@/lib/api';

// Use the API
const jobs = await api.jobs.search({ query: 'engineer' });
const user = await api.users.getById('123');
```

### Import from Specific Modules (Tree-Shaking)

```typescript
// Only import what you need - better for bundle size
import { jobApi } from '@/lib/api/jobs';
import type { Job } from '@/lib/api/jobs';

const jobs = await jobApi.search({ query: 'engineer' });
```

## 🎯 What You Get

### 1. Request Validation (Before Sending to Backend)
```typescript
import { api } from '@/lib/api';

// ❌ This will FAIL before even making the API call
await api.users.create({
  email: 'not-an-email',  // Invalid email format
  account_type: 'hacker'  // Not 'job_seeker' or 'employer'
});
// Throws ValidationError with detailed issues
```

### 2. Response Validation (After Receiving from Backend)
```typescript
// ✅ Backend response is automatically validated
const jobs = await api.jobs.search({ query: 'engineer' });

// If backend sends unexpected data, you'll get a ValidationError
// This protects your frontend from breaking when backend changes
```

### 3. Full TypeScript Type Safety
```typescript
const user = await api.users.create({
  email: 'test@example.com',
  account_type: 'job_seeker'
});

// TypeScript knows the exact type
user.id          // string
user.email       // string
user.created_at  // Date (automatically parsed from ISO string)
user.updated_at  // Date
```

## 📚 Available APIs

All APIs are available through the `api` object:

### Users API
```typescript
api.users.create(data)
api.users.getAll(params)
api.users.getById(id)
api.users.getByEmail(email)
api.users.update(id, data)
api.users.delete(id)
```

### Jobs API
```typescript
api.jobs.create(data, postedBy)
api.jobs.getAll(params)
api.jobs.search(params)
api.jobs.getById(id, incrementViews)
api.jobs.update(id, data)
api.jobs.delete(id)
api.jobs.getCount(params)
```

### Applications API
```typescript
api.applications.create(data)
api.applications.getAll(params)
api.applications.getById(id)
api.applications.update(id, data, changedBy)
api.applications.delete(id)
api.applications.getCount(params)
```

### Job Seeker Profiles API
```typescript
api.jobSeekerProfiles.create(data)
api.jobSeekerProfiles.getAll(params)
api.jobSeekerProfiles.search(params)
api.jobSeekerProfiles.getById(id, incrementViews)
api.jobSeekerProfiles.getByUserId(userId)
api.jobSeekerProfiles.update(id, data)
api.jobSeekerProfiles.delete(id)
```

### Employer Profiles API
```typescript
api.employerProfiles.create(data)
api.employerProfiles.getAll(params)
api.employerProfiles.getById(id)
api.employerProfiles.getByUserId(userId)
api.employerProfiles.update(id, data)
api.employerProfiles.delete(id)
```

### Recommendations API
```typescript
api.recommendations.create(data)
api.recommendations.getForJobSeeker(id, params)
api.recommendations.getCandidatesForJob(id, params)
api.recommendations.getById(id)
api.recommendations.update(id, data)
api.recommendations.markViewed(id)
api.recommendations.dismiss(id)
api.recommendations.delete(id)
api.recommendations.getCount(id, params)
```

## 💻 Code Examples

### Server Component (Next.js 15)
```typescript
import { api } from '@/lib/api';

export default async function JobsPage() {
  const jobs = await api.jobs.getAll({ is_active: true, limit: 20 });

  return (
    <div>
      {jobs.map((job) => (
        <div key={job.id}>
          <h2>{job.title}</h2>
          <p>{job.company} - {job.location}</p>
        </div>
      ))}
    </div>
  );
}
```

### Client Component with Error Handling
```typescript
'use client';

import { useState } from 'react';
import { api, ApiError, ValidationError } from '@/lib/api';

export function JobSearchForm() {
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');

  const handleSearch = async (query: string) => {
    try {
      const jobs = await api.jobs.search({ query });
      setResults(jobs);
      setError('');
    } catch (err) {
      if (err instanceof ValidationError) {
        setError('Invalid search parameters');
      } else if (err instanceof ApiError) {
        setError(`Error: ${err.message}`);
      } else {
        setError('An unexpected error occurred');
      }
    }
  };

  // ... render form
}
```

### Creating a Job Application
```typescript
import { api } from '@/lib/api';

async function applyToJob(jobSeekerId: string, jobId: string) {
  try {
    const application = await api.applications.create({
      job_seeker_id: jobSeekerId,
      job_id: jobId,
      notes: 'I am very interested in this position!'
    });

    console.log('Application submitted!', application);
  } catch (error) {
    if (error instanceof ApiError && error.status === 409) {
      console.error('Already applied to this job!');
    }
  }
}
```

### Using Individual Modules (Tree-Shaking)
```typescript
// Import only what you need - smaller bundle size
import { jobApi } from '@/lib/api/jobs';
import { userApi } from '@/lib/api/users';
import type { Job, User } from '@/lib/api';

// Use them
const jobs = await jobApi.search({ query: 'engineer' });
const user = await userApi.getById('123');
```

## 🔒 Error Types

### ValidationError
Thrown when data doesn't match the schema (before sending or after receiving):
```typescript
import { ValidationError } from '@/lib/api';

catch (error) {
  if (error instanceof ValidationError) {
    console.error('Validation failed:', error.issues);
    error.issues.forEach(issue => {
      console.error(`${issue.path.join('.')}: ${issue.message}`);
    });
  }
}
```

### ApiError
Thrown when the API returns an error status (400, 404, 500, etc.):
```typescript
import { ApiError } from '@/lib/api';

catch (error) {
  if (error instanceof ApiError) {
    console.error(`API Error ${error.status}:`, error.message);
    console.error('Details:', error.data);
  }
}
```

## 🎨 TypeScript Types

All types are automatically inferred from schemas:

```typescript
import type {
  User,
  Job,
  Application,
  JobSeekerProfile,
  EmployerProfile,
  Recommendation
} from '@/lib/api';

// Use in your components
const job: Job = await api.jobs.getById('123');
```

## 🛠️ Advanced Usage

### Access Zod Schemas Directly
```typescript
import { JobSchemas } from '@/lib/api';

// Use for custom validation
const result = JobSchemas.JobCreateSchema.safeParse(data);
```

### Extend a Module
Create `src/lib/api/jobs/custom-api.ts`:
```typescript
import { apiRequest } from '../client';
import { JobResponseSchema } from './schemas';
import { z } from 'zod';

export async function getFeaturedJobs() {
  return apiRequest('/jobs/featured', {
    method: 'GET',
    responseSchema: z.array(JobResponseSchema),
  });
}
```

Then export it in `src/lib/api/jobs/index.ts`:
```typescript
export * from './custom-api';
```

## 🔧 Environment Variables

Make sure `NEXT_PUBLIC_API_URL` is set in your `.env`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## ✨ Benefits of Feature-Based Architecture

1. **Scalability** - Add new features without touching existing code
2. **Maintainability** - Easy to find and update domain-specific code
3. **Better Bundles** - Tree-shaking works better with small modules
4. **Team-Friendly** - Multiple developers can work without conflicts
5. **Testability** - Test each domain in isolation
6. **Clear Boundaries** - Follows domain-driven design principles

## 📈 Performance

### Bundle Size Comparison

**Before (Monolithic):**
- Import one schema → load ALL schemas (300+ lines)
- Import one API → load ALL APIs (600+ lines)

**After (Feature-Based):**
- Import `api.jobs` → load ONLY jobs module (~100 lines)
- Import `api.users` → load ONLY users module (~50 lines)
- Better code-splitting and lazy loading

## 🚨 Important Notes

- All date fields are automatically converted from ISO strings to JavaScript `Date` objects
- The API client uses `NEXT_PUBLIC_API_URL` from environment variables
- Both request and response validation happens automatically
- Invalid data throws errors immediately (fail fast)
- Each module is self-contained and can be tested independently

## 🎓 Best Practices

### ✅ DO
```typescript
// Import from main barrel export for convenience
import { api } from '@/lib/api';
const jobs = await api.jobs.getAll();

// Or import specific modules for better tree-shaking
import { jobApi } from '@/lib/api/jobs';
const jobs = await jobApi.getAll();
```

### ❌ DON'T
```typescript
// Don't import internal files
import { jobApi } from '@/lib/api/jobs/api'; // ❌ Bad
import { JobResponseSchema } from '@/lib/api/jobs/schemas'; // ❌ Bad

// Use barrel exports instead
import { jobApi, JobResponseSchema } from '@/lib/api/jobs'; // ✅ Good
```

## 📝 Migration from Old Setup

If you were using the old monolithic files:

```typescript
// OLD (monolithic)
import { api } from '@/lib/api-client';

// NEW (feature-based) - same usage!
import { api } from '@/lib/api';

// API usage is IDENTICAL
const jobs = await api.jobs.search({ query: 'engineer' });
```

The old files (`schemas.ts`, `api-client.ts`, `api-examples.ts`) can be deleted.
