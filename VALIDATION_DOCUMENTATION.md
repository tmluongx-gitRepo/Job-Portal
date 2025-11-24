# Company Registration - Field Validations Documentation

## Overview

This document details all field validations implemented across the Company Registration page. The validation system provides real-time feedback to users and prevents navigation between tabs if required fields are incomplete or invalid.

## Validation System Architecture

### Components
1. **Validation State**: `errors` state object tracks validation errors for all fields
2. **Validation Functions**: Individual validators for each field type
3. **Tab Validators**: Aggregate validators for each tab (`validateRegisterTab`, `validateProfileTab`)
4. **Visual Feedback**: Red borders and error messages for invalid fields
5. **Navigation Guards**: Prevent tab navigation if current tab has validation errors

## Tab 1: Create Account (Register Tab)

### Required Fields

#### 1. Email Address
- **Field**: `registrationData.email`
- **Required**: ✅ Yes
- **Validation Rules**:
  - Cannot be empty
  - Must match email format: `user@domain.extension`
  - Must contain `@` symbol
  - Must contain domain with extension
  - No spaces allowed
- **Error Messages**:
  - "Email address is required"
  - "Please enter a valid email address (e.g., user@example.com)"
- **Examples**:
  - ✅ Valid: `john.doe@company.com`, `hr@startup.io`
  - ❌ Invalid: `notanemail`, `user@`, `@domain.com`, `user@domain`

#### 2. Company Name
- **Field**: `companyProfile.company_name`
- **Required**: ✅ Yes
- **Validation Rules**:
  - Cannot be empty
  - Minimum 2 characters
- **Error Messages**:
  - "Company name is required"
  - "Company name must be at least 2 characters"

