# Job Portal Frontend

A modern Next.js application for the Job Portal platform, featuring company registration, job browsing, and more.

## Tech Stack

- **Framework:** Next.js 15
- **React:** 19
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Build Tool:** Turbopack (for fast development)

## Features

### ✨ Company Registration (`/company-registration`)

Complete multi-step registration system for employers.

**Features:**

- Multi-step form with navigation guards
- Comprehensive field validation
- Real-time error feedback
- Character counter for description
- Email format validation
- Phone number validation
- Website URL validation
- Year range validation

**Validation Coverage:**

- ✅ Email address format
- ✅ Name fields (letters, spaces, hyphens, apostrophes)
- ✅ Phone number (10+ digits)
- ✅ Company description (50-1000 characters)
- ✅ Required dropdowns (Industry, Company Size)
- ✅ Website URL (http/https protocol)
- ✅ Founded year (1800-2025 range)

### 📋 Jobs Portal (`/jobs`)

Browse and search for job opportunities.

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── company-registration/
│   │   │   └── page.tsx          # Company registration form
│   │   ├── jobs/
│   │   │   └── page.tsx          # Jobs listing page
│   │   ├── layout.tsx            # Root layout
│   │   ├── page.tsx              # Home page
│   │   └── globals.css           # Global styles
│   └── ...
├── public/                        # Static assets
├── package.json                   # Dependencies
├── tsconfig.json                  # TypeScript config
├── tailwind.config.ts             # Tailwind config
├── next.config.mjs                # Next.js config
└── README.md                      # This file
```

## Environment Setup

### Development (Docker)

The application runs in a Docker container. See the main [README.md](/README.md) for full setup instructions.

### Local Development (Without Docker)

If you want to run the frontend locally without Docker:

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

**Environment Variables:**

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

## Available Scripts

| Script | Command         | Description                             |
| ------ | --------------- | --------------------------------------- |
| Dev    | `npm run dev`   | Start development server with Turbopack |
| Build  | `npm run build` | Build for production                    |
| Start  | `npm start`     | Start production server                 |
| Lint   | `npm run lint`  | Run ESLint                              |

## Routes

| Path                    | Component                           | Description               |
| ----------------------- | ----------------------------------- | ------------------------- |
| `/`                     | `app/page.tsx`                      | Home page with navigation |
| `/jobs`                 | `app/jobs/page.tsx`                 | Browse jobs               |
| `/company-registration` | `app/company-registration/page.tsx` | Employer registration     |

## Development Guidelines

### Code Style

- Use TypeScript for all new files
- Follow React best practices
- Use functional components with hooks
- Implement proper error handling
- Add JSDoc comments for complex functions

### Component Structure

```typescript
'use client'; // If using client-side features

import React, { useState } from 'react';

interface Props {
  // Define props
}

export default function ComponentName({ props }: Props): React.JSX.Element {
  // Component logic
  return (
    // JSX
  );
}
```

### Validation Pattern

For forms with validation, follow the pattern used in company registration:

1. Define error state: `useState<ValidationErrors>({})`
2. Create validation functions that return `string | null`
3. Display errors conditionally with visual feedback
4. Clear errors when field becomes valid

### Styling Guidelines

- Use Tailwind CSS utility classes
- Follow mobile-first approach
- Maintain consistent color scheme:
  - Primary: Green (`green-500`, `green-600`, `green-700`)
  - Error: Red (`red-500`, `red-600`)
  - Success: Green
- Use responsive breakpoints: `sm:`, `md:`, `lg:`, `xl:`

## Testing

### Test Results

See [TEST_RESULTS.md](./TEST_RESULTS.md) for detailed test coverage and results.

### Manual Testing Checklist

Before committing changes:

- [ ] Test on Chrome, Firefox, and Safari
- [ ] Test responsive design (mobile, tablet, desktop)
- [ ] Verify all forms validate correctly
- [ ] Check console for errors
- [ ] Test navigation between pages
- [ ] Verify API integration works
- [ ] Check accessibility (keyboard navigation, screen readers)

### Running Tests

```bash
# Run linter
npm run lint

# Fix linting issues
npm run lint --fix
```

## API Integration

### Backend Connection

The frontend connects to the FastAPI backend at `NEXT_PUBLIC_API_URL`.

Example API call:

```typescript
const response = await fetch(
  `${process.env.NEXT_PUBLIC_API_URL}/api/v1/endpoint`,
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }
);

const result = await response.json();
```

### Authentication

Authentication flow to be implemented:

- Login/Logout
- JWT token management
- Protected routes
- Session persistence

## Deployment

### Docker Deployment (Recommended)

From project root:

```bash
# Restart frontend container
docker compose restart frontend

# Or rebuild and restart
docker compose build frontend
docker compose up -d frontend
```

### Production Build

```bash
# Build optimized production bundle
npm run build

# Preview production build locally
npm start
```

### Environment Variables for Production

Ensure these are set in production:

```env
NEXT_PUBLIC_API_URL=https://api.yourcompany.com
NEXT_PUBLIC_BASE_URL=https://yourcompany.com
NODE_ENV=production
```

## Performance Optimization

The application uses:

- Next.js automatic code splitting
- Image optimization with `next/image`
- Font optimization
- Static generation where possible
- Client-side routing for fast navigation

## Accessibility

- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Focus management
- Color contrast compliance

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Issue: Port 3000 already in use

```bash
# Find process using port 3000
lsof -i :3000  # Mac/Linux
netstat -ano | findstr :3000  # Windows

# Kill the process or use different port
PORT=3001 npm run dev
```

### Issue: Module not found errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Issue: Build errors after pulling latest code

```bash
# Clean Next.js cache
rm -rf .next
npm run build
```

### Issue: Styles not applying

```bash
# Restart dev server
# Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)
# Check Tailwind config
```

## Documentation

- [Main Project README](/README.md) - Setup and getting started
- [Routing Guide](/ROUTING_GUIDE.md) - Application routes
- [Validation Documentation](/VALIDATION_DOCUMENTATION.md) - Form validation rules
- [Deployment Guide](/DEPLOYMENT_GUIDE.md) - Deployment instructions
- [Test Results](./TEST_RESULTS.md) - Testing documentation

## Contributing

1. Create feature branch from `Dev`
2. Make changes
3. Test thoroughly
4. Create pull request to `Dev`
5. Wait for review

## Support

For issues or questions:

- Check troubleshooting section above
- Review documentation
- Check Docker logs: `docker compose logs frontend`
- Contact team lead

---

**Version:** 1.0.0  
**Last Updated:** November 10, 2025  
**Maintainer:** Development Team
