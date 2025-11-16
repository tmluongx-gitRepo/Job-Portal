# N8N Webhook Integration - Implementation Summary

## What Was Implemented

The webhook integration has been successfully implemented to send enriched data to n8n for multiple events:
1. **Application Created** - When a job seeker applies to a job
2. **Interview Scheduled** - When an employer schedules an interview
3. **Interview Updated** - When an employer updates or reschedules an interview
4. **Application Status Changed** - When an employer/admin changes application status

This eliminates the need for n8n to make additional API calls.

## Supported Webhook Events

### Event 1: Application Created (`application_created`)
Triggered when a job seeker submits a new application.

### Event 2: Interview Scheduled (`interview_scheduled`)
Triggered when an employer schedules an interview for an application.

### Event 3: Interview Updated (`interview_updated`)
Triggered when an employer updates or reschedules an existing interview.

### Event 4: Application Status Changed (`application_status_changed`)
Triggered when an employer or admin changes the status of an application (e.g., "Under Review", "Rejected", "Offer Extended", "Accepted").

## Changes Made

### 1. Configuration (`backend/app/config.py`)
Added two new settings:
- `N8N_WEBHOOK_URL`: The full webhook URL for n8n (defaults to empty string)
- `N8N_WEBHOOK_ENABLED`: Boolean flag to enable/disable webhook triggers (defaults to False)

