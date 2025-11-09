# Follow System API Documentation

## Overview
This document describes the API endpoints for the follow system, which implements Instagram-style following functionality with notifications.

## Database Tables

### follow_requests
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| from_user_id | String (Foreign Key) | User who sent the request |
| to_user_id | String (Foreign Key) | User who receives the request |
| status | String | pending, accepted, rejected |
| created_at | DateTime | When the request was created |
| updated_at | DateTime | When the request was last updated |

### followers
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| user_id | String (Foreign Key) | The user being followed |
| follower_id | String (Foreign Key) | The user who is following |
| created_at | DateTime | When the follow relationship was created |

### notifications (updated)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| user_id | String (Foreign Key) | User who receives the notification |
| message | Text | Notification message |
| type | String | follow_request, accepted, follow_back |
| from_user_id | String (Foreign Key) | User who triggered the notification |
| read_status | Boolean | Whether the notification has been read |
| created_at | DateTime | When the notification was created |

## API Endpoints

### POST /api/follow/request
Send a follow request to another user.

**Request Body:**
```json
{
  "to_user_id": "user_id_string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Follow request sent"
}
```

### POST /api/follow/accept
Accept a follow request.

**Request Body:**
```json
{
  "request_id": "follow_request_id"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Follow request accepted"
}
```

### POST /api/follow/reject
Reject a follow request.

**Request Body:**
```json
{
  "request_id": "follow_request_id"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Follow request rejected"
}
```

### POST /api/follow/direct
Directly follow a user (for public accounts).

**Request Body:**
```json
{
  "to_user_id": "user_id_string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully followed user"
}
```

### GET /followers/:user_id
Get the list of followers for a user.

**Response:**
```json
{
  "success": true,
  "followers": [
    {
      "id": "user_id",
      "username": "username",
      "first_name": "First",
      "last_name": "Last",
      "profile_image_url": "image_url",
      "is_following": true,
      "followed_at": "timestamp"
    }
  ]
}
```

### GET /following/:user_id
Get the list of users that a user is following.

**Response:**
```json
{
  "success": true,
  "following": [
    {
      "id": "user_id",
      "username": "username",
      "first_name": "First",
      "last_name": "Last",
      "profile_image_url": "image_url",
      "is_following": true,
      "followed_at": "timestamp"
    }
  ]
}
```

### GET /api/notifications
Get all notifications for the current user.

**Response:**
```json
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "message": "User requested to follow you",
      "type": "follow_request",
      "read_status": false,
      "created_at": "timestamp",
      "from_user": {
        "id": "user_id",
        "username": "username",
        "first_name": "First",
        "last_name": "Last",
        "profile_image_url": "image_url"
      }
    }
  ]
}
```

### POST /api/notifications/:id/read
Mark a notification as read.

**Response:**
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

### POST /api/notifications/read-all
Mark all notifications as read.

**Response:**
```json
{
  "success": true,
  "message": "All notifications marked as read"
}
```

## Follow Workflow

1. **User A sends follow request to User B:**
   - If User B's account is public → Direct follow
   - If User B's account is private → Create follow request

2. **User B receives notification:**
   - Notification shows "User A wants to follow you"
   - Options: [ Confirm ] [ Delete ]

3. **User B confirms:**
   - Update follow request status to "accepted"
   - Add entry to followers table
   - Create notification for User A: "User B accepted your follow request"

4. **User B deletes:**
   - Update follow request status to "rejected"
   - Optional notification to User A: "Your follow request was declined"

5. **Follow Back System:**
   - When User A already follows User B
   - And User B follows User A back → Status: Friends/Mutual
   - No button shown in UI

## Notification Examples

| Trigger | Notification |
|---------|--------------|
| User A sent request | "User A requested to follow you" |
| User B accepted request | "User B accepted your follow request" |
| Follow Back needed | "Follow back User A" |
| Mutual follow complete | No notification required |