# 🚀 Quick Start: Testing the Signup & Company Registration Flow

## ✅ What's Ready

- ✅ Signup page integrated with backend API
- ✅ Form validation and error handling
- ✅ Employer profile checking
- ✅ Automatic redirect to company registration
- ✅ Company registration page with validation

## 🧪 Test in 3 Steps

### Step 1: Open Signup Page
```
http://localhost:3000/signup
```

### Step 2: Fill Out Form (Employer Account)
- **First Name**: Jane
- **Last Name**: Smith
- **Email**: jane@company.com
- **Password**: password123
- **Confirm Password**: password123
- **Account Type**: ✓ **Employer** (click the right option)
- **Terms**: ✓ Check the box

### Step 3: Click "Join Career Harmony"

**What Happens**:
1. Loading spinner appears
2. User created in database
3. Checks for employer profile (won't find one)
4. **Redirects to**: http://localhost:3000/company-registration
5. Fill out company information!

## 🎯 Expected Results

### ✅ Success Indicators
- No error messages
- Smooth transition to company-registration page
- Form loads with all fields ready to fill
- Can see "Create Account", "Company Profile", "Preview" tabs

### ❌ Common Issues

**"User already exists"**
- Solution: Use a different email address
- Or: Check backend to delete the test user

**"An unexpected error occurred"**
- Solution: Make sure backend is running
- Check: `docker compose ps` (on host machine)
- Start: `docker compose up backend`

**Form won't submit**
- Check: All required fields filled?
- Check: Password is 8+ characters?
- Check: Passwords match?
- Check: Terms checkbox is checked?

## 📸 Screenshot Checklist

When testing, you should see:

1. **Signup Page**
   - [ ] Two account type options (Job Seeker / Employer)
   - [ ] All form fields visible
   - [ ] Green Career Harmony theme

2. **During Submission**
   - [ ] Loading spinner in button
   - [ ] Button says "Creating Account..."
   - [ ] Button is disabled

3. **After Success**
   - [ ] Page redirects to company-registration
   - [ ] Sees 3 tabs: Create Account, Company Profile, Preview
   - [ ] Can fill out company information

4. **Company Registration Form**
   - [ ] Email field pre-filled (if implemented)
   - [ ] Can enter company name
   - [ ] Can fill all required fields
   - [ ] "Complete Registration" button disabled until ready

## 🔧 Troubleshooting

### Backend Not Running?
```bash
# On your host machine (not in container)
docker compose up backend

# Or start all services
docker compose up
```

### Frontend Not Running?
```bash
# Inside devcontainer or host
cd /workspace/frontend
bun run dev
```

### Can't See Changes?
```bash
# Clear cache and restart
cd /workspace/frontend
rm -rf .next
bun run dev
```

### Database Issues?
```bash
# Restart all services
docker compose down
docker compose up
```

## 📝 Quick Test Script

Copy and paste this test data:

**Job Seeker Test**:
```
First: John
Last: Doe
Email: john.doe@test.com
Password: testpass123
Account: Job Seeker
```

**Employer Test 1**:
```
First: Jane
Last: Smith
Email: jane.smith@company.com
Password: testpass123
Account: Employer ✓
```

**Employer Test 2** (different email):
```
First: Bob
Last: Johnson
Email: bob@techcorp.com
Password: testpass123
Account: Employer ✓
```

## ✅ Validation Tests

Try these to see error messages work:

1. **Missing email**: Leave email blank → "Email is required"
2. **Invalid email**: Enter "notanemail" → "Please enter a valid email"
3. **Short password**: Enter "123" → "Password must be at least 8 characters"
4. **Mismatched passwords**: Different passwords → "Passwords do not match"
5. **No terms**: Uncheck terms → "You must agree to the terms"
6. **Duplicate email**: Use same email twice → "Account already exists"

## 🎉 Success Criteria

You'll know it works when:
- ✅ Can create job seeker accounts (redirect to /dashboard)
- ✅ Can create employer accounts (redirect to /company-registration)
- ✅ Company registration form loads successfully
- ✅ Can fill out and submit company information
- ✅ Error messages show for validation issues
- ✅ Duplicate email is detected and blocked
- ✅ Loading states appear during submission

---

## 🆘 Need Help?

Check these files:
- **Full Details**: `IMPLEMENTATION_SUMMARY.md`
- **Technical Guide**: `SIGNUP_AUTHENTICATION_IMPLEMENTATION.md`
- **API Reference**: `frontend/API_USAGE_GUIDE.md`

Or check the backend API docs: http://localhost:8000/docs

---

**Ready?** Go to http://localhost:3000/signup and start testing! 🚀





