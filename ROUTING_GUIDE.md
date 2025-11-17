# Company Registration Page - Routing Guide

## Overview
This document describes the routing setup for the Company Registration page in the Career Harmony job portal application.

## Route Structure

The application uses Next.js 13+ App Router for routing. The Company Registration page has been set up at the following route:

```
/company-registration
```

## File Structure

```
frontend/
├── src/
│   └── app/
│       ├── company-registration/
│       │   └── page.tsx          # Company registration page component
│       ├── jobs/
│       │   └── page.tsx          # Jobs listing page
│       └── page.tsx              # Home page
```

## Accessing the Company Registration Page

### From the Application
1. Navigate to the home page (`/`)
2. Click the "Register Company" button
3. You will be redirected to `/company-registration`

### Direct URL
Users can also access the page directly via:
- Local development: `http://localhost:3000/company-registration`
- Production: `https://yourdomain.com/company-registration`

## Page Features

The Company Registration page (`/company-registration`) includes:

1. **Multi-step Registration Form**
   - Step 1: Account Information (Email, Password, Contact Details)
   - Step 2: Company Profile (Company Details, Culture, Benefits)
   - Step 3: Preview & Submit

2. **Form Validation**
   - Password strength validation (minimum 8 characters)
   - Password confirmation matching
   - Required field validation

3. **Data Collection**
   - Basic account information
   - Company details (name, industry, size, location)
   - Company culture attributes
   - Benefits and perks offered
   - Remote work policies

## Navigation Flow

```
Home (/)
  ↓
  └─→ Company Registration (/company-registration)
       ├─→ Step 1: Create Account
       ├─→ Step 2: Company Profile
       └─→ Step 3: Preview & Submit
            └─→ Success → Redirect to Employer Dashboard (future)
```

## Integration Points

### Backend API Integration
The registration form is ready to integrate with the backend API endpoint:
- **Endpoint**: `/api/v1/auth/register`
- **Method**: POST
- **Payload**: 
  ```json
  {
    "email": "string",
    "password": "string",
    "confirm_password": "string",
    "account_type": "employer",
    "first_name": "string",
    "last_name": "string",
    "company_profile": {
      "company_name": "string",
      "description": "string",
      "industry": "string",
      "company_size": "string",
      "location": "string",
      "website": "string",
      "phone": "string",
      "job_title": "string",
      "founded_year": "string",
      "remote_policy": "string",
      "work_environment": ["string"],
      "benefits": ["string"]
    }
  }
  ```

### Future Enhancements
- Add authentication redirect
- Implement email verification flow
- Add employer dashboard route
- Add company profile edit page
- Add job posting creation flow

## Styling

The page uses:
- Tailwind CSS for styling
- Custom green color scheme (Career Harmony branding)
- Responsive design for mobile and desktop
- Custom animations (fade-in, slide-up)

## Technical Notes

- **Component Type**: Client Component (`'use client'`)
- **State Management**: React useState hooks
- **Form Handling**: Controlled components
- **Validation**: Client-side validation (can be enhanced with libraries like Zod)
- **Routing**: Next.js App Router (file-based routing)

## Related Files

- Main page with navigation: `/workspace/frontend/src/app/page.tsx`
- Company registration page: `/workspace/frontend/src/app/company-registration/page.tsx`
- Original mockup: `/workspace/frontend/company-registration-tsx.ts`

## Testing the Route

1. Start the development server:
   ```bash
   cd frontend
   npm run dev
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:3000/company-registration
   ```

3. Test the multi-step form:
   - Fill out account information
   - Navigate to company profile
   - Review in preview mode
   - Submit (currently shows success message)

## Notes

- The API integration is commented out and ready to be enabled
- Form data is logged to console for development/debugging
- Success flow shows alert (to be replaced with proper redirect)
- All required fields are marked with red asterisks (*)

