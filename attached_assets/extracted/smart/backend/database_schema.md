# Database Schema for Smart Code Reviewer

This document outlines the database schema for the Smart Code Reviewer application. We will use a relational database (like PostgreSQL or SQLite for development) to store the data.

## Table of Contents
1. `users`
2. `code_snippets`
3. `snippet_versions`
4. `posts`
5. `likes`
6. `comments`
7. `friends`
8. `notifications`
9. `messages`

---

### 1. `users` Table
Stores information about the users.

| Column Name      | Data Type          | Constraints              | Description                                  |
|------------------|--------------------|--------------------------|----------------------------------------------|
| `id`             | INTEGER            | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each user.             |
| `username`       | VARCHAR(50)        | UNIQUE, NOT NULL         | User's unique username.                      |
| `email`          | VARCHAR(100)       | UNIQUE, NOT NULL         | User's email address.                        |
| `password_hash`  | VARCHAR(255)       | NOT NULL                 | Hashed password for local authentication.    |
| `auth_provider`  | VARCHAR(20)        |                          | e.g., 'local', 'google', 'github'.           |
| `provider_id`    | VARCHAR(255)       |                          | User's ID from the external provider.        |
| `profile_picture`| VARCHAR(255)       |                          | URL to the user's profile picture.           |
| `bio`            | TEXT               |                          | A short biography of the user.               |
| `created_at`     | TIMESTAMP          | DEFAULT CURRENT_TIMESTAMP| Timestamp of when the user was created.      |

---

### 2. `code_snippets` Table
Stores the primary information about a code snippet.

| Column Name      | Data Type          | Constraints              | Description                                  |
|------------------|--------------------|--------------------------|----------------------------------------------|
| `id`             | INTEGER            | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each snippet.          |
| `user_id`        | INTEGER            | FOREIGN KEY (`users.id`) | The user who owns the snippet.               |
| `title`          | VARCHAR(100)       | NOT NULL                 | A title for the code snippet.                |
| `language`       | VARCHAR(50)        | NOT NULL                 | The programming language of the code.        |
| `created_at`     | TIMESTAMP          | DEFAULT CURRENT_TIMESTAMP| Timestamp of when the snippet was created.   |

---

### 3. `snippet_versions` Table
Stores the version history of each code snippet and the AI analysis.

| Column Name      | Data Type          | Constraints                      | Description                                  |
|------------------|--------------------|----------------------------------|----------------------------------------------|
| `id`             | INTEGER            | PRIMARY KEY, AUTOINCREMENT       | Unique identifier for each version.          |
| `snippet_id`     | INTEGER            | FOREIGN KEY (`code_snippets.id`) | The parent code snippet.                     |
| `version_number` | INTEGER            | NOT NULL                         | The version number (e.g., 1, 2, 3).          |
| `code_content`   | TEXT               | NOT NULL                         | The actual code for this version.            |
| `review_output`  | TEXT               |                                  | The AI-generated review.                     |
| `explain_output` | TEXT               |                                  | The AI-generated explanation.                |
| `compile_output` | TEXT               |                                  | The AI-generated compilation output/result.  |
| `created_at`     | TIMESTAMP          | DEFAULT CURRENT_TIMESTAMP        | Timestamp of when this version was created.  |

---

### 4. `posts` Table
Stores user-created posts that feature a code snippet.

| Column Name      | Data Type          | Constraints                      | Description                                  |
|------------------|--------------------|----------------------------------|----------------------------------------------|
| `id`             | INTEGER            | PRIMARY KEY, AUTOINCREMENT       | Unique identifier for each post.             |
| `user_id`        | INTEGER            | FOREIGN KEY (`users.id`)         | The user who created the post.               |
| `snippet_id`     | INTEGER            | FOREIGN KEY (`code_snippets.id`) | The code snippet featured in the post.       |
| `caption`        | TEXT               |                                  | A caption or description for the post.       |
| `created_at`     | TIMESTAMP          | DEFAULT CURRENT_TIMESTAMP        | Timestamp of when the post was created.      |

