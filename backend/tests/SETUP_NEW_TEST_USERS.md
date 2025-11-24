# Setup New Test Users

## What Changed

We've added 2 new permanent test users to avoid Supabase rate limits:

- `test.jobseeker2@yourapp.com` (job_seeker_2)
- `test.employer2@yourapp.com` (employer_2)

These users are needed for cross-user authorization tests (e.g., testing that User A cannot access User B's data).

## Setup Instructions

### 1. Create the New Users in Supabase

Run the setup script to create all 5 test users:

```bash
cd backend
python -m tests.setup_test_users
```

Expected output:
```
============================================================
🔧 Creating Permanent Test Users in Supabase
============================================================

✅ Created job_seeker   | test.jobseeker@yourapp.com
✅ Created job_seeker   | test.jobseeker2@yourapp.com
✅ Created employer     | test.employer@yourapp.com
✅ Created employer     | test.employer2@yourapp.com
✅ Created admin        | test.admin@yourapp.com

============================================================
✅ Setup Complete!
============================================================
```

If you see "ℹ Already exists" for some users, that's fine - it means they were already created.

### 2. Verify Tests Pass

Run the updated test:

```bash
cd backend
python -m pytest tests/test_application_workflow.py -v
```

All tests should pass without any rate limit issues!

### 3. Optional: Update Other RBAC Tests

Many RBAC tests currently use `create_temp_user` but could be updated to use the new permanent fixtures. This would make tests faster and more reliable.

**Files that could be optimized:**
- `tests/auth/test_applications_rbac.py` (5 uses of create_temp_user)
- `tests/auth/test_jobs_rbac.py` (1 use)
- `tests/auth/test_job_seeker_profiles_rbac.py` (multiple uses)
- `tests/auth/test_employer_profiles_rbac.py` (multiple uses)
- `tests/auth/test_saved_jobs_rbac.py` (2 uses)
- `tests/auth/test_resumes_rbac.py` (2 uses)

**When to still use `create_temp_user`:**
- Pagination tests (need 3+ users)
- Search/filter tests (need diverse user data)
- Complex E2E workflows that simulate many users

## Benefits

✅ **No more rate limit issues** - No dynamic user creation
✅ **Faster tests** - No user creation overhead  
✅ **More reliable** - Tests won't randomly fail or skip
✅ **Reusable** - Same users across all test runs
✅ **Cleaner** - Follows existing pattern for permanent users

## Test User List

| Email | Password | Account Type | Purpose |
|-------|----------|--------------|---------|
| test.jobseeker@yourapp.com | TestJobSeeker123! | job_seeker | Primary job seeker |
| test.jobseeker2@yourapp.com | TestJobSeeker2123! | job_seeker | Secondary for cross-user tests |
| test.employer@yourapp.com | TestEmployer123! | employer | Primary employer |
| test.employer2@yourapp.com | TestEmployer2123! | employer | Secondary for cross-user tests |
| test.admin@yourapp.com | TestAdmin123! | admin | Admin tests |

## Troubleshooting

**Error: "Cannot login test job seeker 2"**
- Make sure you ran `python -m tests.setup_test_users`
- Check that the user was created in Supabase Dashboard > Authentication > Users
- Verify your `.env` has correct Supabase credentials

**Tests still failing with rate limits**
- Make sure you updated the test to use `job_seeker_2_with_profile` fixture
- Check that you're not still using `create_temp_user` in the test

**User already exists error**
- This is normal - the script will show "ℹ Already exists" for existing users
- No action needed

