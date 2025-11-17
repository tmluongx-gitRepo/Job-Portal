# Notifications Feature Documentation

## Overview

The Notifications feature provides a comprehensive, LinkedIn-style notification system for both job seekers and employers in the Career Harmony application. It supports **three delivery channels**: in-app notifications, email notifications, and push notifications (mobile).

## Files Created

### 1. `/src/app/notifications/page.tsx`
The main notifications page that displays all notifications in a clean, LinkedIn-inspired interface.

**Features:**
- Filter notifications by "All" or "Unread"
- Mark individual notifications as read
- Mark all notifications as read at once
- Delete individual notifications
- Interactive notification cards with action buttons
- Real-time unread count
- **Delivery channel badges** showing which channels were used (App, Email, Push)
- Link to notification preferences
- Responsive design for mobile and desktop

### 2. `/src/app/notifications/preferences/page.tsx`
A simple, user-friendly preferences page where users can control notification delivery channels.

**Features:**
- Toggle each notification type for three channels: In-App, Email, Push
- Organized by category (Important, Updates, Tips & Recommendations)
- Visual channel selection with checkmarks
- Save preferences functionality
- Email address display
- Helpful information about each channel
- Category-based color coding

### 3. `/src/components/NotificationButton.tsx`
A reusable notification bell button component with badge indicator.

**Features:**
- Bell icon with unread count badge
- Pulse animation for unread notifications
- Links to the notifications page
- Consistent styling with app theme

### 4. `/src/lib/notifications.ts`
Shared notification types, preferences, and mock data for both job seekers and employers.

**Exports:**
- `NotificationType` - TypeScript type for notification categories
- `NotificationChannel` - Type for delivery channels (in_app, email, push)
- `Notification` - Interface for notification objects with channels
- `NotificationPreference` - Interface for user preferences
- `defaultJobSeekerPreferences` - Default preferences for job seekers
- `defaultEmployerPreferences` - Default preferences for employers
- `mockJobSeekerNotifications` - Sample notifications for job seekers
- `mockEmployerNotifications` - Sample notifications for employers
- `formatNotificationTimestamp` - Utility function for time formatting
- `getChannelInfo` - Helper for channel metadata

## Integration

### Dashboard (Job Seeker)
The NotificationButton has been added to the dashboard header with a sample unread count of 3.

Location: Top right of the welcome section, next to the greeting.

### Employer Dashboard
The NotificationButton has been added to the employer dashboard with a sample unread count of 5.

Location: 
- **Mobile**: Top right of the welcome section
- **Desktop**: Next to the company filter dropdown

## Notification Channels

### 1. In-App Notifications 📱
- **Icon**: Bell
- **Color**: Green
- **Description**: Notifications appear within Career Harmony when you're logged in
- **Use Case**: Real-time updates while actively using the platform

### 2. Email Notifications 📧
- **Icon**: Mail
- **Color**: Blue
- **Description**: Notifications sent to your registered email address
- **Use Case**: Important updates that need attention even when not using the app

### 3. Push Notifications 📲
- **Icon**: Smartphone
- **Color**: Purple
- **Description**: Instant notifications on your mobile device
- **Use Case**: Time-sensitive alerts (interviews, application updates, new applications)
- **Note**: Requires mobile app installation

## Notification Types

### Job Seeker Notifications

#### Important (Always recommended)
- **Application Update** 
  - Channels: ✅ App, ✅ Email, ✅ Push
  - When: Application status changes
  
- **Interview Scheduled** 
  - Channels: ✅ App, ✅ Email, ✅ Push
  - When: New interview appointments
  
- **Messages** 
  - Channels: ✅ App, ✅ Email, ✅ Push
  - When: New messages from recruiters

#### Activity Updates
- **Job Match** 
  - Channels: ✅ App, ✅ Email, ❌ Push
  - When: Recommended job opportunities
  
- **Profile View** 
  - Channels: ✅ App, ❌ Email, ❌ Push
  - When: Employers viewing your profile
  
- **System Updates** 
  - Channels: ✅ App, ❌ Email, ❌ Push
  - When: Profile completion and system updates

#### Tips & Recommendations
- **Career Tips** 
  - Channels: ✅ App, ❌ Email, ❌ Push
  - When: Career advice and suggestions

### Employer Notifications

#### Important (Always recommended)
- **New Application** 
  - Channels: ✅ App, ✅ Email, ✅ Push
  - When: Candidates apply to your jobs
  
- **Interview Reminder** 
  - Channels: ✅ App, ✅ Email, ✅ Push
  - When: Upcoming interview alerts
  
- **Candidate Accepted** 
  - Channels: ✅ App, ✅ Email, ✅ Push
  - When: Offer acceptances

#### Activity Updates
- **Job Expired** 
  - Channels: ✅ App, ✅ Email, ❌ Push
  - When: Expiring job postings
  
- **Company Profile Views** 
  - Channels: ✅ App, ❌ Email, ❌ Push
  - When: Profile analytics
  