---

### 5. `likes` Table
Stores likes on posts.

| Column Name      | Data Type          | Constraints              | Description                                  |
|------------------|--------------------|--------------------------|----------------------------------------------|
| `id`             | INTEGER            | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each like.             |
| `user_id`        | INTEGER            | FOREIGN KEY (`users.id`) | The user who liked the post.                 |
| `post_id`        | INTEGER            | FOREIGN KEY (`posts.id`) | The post that was liked.                     |
| `created_at`     | TIMESTAMP          | DEFAULT CURRENT_TIMESTAMP| Timestamp of when the like was given.        |

---

### 6. `comments` Table
Stores comments on posts.

| Column Name      | Data Type          | Constraints              | Description                                  |
|------------------|--------------------|--------------------------|----------------------------------------------|
| `id`             | INTEGER            | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each comment.          |
| `user_id`        | INTEGER            | FOREIGN KEY (`users.id`) | The user who wrote the comment.              |
| `post_id`        | INTEGER            | FOREIGN KEY (`posts.id`) | The post that was commented on.              |
| `content`        | TEXT               | NOT NULL                 | The content of the comment.                  |
| `created_at`     | TIMESTAMP          | DEFAULT CURRENT_TIMESTAMP| Timestamp of when the comment was made.      |

---

### 7. `friends` Table
Stores the friendship relationships between users.

| Column Name      | Data Type          | Constraints              | Description                                  |
|------------------|--------------------|--------------------------|----------------------------------------------|
| `id`             | INTEGER            | PRIMARY KEY, AUTOINCREMENT | Unique identifier for the relationship.      |
| `user1_id`       | INTEGER            | FOREIGN KEY (`users.id`) | The user who initiated the request.          |
| `user2_id`       | INTEGER            | FOREIGN KEY (`users.id`) | The user who received the request.           |
| `status`         | VARCHAR(20)        | NOT NULL                 | e.g., 'pending', 'accepted', 'declined'.     |
| `created_at`     | TIMESTAMP          | DEFAULT CURRENT_TIMESTAMP| Timestamp of when the request was sent.      |

---

### 8. `notifications` Table
Stores notifications for users.

| Column Name      | Data Type          | Constraints              | Description                                  |
|------------------|--------------------|--------------------------|----------------------------------------------|
| `id`             | INTEGER            | PRIMARY KEY, AUTOINCREMENT | Unique identifier for the notification.      |
| `user_id`        | INTEGER            | FOREIGN KEY (`users.id`) | The user who receives the notification.      |
| `type`           | VARCHAR(50)        | NOT NULL                 | e.g., 'friend_request', 'new_like', 'new_comment'. |
| `related_id`     | INTEGER            |                          | ID of the related item (e.g., user_id, post_id). |
| `is_read`        | BOOLEAN            | DEFAULT FALSE            | Whether the user has read the notification.  |
| `created_at`     | TIMESTAMP          | DEFAULT CURRENT_TIMESTAMP| Timestamp of when the notification was created.|

---

### 9. `messages` Table
Stores chat messages between friends.

| Column Name      | Data Type          | Constraints              | Description                                  |
|------------------|--------------------|--------------------------|----------------------------------------------|
| `id`             | INTEGER            | PRIMARY KEY, AUTOINCREMENT | Unique identifier for the message.           |
| `sender_id`      | INTEGER            | FOREIGN KEY (`users.id`) | The user who sent the message.               |
| `receiver_id`    | INTEGER            | FOREIGN KEY (`users.id`) | The user who received the message.           |
| `content`        | TEXT               | NOT NULL                 | The content of the message.                  |
| `is_code_snippet`| BOOLEAN            | DEFAULT FALSE            | True if the content is a code snippet.       |
| `created_at`     | TIMESTAMP          | DEFAULT CURRENT_TIMESTAMP| Timestamp of when the message was sent.      |
