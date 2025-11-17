# Company Registration Feature - Deployment Guide

## 🚀 Deployment Instructions

### Prerequisites
- Docker and Docker Compose installed
- Access to the host machine (not inside dev container)

### Quick Deployment

#### Option 1: Simple Restart (Recommended)
From your **host machine**, navigate to the project root and run:

```bash
docker compose restart frontend
```

This will restart the frontend container and pick up all file changes.

#### Option 2: Full Rebuild
If Option 1 doesn't work or you want a clean rebuild:

```bash
docker compose down frontend
docker compose build frontend
docker compose up -d frontend
```

#### Option 3: Restart All Services
To restart the entire application stack:

```bash
docker compose restart
```

### Verify Deployment

1. **Check container status:**
   ```bash
   docker compose ps
   ```
   
   Ensure `job-portal-frontend` is running.

2. **Check logs:**
   ```bash
   docker compose logs -f frontend
   ```
   
   Look for "Ready" or "started server on" messages.

3. **Access the application:**
   - Home page: `http://localhost:3000`
   - Registration page: `http://localhost:3000/company-registration`

4. **Test the feature:**
   - Click "Register Company" button on home page
   - Verify multi-step form loads
   - Test field validations

## 📦 What's Being Deployed

### New Features
1. **Company Registration Route**
   - Route: `/company-registration`
   - Multi-step form (Create Account → Company Profile → Preview)

2. **Password Removal**
   - Removed password and confirm password fields
   - Simplified account creation

3. **Email Validation**
   - Format: `user@domain.extension`
   - Real-time validation feedback

4. **Comprehensive Field Validations**
   - 11+ validated fields across all tabs
   - Visual error feedback (red borders, error messages)
   - Navigation guards prevent proceeding with errors

### Files Modified/Created

**Frontend Application:**
- `/workspace/frontend/src/app/page.tsx` - Added "Register Company" button
- `/workspace/frontend/src/app/company-registration/page.tsx` - Main registration form

**Documentation:**
- `/workspace/ROUTING_GUIDE.md` - Routing documentation
- `/workspace/COMPANY_REGISTRATION_CHANGES.md` - Feature changes
- `/workspace/VALIDATION_DOCUMENTATION.md` - Validation rules
- `/workspace/DEPLOYMENT_GUIDE.md` - This file

## 🧪 Post-Deployment Testing

### Manual Testing Checklist

#### Home Page
- [ ] "Register Company" button is visible
- [ ] Button has green background
- [ ] Clicking button navigates to `/company-registration`

#### Registration Page - Create Account Tab
- [ ] Form renders correctly
- [ ] All fields are present (Email, Company Name, First Name, Last Name, Phone, Job Title)
- [ ] Email validation works (try invalid email)
- [ ] Name validation works (try numbers in name)
- [ ] Phone validation works (try letters in phone)
- [ ] "Next" button validates before proceeding
- [ ] Error messages display with red borders

#### Registration Page - Company Profile Tab
- [ ] Form renders correctly
- [ ] Description field has character counter
- [ ] Industry dropdown has all options
- [ ] Company size dropdown has all options
- [ ] Website validation works (try without http://)
- [ ] Founded year validation works (try future year)
- [ ] "Preview" button validates before proceeding
- [ ] "Back" button returns to previous tab

#### Registration Page - Preview Tab
- [ ] Company information displays correctly
- [ ] Work environment tags show if selected
- [ ] Benefits tags show if selected
- [ ] "Edit Profile" button returns to profile tab
- [ ] "Complete Registration" validates all tabs

#### Validation Testing
- [ ] Required fields show errors when empty
- [ ] Valid data removes errors
- [ ] Invalid data shows specific error messages
- [ ] Character counter updates in real-time
- [ ] Can't navigate with validation errors

## 🔧 Troubleshooting

### Issue: "Register Company" button not visible

**Solution 1:** Hard refresh browser
```
Windows/Linux: Ctrl + Shift + R or Ctrl + F5
Mac: Cmd + Shift + R
```

**Solution 2:** Clear browser cache

**Solution 3:** Check if frontend container is running
```bash
docker compose ps frontend
```

### Issue: Route shows "Cannot find module" error

**Solution:** Rebuild the frontend container
```bash
docker compose build frontend --no-cache
docker compose up -d frontend
```

### Issue: Changes not appearing

**Solution 1:** Check if files are properly mounted
```bash
docker compose exec frontend ls -la /app/src/app/company-registration/
```

**Solution 2:** Restart with cache clear
```bash
docker compose down
docker compose up -d
```

### Issue: Validation not working

**Solution:** Check browser console for JavaScript errors (F12)

## 📊 Monitoring

### Check Application Health

```bash
# View frontend logs
docker compose logs -f frontend

# Check if port 3000 is accessible
curl -I http://localhost:3000

# Inspect frontend container
docker compose exec frontend sh
```

### Performance Metrics

The application should:
- Load home page in < 2 seconds
- Load registration page in < 3 seconds
- Respond to validation within 100ms

## 🔄 Rollback Procedure

If issues occur, rollback to previous version:

```bash
# Stop current containers
docker compose down

# Checkout previous commit
git log --oneline  # Find commit before changes
git checkout <previous-commit-hash>

# Rebuild and restart
docker compose build frontend
docker compose up -d
```

## 📝 Environment Variables

The frontend uses these environment variables (from `.env`):

```env
FRONTEND_PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

Ensure these are set correctly in your `.env` file.

## 🎯 Success Criteria

Deployment is successful when:
- [x] Frontend container is running
- [x] Home page loads at `http://localhost:3000`
- [x] "Register Company" button is visible
- [x] Registration page loads at `http://localhost:3000/company-registration`
- [x] All form fields render correctly
- [x] Field validations work as expected
- [x] Navigation between tabs works
- [x] No console errors in browser dev tools

## 🆘 Support

If deployment issues persist:

1. **Check Docker logs:**
   ```bash
   docker compose logs frontend --tail=100
   ```

2. **Verify file changes:**
   ```bash
   git status
   git diff
   ```

3. **Check Node.js version:**
   ```bash
   docker compose exec frontend node --version
   ```

4. **Review error messages** in browser console (F12 → Console tab)

## 📚 Related Documentation

- [Routing Guide](/workspace/ROUTING_GUIDE.md)
- [Validation Documentation](/workspace/VALIDATION_DOCUMENTATION.md)
- [Feature Changes](/workspace/COMPANY_REGISTRATION_CHANGES.md)
- [Testing Results](/workspace/frontend/TEST_RESULTS.md)

---

**Last Updated:** November 10, 2025  
**Version:** 1.0.0  
**Status:** Ready for Deployment ✅