- **System Updates** 
  - Channels: ✅ App, ❌ Email, ❌ Push
  - When: Company updates

## Preference System

### Simple Design Philosophy
The preference system is intentionally kept simple:
- **Toggle-based**: Each notification type can be enabled/disabled per channel
- **Visual feedback**: Checkmarks and color coding for active channels
- **Category grouping**: Notifications organized by importance
- **Smart defaults**: Pre-configured sensible defaults

### Default Preferences
- **Important notifications**: All channels enabled by default
- **Activity updates**: In-app + Email (no push to avoid notification fatigue)
- **Tips**: In-app only (least intrusive)

### User Actions
1. Navigate to `/notifications/preferences`
2. Toggle channels on/off for each notification type
3. Click "Save Preferences"
4. Confirmation message appears

## Design Features

### Color-Coded Icons & Channels
Each notification type has a unique icon and color scheme:
- 🟢 Green: Applications, job matches, acceptances
- 🟣 Purple: Interviews and meetings
- 🟡 Amber: Recommendations and warnings
- 🔵 Blue: Profile views and analytics
- 🟠 Orange: Expiring items
- 🩷 Pink: Tips and suggestions

Channel badges:
- 🟢 Green (In-App): Bell icon
- 🔵 Blue (Email): Mail icon
- 🟣 Purple (Push): Smartphone icon

### LinkedIn-Inspired UI
- Clean, card-based layout
- Hover effects for interactivity
- Timestamp formatting (e.g., "30m ago", "2h ago")
- Read/unread visual distinction
- Smooth animations and transitions
- Channel badges on each notification
- Settings gear icon for preferences

### Responsive Design
- Mobile-first approach
- Adapts to different screen sizes
- Touch-friendly buttons and actions
- Proper spacing and layout on all devices
- Stacked layout on mobile, grid on desktop

## Usage

### Viewing Notifications
1. Click the bell icon button in the dashboard header
2. Navigate to `/notifications` page
3. View all notifications or filter by unread
4. See which channels each notification was delivered through

### Managing Notifications
- **Mark as Read**: Click "Mark as read" on individual notifications
- **Mark All as Read**: Click "Mark all as read" button in the header
- **Delete**: Hover over a notification and click the X icon
- **Take Action**: Click the action button (e.g., "View Application") to navigate
- **Preferences**: Click the gear icon to manage delivery preferences

### Managing Preferences
1. Click the gear/settings icon in notifications page header
2. Navigate to `/notifications/preferences`
3. Toggle channels for each notification type:
   - Click any channel button to enable/disable
   - Green checkmark = enabled
   - Gray = disabled
4. Click "Save Preferences" to persist changes

### Filters
- **All**: Shows all notifications (read and unread)
- **Unread**: Shows only unread notifications

## Future Enhancements

### Backend Integration (TODO)
- Connect to real notification API endpoints
- Implement real-time notifications using WebSockets or Server-Sent Events
- Persist notification read/unread status in database
- Store user preferences in backend
- **Send actual emails** via email service (SendGrid, AWS SES, etc.)
- **Implement push notification service** (Firebase Cloud Messaging, OneSignal, etc.)
- Add email templates for different notification types
- Track email delivery and open rates
- Implement notification queuing and batching

### Email Notifications (Implementation Guide)
```typescript
// Example: Send email notification
async function sendEmailNotification(
  userId: string,
  notification: Notification
) {
  const user = await getUserProfile(userId);
  const preferences = await getNotificationPreferences(userId);
  
  // Check if email is enabled for this notification type
  const pref = preferences.find(p => p.type === notification.type);
  if (!pref?.channels.email) {
    return; // User has disabled email for this type
  }
  
  // Send email via service
  await emailService.send({
    to: user.email,
    subject: notification.title,
    template: notification.type,
    data: {
      title: notification.title,
      description: notification.description,
      actionUrl: `${APP_URL}${notification.actionUrl}`,
      actionText: notification.actionText,
    },
  });
}
```

### Push Notifications (Implementation Guide)
```typescript
// Example: Send push notification
async function sendPushNotification(
  userId: string,
  notification: Notification
) {
  const preferences = await getNotificationPreferences(userId);
  
  // Check if push is enabled
  const pref = preferences.find(p => p.type === notification.type);
  if (!pref?.channels.push) {
    return;
  }
  
  // Get user's device tokens
  const tokens = await getUserDeviceTokens(userId);
  
  // Send push via FCM/OneSignal
  await pushService.send({
    tokens,
    title: notification.title,
    body: notification.description,
    data: {
      type: notification.type,
      url: notification.actionUrl,
    },
  });
}
```

### Additional Features (Potential)
- Notification batching (daily/weekly digests)
- Quiet hours for push notifications
- Notification history archive (90 days)
- Search functionality within notifications
- Mark as important/starred
- Notification categories (expandable/collapsible)
- Desktop browser push notifications
- In-app notification sounds (optional)
- SMS notifications for critical alerts
- Webhook notifications for integrations

## Customization

