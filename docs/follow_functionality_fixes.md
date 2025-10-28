# Follow Functionality Fixes

## Issues Fixed

1. **Incorrect Button Display After Accepting Follow Request**
   - **Problem**: When a user accepted a follow request, the notification still showed "Follow Back" button
   - **Solution**: Changed to show "View" button instead, which navigates to the user's profile

2. **Incorrect Follow Back Behavior**
   - **Problem**: When a user clicked "Follow Back", it directly confirmed the relationship instead of sending a new follow request
   - **Solution**: Now sends a new pending follow request that requires confirmation from the other user

## Changes Made

### Backend (routes.py)
- Modified the `follow_back` action in `/api/notifications/<int:notif_id>/respond` endpoint
- Changed the status from `'accepted'` to `'pending'` when creating reverse friendship
- Added proper notification flow for follow back requests
- Updated notification content to reflect the correct state

### Frontend (notifications.html)
- Updated `createNotificationItem()` function to show correct buttons based on notification content
- Added logic to show "View" button after accepting a follow request
- Added logic to show "Requested" text after sending a follow back request
- Updated `respondToNotification()` function to handle the new follow back flow

## New Notification Flow

1. **User A sends follow request to User B**
   - User B receives notification: "User A sent you a friend request"
   - Buttons: "Confirm" / "Delete"

2. **User B accepts the request**
   - User A receives notification: "User B accepted your friend request"
   - User B's notification changes to: "User A started following you"
   - Buttons for both users: "View" (navigates to profile)

3. **User B clicks "Follow Back"**
   - User B's notification changes to: "You requested to follow User A"
   - User A receives new notification: "User B requested to follow you"
   - Buttons for User B: "Requested" (text only)
   - Buttons for User A: "Confirm" / "Delete"

4. **User A confirms User B's follow request**
   - Both users receive notification: "You and User B now follow each other"
   - Buttons: None (mutual follow established)

## Testing

A test script (`test_follow_functionality.py`) has been created to verify the correct behavior of the follow flow.