#### 3. First Name
- **Field**: `registrationData.first_name`
- **Required**: ✅ Yes
- **Validation Rules**:
  - Cannot be empty
  - Minimum 2 characters
  - Only letters, spaces, hyphens (-), and apostrophes (') allowed
  - Regex: `/^[a-zA-Z\s'-]+$/`
- **Error Messages**:
  - "First name is required"
  - "First name must be at least 2 characters"
  - "First name can only contain letters, spaces, hyphens, and apostrophes"
- **Examples**:
  - ✅ Valid: `John`, `Mary-Anne`, `O'Brien`, `Jean Paul`
  - ❌ Invalid: `John123`, `J`, `John@Smith`

#### 4. Last Name
- **Field**: `registrationData.last_name`
- **Required**: ✅ Yes
- **Validation Rules**:
  - Same as First Name
- **Error Messages**:
  - "Last name is required"
  - "Last name must be at least 2 characters"
  - "Last name can only contain letters, spaces, hyphens, and apostrophes"

### Optional Fields

#### 5. Phone Number
- **Field**: `companyProfile.phone`
- **Required**: ❌ No (Optional)
- **Validation Rules** (if provided):
  - Only digits, spaces, hyphens, plus signs, and parentheses allowed
  - Regex: `/^[\d\s\-\+\(\)]+$/`
  - Must have at least 10 digits (excluding formatting characters)
- **Error Messages**:
  - "Please enter a valid phone number"
  - "Phone number must have at least 10 digits"
- **Examples**:
  - ✅ Valid: `+1 (555) 123-4567`, `555-123-4567`, `5551234567`
  - ❌ Invalid: `123` (too short), `phone-number` (letters)

#### 6. Job Title
- **Field**: `companyProfile.job_title`
- **Required**: ❌ No (Optional)
- **Validation Rules**: None
- **Examples**: `HR Manager`, `Recruiter`, `CEO`

---

## Tab 2: Company Profile

### Required Fields

#### 1. Company Description
- **Field**: `companyProfile.description`
- **Required**: ✅ Yes
- **Validation Rules**:
  - Cannot be empty
  - Minimum 50 characters
  - Maximum 1000 characters
  - Character counter displayed in real-time
- **Error Messages**:
  - "Company description is required"
  - "Description must be at least 50 characters"
  - "Description must not exceed 1000 characters"
- **UI Feature**: Character counter shows `X/1000 characters`

#### 2. Industry
- **Field**: `companyProfile.industry`
- **Required**: ✅ Yes
- **Validation Rules**:
  - Must select a valid option (not empty string)
- **Error Messages**:
  - "Please select an industry"
- **Options**:
  - Technology
  - Healthcare
  - Education
  - Finance
  - Manufacturing
  - Retail
  - Non-Profit
  - Other

#### 3. Company Size
- **Field**: `companyProfile.company_size`
- **Required**: ✅ Yes
- **Validation Rules**:
  - Must select a valid option (not empty string)
- **Error Messages**:
  - "Please select company size"
- **Options**:
  - Startup (1-10)
  - Small (11-50)
  - Medium (51-200)
  - Large (201-1000)
  - Enterprise (1000+)

#### 4. Location
- **Field**: `companyProfile.location`
- **Required**: ✅ Yes
- **Validation Rules**:
  - Cannot be empty
- **Error Messages**:
  - "Location is required"
- **Examples**: `San Francisco, CA`, `New York, NY`, `Remote`

### Optional Fields

#### 5. Website
- **Field**: `companyProfile.website`
- **Required**: ❌ No (Optional)
- **Validation Rules** (if provided):
  - Must be a valid URL
  - Must start with `http://` or `https://`
  - URL validation using `new URL()` constructor
- **Error Messages**:
  - "Website must start with http:// or https://"
  - "Please enter a valid website URL (e.g., https://example.com)"
- **Examples**:
  - ✅ Valid: `https://company.com`, `http://www.startup.io`
  - ❌ Invalid: `company.com` (missing protocol), `ftp://site.com` (wrong protocol)

#### 6. Remote Work Policy
- **Field**: `companyProfile.remote_policy`
- **Required**: ❌ No (Has default value)
- **Default**: `flexible`
- **Options**:
  - Fully Remote
  - Hybrid
  - On-Site
  - Flexible

#### 7. Founded Year
- **Field**: `companyProfile.founded_year`
- **Required**: ❌ No (Optional)
- **Validation Rules** (if provided):
  - Must be a valid number
  - Must be between 1800 and current year (2025)
- **Error Messages**:
  - "Please enter a valid year"
  - "Year must be between 1800 and 2025"
- **Examples**:
  - ✅ Valid: `2020`, `1995`, `1850`
  - ❌ Invalid: `2030` (future), `1700` (too old), `abc` (not a number)

#### 8. Work Environment
- **Field**: `companyProfile.work_environment`
- **Required**: ❌ No (Optional)
- **Type**: Array of strings (multi-select checkboxes)
- **Options**:
  - collaborative
  - innovative
  - supportive
  - flexible
  - diverse

#### 9. Benefits
- **Field**: `companyProfile.benefits`
- **Required**: ❌ No (Optional)
- **Type**: Array of strings (multi-select checkboxes)
- **Options**:
  - health_insurance - Health Insurance
  - dental - Dental & Vision
  - 401k - 401(k) Matching
  - pto - Generous PTO
  - wellness - Wellness Programs
  - learning - Learning & Development
  - equity - Equity/Stock Options
  - parental - Parental Leave

---

## Tab 3: Preview

### Validation
- No new fields to validate
- Runs complete validation of both previous tabs before final submission
- If validation fails, redirects user to the appropriate tab with errors

---

## Validation Flow

### Navigation Between Tabs

#### From "Create Account" → "Company Profile"
1. User clicks "Next: Company Profile →" button
2. System calls `handleNextToProfile()`
3. System runs `validateRegisterTab()`
4. If validation passes: Navigate to Profile tab
5. If validation fails: Display error messages, stay on Register tab

#### From "Company Profile" → "Preview"
1. User clicks "Preview Profile →" button
2. System calls `handleNextToPreview()`
3. System runs `validateProfileTab()`
4. If validation passes: Navigate to Preview tab
5. If validation fails: Display error messages, stay on Profile tab

#### Final Submission
1. User clicks "Complete Registration ✓" button
2. System calls `submitRegistration()`
3. System runs both `validateRegisterTab()` and `validateProfileTab()`
4. If Register tab invalid: Show alert, navigate to Register tab
5. If Profile tab invalid: Show alert, navigate to Profile tab
6. If all valid: Submit data to backend

---

## Visual Feedback

### Valid Field State
- **Border**: Green (`border-green-200`)
- **Focus**: Green border and ring (`focus:border-green-500 focus:ring-green-100`)
- **No error message displayed**

### Invalid Field State
- **Border**: Red (`border-red-500`)
- **Focus**: Red border and ring (`focus:border-red-500 focus:ring-red-100`)
- **Error Message**: Displayed below field with ⚠️ icon
- **Color**: Red text (`text-red-600`)
- **Format**: `⚠️ Error message here`

### Example Error Display
```
┌─────────────────────────────────────┐
│ Email Address *                     │
│ ┌─────────────────────────────────┐ │
│ │ [invalid-email]                 │ │ ← Red border
│ └─────────────────────────────────┘ │
│ ⚠️ Please enter a valid email      │ ← Error message
└─────────────────────────────────────┘
```

---

## Code Structure

### Validation Functions

```typescript
// Individual field validators
validateEmail(email: string): string | null
validateName(name: string, fieldName: string): string | null
validatePhone(phone: string): string | null
validateWebsite(website: string): string | null
validateFoundedYear(year: string): string | null
validateDescription(description: string): string | null

// Tab validators
validateRegisterTab(): boolean
validateProfileTab(): boolean

// Navigation handlers
handleNextToProfile(): void
handleNextToPreview(): void
submitRegistration(): Promise<void>
```

### State Management

```typescript
// Error state
const [errors, setErrors] = useState<ValidationErrors>({});

interface ValidationErrors {
  [key: string]: string;
}

// Example error state:
{
  email: "Please enter a valid email address",
  first_name: "First name is required",
  description: "Description must be at least 50 characters"
}
```

---

## Testing Checklist

### Register Tab Tests
- [ ] Email validation (empty, invalid format, valid)
- [ ] Company name validation (empty, too short, valid)
- [ ] First name validation (empty, too short, invalid characters, valid)
- [ ] Last name validation (empty, too short, invalid characters, valid)
- [ ] Phone validation (optional, invalid format, too short, valid)
- [ ] Navigation blocked when fields invalid
- [ ] Navigation allowed when all fields valid

### Profile Tab Tests
- [ ] Description validation (empty, too short, too long, valid)
- [ ] Industry validation (empty, valid)
- [ ] Company size validation (empty, valid)
- [ ] Location validation (empty, valid)
- [ ] Website validation (optional, invalid format, missing protocol, valid)
- [ ] Founded year validation (optional, invalid year, too old, future, valid)
- [ ] Character counter display for description
- [ ] Navigation blocked when fields invalid
- [ ] Navigation allowed when all fields valid

### Final Submission Tests
- [ ] Validates all tabs before submission
- [ ] Redirects to Register tab if invalid
- [ ] Redirects to Profile tab if invalid
- [ ] Submits successfully when all valid
- [ ] Shows success message after submission

### Visual Tests
- [ ] Red borders appear on invalid fields
- [ ] Error messages display correctly
- [ ] Green borders on valid fields
- [ ] Error messages disappear when field becomes valid
- [ ] Character counter updates in real-time

---

## Browser Compatibility

The validation system uses:
- **Regex**: Supported in all modern browsers
- **URL Constructor**: Supported in all modern browsers
- **Template Literals**: ES6 feature, supported in all modern browsers
- **Optional Chaining**: Modern browsers (can use polyfill if needed)

---

## Future Enhancements

1. **Real-time Validation**: Validate fields on blur or as user types
2. **Password Strength Meter**: If password is added back
3. **Email Verification**: Check if email already exists
4. **Location Autocomplete**: Google Maps integration
5. **Custom Error Tooltips**: Better UX for error display
6. **Accessibility**: ARIA labels for screen readers
7. **Internationalization**: Multi-language error messages
8. **Analytics**: Track which fields cause most errors