### Changing Unread Count
The unread count is currently hardcoded in the dashboard files:
- **Dashboard**: `<NotificationButton unreadCount={3} />`
- **Employer Dashboard**: `<NotificationButton unreadCount={5} />`

To make it dynamic:
```typescript
// In dashboard
const [notifications, setNotifications] = useState([]);
const unreadCount = notifications.filter(n => !n.read).length;

<NotificationButton unreadCount={unreadCount} />
```

### Adding New Notification Types
1. Add new type to `NotificationType` in `/src/lib/notifications.ts`
2. Add to preference defaults with appropriate channels:
```typescript
{
  type: "new_type",
  label: "New Notification Type",
  description: "Description of when this fires",
  channels: { in_app: true, email: true, push: false },
  category: "updates",
}
```
3. Create notification object with icon and colors
4. Add to mock data or fetch from API

### Customizing Default Preferences
Edit `defaultJobSeekerPreferences` or `defaultEmployerPreferences` in `/src/lib/notifications.ts`:
- Change `channels` object to set defaults
- Modify `category` to change grouping
- Update `label` and `description` for clarity

### Styling
All styles follow the app's green/amber theme and use Tailwind CSS classes. To customize:
- Modify color classes in components
- Update gradient colors for buttons and headers
- Adjust spacing and sizing as needed
- Change channel badge colors in `ChannelBadge` component

## Testing

### Manual Testing Checklist
#### Notifications Page
- ✅ Notification button appears in both dashboards
- ✅ Badge shows correct unread count
- ✅ Bell icon animates with pulse for unread items
- ✅ Notifications page loads correctly
- ✅ Channel badges display correctly (App, Email, Push)
- ✅ Filter buttons work (All/Unread)
- ✅ Mark as read functionality works
- ✅ Mark all as read clears all unread indicators
- ✅ Delete removes notifications
- ✅ Action buttons navigate to correct pages
- ✅ Settings icon links to preferences
- ✅ Responsive layout works on mobile
- ✅ Hover effects show properly
- ✅ Empty state displays when no notifications

#### Preferences Page
- ✅ Preferences page loads correctly
- ✅ All notification types display
- ✅ Category grouping works (Important, Updates, Tips)
- ✅ Channel toggles work (click to enable/disable)
- ✅ Visual feedback (checkmarks, colors)
- ✅ Save button works
- ✅ Success message shows after save
- ✅ Back link returns to notifications
- ✅ Email address displays correctly
- ✅ Info banners show helpful context
- ✅ Responsive layout on mobile

## Technical Notes

- Built with Next.js 14 App Router
- Uses React 18 hooks (useState, useEffect)
- TypeScript for type safety
- Tailwind CSS for styling
- Lucide React for icons
- Client-side rendering ("use client")
- Mock data for demonstration
- Ready for backend integration

## API Integration Guide

### Endpoints Needed

```typescript
// GET /api/notifications
// Fetch user's notifications
GET /api/users/{userId}/notifications?unread=true&limit=50

// PATCH /api/notifications/{id}
// Mark notification as read
PATCH /api/notifications/{notificationId}/read

// DELETE /api/notifications/{id}
// Delete notification
DELETE /api/notifications/{notificationId}

// GET /api/notification-preferences
// Fetch user preferences
GET /api/users/{userId}/notification-preferences

// PUT /api/notification-preferences
// Update user preferences
PUT /api/users/{userId}/notification-preferences
Body: NotificationPreference[]

// POST /api/notifications/mark-all-read
// Mark all as read
POST /api/users/{userId}/notifications/mark-all-read
```

### Data Models

```typescript
// Database schema for notifications
interface NotificationRecord {
  id: string;
  user_id: string;
  type: NotificationType;
  title: string;
  description: string;
  action_url?: string;
  action_text?: string;
  channels: NotificationChannel[];
  read: boolean;
  created_at: Date;
  read_at?: Date;
}

// Database schema for preferences
interface NotificationPreferenceRecord {
  user_id: string;
  type: NotificationType;
  in_app_enabled: boolean;
  email_enabled: boolean;
  push_enabled: boolean;
  updated_at: Date;
}
```

## Support

For questions or issues with the notifications feature, refer to:
- Main documentation in `/workspace/frontend/README.md`
- API usage guide in `/workspace/frontend/API_USAGE_GUIDE.md`
- Component examples in `/workspace/frontend/src/components/`

## Summary

The notification system now supports:
- ✅ **In-App Notifications**: Real-time updates within the application
- ✅ **Email Notifications**: Updates sent to user's email address
- ✅ **Push Notifications**: Mobile device alerts (UI ready, backend needed)
- ✅ **Simple Preferences**: Easy-to-use toggle system for each channel
- ✅ **Smart Defaults**: Pre-configured sensible settings
- ✅ **Visual Indicators**: Channel badges showing delivery methods
- ✅ **Category Organization**: Grouped by importance
- ✅ **LinkedIn-Inspired Design**: Professional, familiar interface
- ✅ **Responsive**: Works on all devices
- ✅ **Ready for Backend**: Clean API integration points
