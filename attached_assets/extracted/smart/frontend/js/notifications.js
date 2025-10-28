document.addEventListener('DOMContentLoaded', async () => {
    const notificationsContainer = document.getElementById('notifications-container');

    async function fetchNotifications() {
        try {
            const response = await fetch('/notifications');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const notifications = await response.json();
            displayNotifications(notifications);
        } catch (error) {
            console.error('Error fetching notifications:', error);
            notificationsContainer.innerHTML = '<p>Error loading notifications. Please try again later.</p>';
        }
    }

    function displayNotifications(notifications) {
        notificationsContainer.innerHTML = ''; // Clear loading message
        if (notifications.length === 0) {
            notificationsContainer.innerHTML = '<p>No new notifications.</p>';
            return;
        }

        notifications.forEach(notification => {
            const notificationElement = document.createElement('div');
            notificationElement.classList.add('notification-item');
            if (!notification.is_read) {
                notificationElement.classList.add('unread');
            }

            let message = '';
            switch (notification.type) {
                case 'new_like':
                    message = `Your post received a new like!`;
                    break;
                case 'new_comment':
                    message = `Your post received a new comment!`;
                    break;
                case 'friend_request':
                    message = `You have a new friend request from User ID: ${notification.related_id}.`;
                    // Add buttons to accept/decline friend request
                    notificationElement.innerHTML += `
                        <button class="accept-friend-btn" data-sender-id="${notification.related_id}" data-notification-id="${notification.id}">Accept</button>
                        <button class="decline-friend-btn" data-sender-id="${notification.related_id}" data-notification-id="${notification.id}">Decline</button>
                    `;
                    break;
                case 'friend_request_accepted':
                    message = `Your friend request to User ID: ${notification.related_id} was accepted!`;
                    break;
                case 'new_message':
                    message = `You received a new message from User ID: ${notification.related_id}.`;
                    break;
                default:
                    message = `New notification: ${notification.type}`;
            }

            notificationElement.innerHTML = `
                <p>${message}</p>
                <span>${new Date(notification.created_at).toLocaleString()}</span>
                ${!notification.is_read ? `<button class="mark-read-btn" data-notification-id="${notification.id}">Mark as Read</button>` : ''}
            `;
            notificationsContainer.appendChild(notificationElement);
        });

        // Add event listeners for mark as read buttons
        notificationsContainer.querySelectorAll('.mark-read-btn').forEach(button => {
            button.addEventListener('click', handleMarkAsRead);
        });
        notificationsContainer.querySelectorAll('.accept-friend-btn').forEach(button => {
            button.addEventListener('click', handleAcceptFriendRequest);
        });
        notificationsContainer.querySelectorAll('.decline-friend-btn').forEach(button => {
            button.addEventListener('click', handleDeclineFriendRequest);
        });
    }

    async function handleMarkAsRead(event) {
        const notificationId = event.target.dataset.notificationId;
        try {
            const response = await fetch(`/notifications/${notificationId}/read`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                fetchNotifications(); // Refresh notifications
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
            alert('An error occurred.');
        }
    }

    async function handleAcceptFriendRequest(event) {
        const senderId = event.target.dataset.senderId;
        const notificationId = event.target.dataset.notificationId;
        try {
            const response = await fetch(`/friends/accept/${senderId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                // Mark the friend request notification as read after action
                await fetch(`/notifications/${notificationId}/read`, { method: 'POST' });
                fetchNotifications(); // Refresh notifications
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error('Error accepting friend request:', error);
            alert('An error occurred.');
        }
    }

    async function handleDeclineFriendRequest(event) {
        const senderId = event.target.dataset.senderId;
        const notificationId = event.target.dataset.notificationId;
        try {
            const response = await fetch(`/friends/decline/${senderId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                // Mark the friend request notification as read after action
                await fetch(`/notifications/${notificationId}/read`, { method: 'POST' });
                fetchNotifications(); // Refresh notifications
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error('Error declining friend request:', error);
            alert('An error occurred.');
        }
    }

    fetchNotifications();
});