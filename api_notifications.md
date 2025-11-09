# Instagram-Style Notification System API Documentation

## Overview
This document describes the API endpoints for the Instagram-style notification system, which implements social interaction notifications similar to Instagram.

## Database Tables

### notifications (updated)
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| user_id | String (Foreign Key) | User who receives the notification |
| message | Text | Notification message |
| type | String | follow_request, accepted, follow_back, like, comment, comment_reply, system_update |
| from_user_id | String (Foreign Key) | User who triggered the notification |
| read_status | Boolean | Whether the notification has been read |
| created_at | DateTime | When the notification was created |

### post_likes
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| post_id | Integer (Foreign Key) | Post being liked |
| user_id | String (Foreign Key) | User who liked the post |
| created_at | DateTime | When the like was created |

### comments
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| post_id | Integer (Foreign Key) | Post being commented on |
| user_id | String (Foreign Key) | User who made the comment |
| content | Text | Comment content |
| created_at | DateTime | When the comment was created |

## API Endpoints

### POST /api/post/:post_id/like
Like or unlike a post.

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "success": true,
  "message": "Post liked",
  "liked": true
}
```

### POST /api/post/:post_id/comment
Comment on a post.

**Request Body:**
```json
{
  "content": "Nice code!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Comment added"
}
```

### POST /api/comment/:comment_id/reply
Reply to a comment.

**Request Body:**
```json
{
  "content": "Thanks for the feedback!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Reply added"
}
```

### POST /api/system-announcement
Create a system announcement (admin only).

**Request Body:**
```json
{
  "title": "System Update",
  "message": "New version released - Explore updated features!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "System announcement created"
}
```

### GET /api/notifications/unread-count
Get the count of unread notifications for the current user.

**Response:**
```json
{
  "success": true,
  "count": 5
}
```

### GET /api/chats/unread-count
Get the count of unread chats for the current user.

**Response:**
```json
{
  "success": true,
  "count": 3
}
```

## Notification Types

### Follow Notifications
- **follow_request**: "User A requested to follow you"
- **accepted**: "User B accepted your follow request"
- **follow_back**: "Follow back User A"

### Social Interaction Notifications
- **like**: "User C liked your post"
- **comment**: "User D commented on your post: 'Nice code!'"
- **comment_reply**: "User E replied to your comment: 'Thanks!'"

### System Notifications
- **system_update**: "New version released - Explore updated features!"

## Notification Workflow

### Like Notification
1. User A likes User B's post
2. Backend creates like record in post_likes table
3. Backend creates notification for User B: "User A liked your post"
4. Real-time notification sent via SocketIO
5. Notification badge updated on User B's client

### Comment Notification
1. User A comments on User B's post
2. Backend creates comment record in comments table
3. Backend creates notification for User B: "User A commented on your post: 'Nice code!'"
4. Real-time notification sent via SocketIO
5. Notification badge updated on User B's client

### Reply Notification
1. User A replies to User B's comment
2. Backend creates reply record in comments table
3. Backend creates notification for User B: "User A replied to your comment: 'Thanks!'"
4. Real-time notification sent via SocketIO
5. Notification badge updated on User B's client

### System Update Notification
1. Admin creates system announcement
2. Backend creates notification for all users
3. Real-time notifications sent via SocketIO
4. Notification badges updated on all clients

## Edge Cases

### Unlike
- When a user unlikes a post, the corresponding like notification is removed
- Notification badge is updated accordingly

### Blocked Users
- Notifications from blocked users are not delivered
- Existing notifications from blocked users are hidden

### Deleted Content
- Notifications for deleted posts show "Content unavailable"
- Links in notifications navigate to appropriate error pages

### Pending Requests
- Follow requests remain in pending state until accepted/rejected
- Users can see pending requests in their notifications

### Mutual Follows
- When two users follow each other, they become mutual connections
- No action buttons are shown for mutual follow notifications