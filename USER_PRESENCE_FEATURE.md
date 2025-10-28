# User Presence Feature Documentation

## Overview

The User Presence feature in SmartFixer provides real-time status updates for users, showing whether they are online, recently active, or when they were last seen. This feature enhances the social experience by allowing users to know the availability of their connections.

## Presence Status Types

1. **🟢 Online** - User is currently active in the app or chat
2. **🕓 Active X minutes ago** - User was active within the last 5 minutes
3. **⏰ Last seen at [time]** - User has been inactive for more than 5 minutes

## Technical Implementation

### Database Schema

The User model has been extended with two new fields:
- `last_active` (DateTime) - Timestamp of the user's last activity
- `is_online` (Boolean) - Current online status of the user

### Backend Logic

#### Presence Tracking
- User activity is tracked through Socket.IO events
- The `last_active` timestamp is updated on any user interaction
- Users are marked as online when they connect and offline when they disconnect

#### Status Calculation
The presence status is calculated based on the time difference between now and the user's last activity:
- **Online**: If `is_online` is true and last activity was within 5 minutes
- **Active**: If last activity was within 5 minutes but user is not currently connected
- **Last seen**: If last activity was more than 5 minutes ago

### Frontend Implementation

#### Real-time Updates
- Socket.IO is used to broadcast presence updates to all connected clients
- Presence indicators are updated in real-time without page refresh

#### Display Locations
- Chat interface shows presence status next to user names
- User profile pages display current presence status

## API Endpoints

### Get User Presence
```
GET /api/user-presence/<user_id>
```

Returns the presence status for a specific user:
```json
{
  "is_online": true,
  "status": "online"
}
```

Or for offline users:
```json
{
  "is_online": false,
  "status": "Last seen today at 14:30"
}
```

## Socket.IO Events

### Outgoing Events
- `user_presence_update` - Broadcast when a user's presence status changes

### Incoming Events
- `user_activity` - Sent by client when user performs an action
- `connect` - Sent when user connects to the application
- `disconnect` - Sent when user disconnects from the application

## Configuration

No additional configuration is required. The presence feature works automatically once the application is running.

## Migration

When upgrading from a previous version, run the migration script to initialize the `last_active` field for existing users:

```bash
python migrate_user_presence.py
```

## Privacy Considerations

The presence feature only shows status to authenticated users who are connected to the platform. Users can control their visibility through their privacy settings.