### 2. Webhook Service (`backend/app/services/webhook_service.py`)
Created a new service module with:
- `trigger_application_webhook()` function that sends enriched application data to n8n
- `trigger_interview_webhook()` function that sends enriched interview data to n8n
- `trigger_interview_updated_webhook()` function that sends interview update/reschedule data to n8n
- `trigger_application_status_changed_webhook()` function that sends application status change data to n8n
- Fire-and-forget async HTTP POST using httpx
- Graceful error handling (logs errors but doesn't raise exceptions)
- Automatic skip if webhook is disabled or URL not configured

**Application Webhook Payload Structure:**
```json
{
  "event": "application_created",
  "application": {
    "id": "...",
    "status": "Application Submitted",
    "applied_date": "2024-01-01T12:00:00Z",
    "notes": "..."
  },
  "job": {
    "id": "...",
    "title": "Software Engineer",
    "company": "Company Name",
    "location": "City, State",
    "job_type": "Full-time",
    "description": "...",
    "salary_min": 80000,
    "salary_max": 120000
  },
  "job_seeker": {
    "id": "...",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "location": "City, State",
    "skills": ["Python", "JavaScript"],
    "experience_years": 5
  }
}
```

**Interview Webhook Payload Structure:**
```json
{
  "event": "interview_scheduled",
  "interview": {
    "id": "...",
    "interview_type": "Phone Screen",
    "scheduled_date": "2024-01-15T10:00:00Z",
    "duration_minutes": 60,
    "timezone": "America/New_York",
    "location": "https://zoom.us/j/...",
    "interviewer_name": "John Smith",
    "interviewer_email": "john@company.com",
    "interviewer_phone": "+1234567890",
    "notes": "Please prepare your portfolio"
  },
  "job": {
    "id": "...",
    "title": "Software Engineer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "job_type": "Full-time"
  },
  "job_seeker": {
    "id": "...",
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@example.com",
    "phone": "+0987654321"
  },
  "application": {
    "id": "...",
    "status": "interview_scheduled"
  }
}
```

**Interview Update Webhook Payload Structure:**
```json
{
  "event": "interview_updated",
  "update_type": "rescheduled",
  "interview": {
    "id": "...",
    "interview_type": "Phone Screen",
    "scheduled_date": "2024-01-20T14:00:00Z",
    "duration_minutes": 60,
    "timezone": "America/New_York",
    "location": "https://zoom.us/j/...",
    "interviewer_name": "John Smith",
    "interviewer_email": "john@company.com",
    "interviewer_phone": "+1234567890",
    "notes": "Please prepare your portfolio",
    "status": "Rescheduled",
    "rescheduled_from": "2024-01-15T10:00:00Z"
  },
  "job": {
    "id": "...",
    "title": "Software Engineer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "job_type": "Full-time"
  },
  "job_seeker": {
    "id": "...",
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@example.com",
    "phone": "+0987654321"
  },
  "application": {
    "id": "...",
    "status": "interview_scheduled"
  }
}
```

**Application Status Change Webhook Payload Structure:**
```json
{
  "event": "application_status_changed",
  "old_status": "Application Submitted",
  "new_status": "Under Review",
  "application": {
    "id": "...",
    "status": "Under Review",
    "applied_date": "2024-01-01T12:00:00Z",
    "notes": "...",
    "next_step": "We will review your application within 3-5 business days",
    "rejection_reason": null
  },
  "job": {
    "id": "...",
    "title": "Software Engineer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "job_type": "Full-time"
  },
  "job_seeker": {
    "id": "...",
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@example.com",
    "phone": "+0987654321"
  }
}
```

### 3. Application Creation Endpoint (`backend/app/api/routes/applications.py`)
- Added import for `asyncio` and `trigger_application_webhook`
- Integrated webhook trigger after successful application creation
- Uses `asyncio.create_task()` for non-blocking execution
- Reuses job and profile data already fetched during validation

### 4. Interview Scheduling Endpoint (`backend/app/api/routes/interviews.py`)
- Added import for `asyncio` and `trigger_interview_webhook`
- Integrated webhook trigger after successful interview creation
- Fetches job seeker profile for webhook payload
- Uses `asyncio.create_task()` for non-blocking execution
- Reuses job and application data already fetched during authorization

### 5. Interview Update Endpoint (`backend/app/api/routes/interviews.py`)
- Added import for `trigger_interview_updated_webhook`
- Integrated webhook trigger after successful interview update
- Determines update type ("rescheduled" or "modified")
- Fetches all related data (job, application, job seeker profile)
- Uses `asyncio.create_task()` for non-blocking execution
- Includes previous scheduled date if rescheduled

### 6. Application Update Endpoint (`backend/app/api/routes/applications.py`)
- Added import for `trigger_application_status_changed_webhook`
- Integrated webhook trigger after successful status change
- Only triggers when employer/admin changes status (not job seeker updates)
- Detects status changes by comparing old vs new status
- Fetches all related data (job, job seeker profile)
- Uses `asyncio.create_task()` for non-blocking execution

### 6. N8N Workflow Files

**Current Workflow**: `n8n_JP_combined_notifications.json` (in project root)

This single workflow handles all notification types:
- Application created confirmations
- Interview scheduled confirmations
- Interview update/reschedule notifications
- Application status change notifications

**Note**: Previous individual workflow files (`n8n_JP_application_received.json`, `n8n_JP_interview_scheduled.json`, `n8n_JP_interview_updated.json`) have been consolidated into the combined workflow for easier management and maintenance.

### 7. N8N Combined Workflow (`n8n_JP_combined_notifications.json`)
**This is the recommended workflow** - handles all 4 events with a single webhook:
- **Webhook node**: Single entry point for all events
- **Switch node (v3.3)**: Routes based on `$json.event` field
  - Output 1: `application_created` → Application confirmation email
  - Output 2: `interview_scheduled` → Interview confirmation email
  - Output 3: `interview_updated` → Interview update email
  - Output 4: `application_status_changed` → Status change email
- **Four Gmail nodes**: One for each event type with HTML formatting
- **Email features**:
  - HTML formatting with `<br>` tags for proper line breaks
  - Conditional content based on data availability
  - Status-specific messages (Rejected, Offer Extended, Accepted, Under Review)
  - Dynamic subject lines
  - Job details and application date

**Note**: Individual workflow files have been consolidated into this single combined workflow for easier management.

## Configuration Instructions

### Step 1: Add Environment Variables
Add these variables to your `.env` file in the project root:

```bash
# N8N Webhook Integration
# Production n8n cloud webhook URL (handles all events via Switch node routing)
N8N_WEBHOOK_URL=https://your-n8n-instance.app.n8n.cloud/webhook/your-webhook-id
N8N_WEBHOOK_ENABLED=true
```

**Note**: 
- n8n is running on **n8n Cloud** (not in a local Docker container)
- The same webhook URL is used for all events (application created, interview scheduled, interview updated, application status changed)
- The combined workflow uses a **Switch node** to route events based on the `event` field in the payload
- Get your production webhook URL from your n8n cloud workflow after importing

### Step 2: Install httpx (if not already installed)
The webhook service uses `httpx` for async HTTP requests. Add to `backend/requirements.txt` if not present:

```
httpx>=0.24.0
```

Then reinstall dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Import N8N Workflow
1. Log in to your **n8n Cloud** instance
2. Go to Workflows → Import from File
3. Import `n8n_JP_combined_notifications.json` from the project root
4. Configure the workflow:
   - **Webhook node**: The webhook will automatically get a production URL
   - **Gmail nodes**: Configure Gmail OAuth2 credentials for all 4 email nodes
   - **Switch node**: Verify it's using typeVersion 3.3 (required for n8n v1.117.2+)
5. Activate the workflow
6. Copy the **production webhook URL** from the Webhook node
7. Update your `.env` file with the production URL:
   ```bash
   N8N_WEBHOOK_URL=https://your-n8n-instance.app.n8n.cloud/webhook/your-webhook-id
   ```

**Important Notes:**
- n8n is running on **n8n Cloud**, not in a local Docker container
- The Switch node must use **typeVersion 3.3** for compatibility with n8n v1.117.2
- Each Gmail node needs Gmail OAuth2 credentials configured
- HTML formatting (`<br>` tags) is used for proper email line breaks
- Conditional content uses ternary operators for dynamic messages
- The production webhook URL must be accessible from your backend server

### Step 4: Restart Backend
Restart the FastAPI backend to load the new configuration:

```bash
docker-compose restart backend
```

Or if running locally:
```bash
cd backend
uvicorn app.main:app --reload
```

**Note**: The backend will now send webhook requests to your n8n Cloud instance.

## Testing

### Test Application Webhook
1. Create a new job application through the API or frontend
2. Check backend logs for webhook trigger confirmation:
   ```
   INFO: Successfully triggered n8n webhook for application <id>
   ```
3. Check n8n workflow execution history
4. Verify the applicant receives the confirmation email

### Test Interview Webhook
1. Schedule an interview for an existing application
2. Check backend logs for webhook trigger confirmation:
   ```
   INFO: Successfully triggered n8n webhook for interview <id>
   ```
3. Check n8n workflow execution history
4. Verify the job seeker receives the interview confirmation email with all details

### Test Interview Update Webhook
1. Update or reschedule an existing interview
2. Check backend logs for webhook trigger confirmation:
   ```
   INFO: Successfully triggered n8n webhook for interview update <id>
   ```
3. Check n8n workflow execution history
4. Verify the job seeker receives the update notification with new details and previous date (if rescheduled)

### Test Application Status Change Webhook
1. Update an application status (as employer/admin)
2. Check backend logs for webhook trigger confirmation:
   ```
   INFO: Successfully triggered n8n webhook for application status change <id>
   ```
3. Check n8n workflow execution history
4. Verify the job seeker receives the status change notification with old status, new status, and contextual information

### Troubleshooting

**Webhook not triggering:**
- Verify `N8N_WEBHOOK_ENABLED=true` in `.env`
- Verify `N8N_WEBHOOK_URL` is set correctly with your n8n Cloud production URL
- Ensure the backend server can reach n8n Cloud (check firewall/network settings)
- Check backend logs for errors or timeout messages

**N8N workflow fails:**
- Verify the workflow is active in your n8n Cloud instance
- Check that Gmail credentials are configured
- Verify the webhook payload structure matches expectations
- Check n8n execution logs in the cloud dashboard for details
- Ensure your n8n Cloud plan supports the required executions

**Email not sending:**
- Verify Gmail OAuth2 credentials in n8n
- Check Gmail API quotas
- Verify email addresses are valid

## Benefits

✅ **Single workflow** - One combined workflow handles all notification types
✅ **Faster n8n workflows** - No additional API calls needed for any event type
✅ **Simpler n8n workflows** - Direct webhook-to-email routing
✅ **Better performance** - Fire-and-forget async execution doesn't slow down API responses
✅ **More reliable** - All data validated before webhook trigger
✅ **Easier maintenance** - Single workflow to manage and update
✅ **Graceful degradation** - Operations succeed even if webhook fails
✅ **Flexible routing** - Single `event` field enables easy routing via Switch node
✅ **Multiple events supported** - Application created, interview scheduled, interview updated, and application status changed
✅ **Update type tracking** - Distinguishes between rescheduled and modified interviews
✅ **Status change notifications** - Keeps job seekers informed of application progress
✅ **Smart triggering** - Only sends status change emails when employer/admin updates (not job seeker edits)
✅ **HTML email formatting** - Properly formatted emails with line breaks and conditional content

## Event Routing in N8N

You can use the `event` field to route different webhook events to different actions:

```javascript
// In n8n Switch node, use expression:
{{ $json.event }}

// Routes:
// - "application_created" → Send application confirmation
// - "interview_scheduled" → Send interview confirmation
// - "interview_updated" → Send interview update/reschedule notification
// - "application_status_changed" → Send status change notification
```

For interview updates, you can also check the `update_type` field:
```javascript
// Check if interview was rescheduled vs just modified:
{{ $json.update_type === 'rescheduled' }}
```

For application status changes, you can customize messages based on the new status:
```javascript
// Check the new status:
{{ $json.new_status === 'Rejected' }}
{{ $json.new_status === 'Offer Extended' }}
{{ $json.new_status === 'Accepted' }}
```

## Future Enhancements

Potential improvements you could make:
- Add webhook triggers for more events:
  - `interview_cancelled` - When interview is cancelled
  - `application_withdrawn` - When job seeker withdraws application
  - `interview_completed` - When interview is marked complete with feedback
- Add webhook retry logic with exponential backoff
- Add webhook signature validation for security
- Add support for multiple webhook URLs (different URLs for different events)
- Add webhook event filtering/routing at application level
- Add webhook delivery tracking and analytics


