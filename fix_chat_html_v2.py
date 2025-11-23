
import os

file_path = r'c:\Users\Admin\OneDrive\Desktop\SmartFixer\templates\chat.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the split point
split_marker = "// Load theme and initialize on page load"
split_index = content.find(split_marker)

if split_index == -1:
    print("Could not find split marker")
    exit(1)

# Keep the top part
top_part = content[:split_index]

# Define the bottom part (fixed)
bottom_part = """// Load theme and initialize on page load
        document.addEventListener('DOMContentLoaded', function () {
            const theme = localStorage.getItem('theme') || 'light';
            if (theme === 'dark') {
                document.body.setAttribute('data-theme', 'dark');
                document.querySelector('.moon').style.display = 'none';
                document.querySelector('.sun').style.display = 'block';
            }
            updateNavigationHistory();

            // Initialize Socket.IO
            socket = io();

            // Socket event listeners
            socket.on('receive_message', function (data) {
                // Check if this message is for the current chat
                if (currentChatUser && (data.sender_id === currentChatUser || data.receiver_id === currentChatUser)) {
                    displayMessage(data);
                }
            });
            socket.on('user_joined', (data) => {
                console.log(data.user + ' joined the chat');
            });
            socket.on('user_left', (data) => {
                console.log(data.user + ' left the chat');
            });

            // Listen for user presence updates
            socket.on('user_presence_update', function (data) {
                updateUserPresenceIndicator(data);
            });

            // Listen for new notifications
            socket.on('new_notification', function (data) {
                if (data.user_id === '{{ user.id }}') {
                    // Show notification alert
                    alert('You have a new notification!');
                }
            });

            // Join user's personal room for notifications
            socket.emit('join', {room: `user_{{ user.id }}`});
            
            // Join user's own chat room to receive sent messages in real-time
            socket.emit('join', {room: `chat_{{ user.id }}`});
            
            // Send chat window opened event to update presence
            socket.emit('chat_window_opened', {});
            
            // Load chats
            loadChats();
        });

        // Handle page visibility changes (tab switching)
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                // User switched to another tab - mark as offline
                if (socket) {
                    socket.emit('chat_window_closed', {});
                }
            } else {
                // User returned to chat tab - mark as online
                if (socket) {
                    socket.emit('chat_window_opened', {});
                }
            }
        });

        // Handle page unload (closing/navigating away)
        window.addEventListener('beforeunload', function() {
            if (socket) {
                socket.emit('chat_window_closed', {});
            }
        });

        // Add function to update user presence indicators
        function updateUserPresenceIndicator(data) {
            const statusIndicator = document.getElementById(`online-status-${data.user_id}`);
            if (statusIndicator) {
                if (data.is_online) {
                    statusIndicator.className = 'online-status-indicator online';
                    statusIndicator.title = 'Online';
                } else {
                    statusIndicator.className = 'online-status-indicator offline';
                    if (data.last_seen) {
                        const lastSeen = new Date(data.last_seen);
                        // Format as 12-hour with AM/PM
                        const hours = lastSeen.getHours();
                        const minutes = lastSeen.getMinutes();
                        const ampm = hours >= 12 ? 'PM' : 'AM';
                        const hours12 = hours % 12 || 12;
                        const minutesStr = minutes.toString().padStart(2, '0');
                        statusIndicator.title = `Was online at ${hours12}:${minutesStr} ${ampm}`;
                    } else {
                        statusIndicator.title = 'Offline';
                    }
                }
            }
            
            // Update chat header if this is the current chat user
            if (currentChatUser === data.user_id) {
                const statusElement = document.querySelector('.current-chat-status');
                if (statusElement) {
                    if (data.is_online) {
                        statusElement.textContent = 'Online';
                        statusElement.style.color = '#4CAF50';
                    } else {
                        if (data.last_seen) {
                            const lastSeen = new Date(data.last_seen);
                            // Format as 12-hour with AM/PM
                            const hours = lastSeen.getHours();
                            const minutes = lastSeen.getMinutes();
                            const ampm = hours >= 12 ? 'PM' : 'AM';
                            const hours12 = hours % 12 || 12;
                            const minutesStr = minutes.toString().padStart(2, '0');
                            statusElement.textContent = `Was online at ${hours12}:${minutesStr} ${ampm}`;
                        } else {
                            statusElement.textContent = 'Offline';
                        }
                        statusElement.style.color = '#888';
                    }
                }
            }
        }

        function autoSelectChat(friends) {
            // Show "Select a chat" only when there are 0 friends
            if (!friends || friends.length === 0) {
                showFriendSelection();
                return;
            }
            
            // Check if there's a last chat in history
            if (chatHistory.lastChat && friends.some(f => f.id === chatHistory.lastChat)) {
                // Open the last chat
                setTimeout(() => {
                    openChat(chatHistory.lastChat);
                }, 100);
            } else if (friends && friends.length > 0) {
                // Open the first chat (most recent)
                setTimeout(() => {
                    openChat(friends[0].id);
                }, 100);
            } else {
                // No friends, show friend selection for first-time users
                showFriendSelection();
            }
        }

        function openImageLightbox(imageSrc) {
            const lightbox = document.getElementById('imageLightbox');
            const lightboxImg = document.getElementById('lightboxImage');
            lightboxImg.src = imageSrc;
            lightbox.style.display = 'flex';
        }

        function closeImageLightbox() {
            const lightbox = document.getElementById('imageLightbox');
            lightbox.style.display = 'none';
            document.getElementById('lightboxImage').src = '';
        }
    </script>

    <!-- Image Lightbox -->
    <div id="imageLightbox" class="image-lightbox" onclick="closeImageLightbox()">
        <button class="lightbox-close" onclick="closeImageLightbox()">&times;</button>
        <img id="lightboxImage" class="lightbox-content" src="" alt="Full size image" onclick="event.stopPropagation()">
    </div>
</body>

</html>
"""

new_content = top_part + bottom_part

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully fixed chat.html")
