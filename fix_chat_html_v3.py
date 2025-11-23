
import os

file_path = r'c:\Users\Admin\OneDrive\Desktop\SmartFixer\templates\chat.html'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to keep the top part (HTML structure) and rewrite the script part
# Find where the script starts
script_start = content.find('<script>')
if script_start == -1:
    print("Could not find script tag")
    exit(1)

top_part = content[:script_start + 8] # Include <script>

# Define the correct script content
script_content = """
        // Navigation history management
        let navigationHistory = JSON.parse(sessionStorage.getItem('navigationHistory') || '[]');
        let socket;
        let currentChatUser = null;
        let allChats = [];
        let chatHistory = JSON.parse(localStorage.getItem('chatHistory') || '{}'); // Store chat history
        let searchTimeout;

        function updateNavigationHistory() {
            const currentPath = window.location.pathname;
            if (navigationHistory.length === 0 || navigationHistory[navigationHistory.length - 1] !== currentPath) {
                navigationHistory.push(currentPath);
                if (navigationHistory.length > 10) {
                    navigationHistory.shift();
                }
                sessionStorage.setItem('navigationHistory', JSON.stringify(navigationHistory));
            }
        }

        function goBack() {
            // Go back to the editor page
            window.location.href = '/editor';
        }

        function toggleTheme() {
            const currentTheme = document.body.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);

            if (newTheme === 'dark') {
                document.querySelector('.moon').style.display = 'none';
                document.querySelector('.sun').style.display = 'block';
            } else {
                document.querySelector('.moon').style.display = 'block';
                document.querySelector('.sun').style.display = 'none';
            }
        }

        function startNewChat() {
            // Show friend selection interface
            showFriendSelection();
        }

        function showFriendSelection() {
            // Hide chat interface and show friend selection
            document.querySelector('.chat-main').style.display = 'none';
            document.querySelector('.friend-selection-container').style.display = 'block';

            // Load friends for selection
            loadFriendsForSelection();
        }

        function hideFriendSelection() {
            // Show chat interface and hide friend selection
            document.querySelector('.friend-selection-container').style.display = 'none';
            document.querySelector('.chat-main').style.display = 'flex';
        }

        async function loadFriendsForSelection() {
            try {
                const response = await fetch('/api/friends');
                const friends = await response.json();
                displayFriendsForSelection(friends);
            } catch (error) {
                console.error('Error loading friends:', error);
            }
        }

        function displayFriendsForSelection(friends) {
            const friendList = document.getElementById('friendList');
            if (friends && friends.length > 0) {
                friendList.innerHTML = friends.map(friend => `
                    <div class="friend-item" onclick="selectFriend('${friend.id}')">
                        <img src="${friend.image || 'https://via.placeholder.com/40'}" alt="Profile" class="friend-avatar">
                        <div class="friend-info">
                            <div class="friend-name">${friend.name}</div>
                            <div class="friend-username">@${friend.username}</div>
                        </div>
                    </div>
                `).join('');
            } else {
                friendList.innerHTML = '<div class="no-friends">No friends found</div>';
            }
        }

        function selectFriend(userId) {
            // Hide friend selection and show chat
            hideFriendSelection();

            // Open chat with selected friend
            openChat(userId);

            // Update chat history
            chatHistory.lastChat = userId;
            localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
        }

        async function loadChats() {
            try {
                const response = await fetch('/api/friends');
                const friends = await response.json();
                allChats = friends;
                displayChats(friends);

                // Auto-select last chat or show friend selection for first-time users
                autoSelectChat(friends);
            } catch (error) {
                console.error('Error loading chats:', error);
                // Show friend selection on error as fallback
                showFriendSelection();
            }
        }

        function searchUsers() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const searchTerm = document.querySelector('.search-input').value.toLowerCase();
                if (searchTerm.length > 0) {
                    // Search for users
                    fetch(`/api/search-users-chat?q=${encodeURIComponent(searchTerm)}`)
                        .then(response => response.json())
                        .then(users => {
                            displayChats(users);
                        })
                        .catch(error => {
                            console.error('Error searching users:', error);
                        });
                } else {
                    // Load all friends if search is empty
                    loadChats();
                }
            }, 300); // Debounce for 300ms
        }

        function displayChats(chats) {
            const chatList = document.getElementById('chatList');
            if (chats && chats.length > 0) {
                chatList.innerHTML = chats.map(friend => `
                    <div class="chat-item">
                        <img src="${friend.image || 'https://via.placeholder.com/40'}" alt="Profile" class="chat-avatar" onclick="window.location.href='/user/${friend.id}'" style="cursor: pointer;">
                        <div class="chat-info" onclick="openChat('${friend.id}')" style="cursor: pointer;">
                            <div class="chat-name" onclick="window.location.href='/user/${friend.id}'; event.stopPropagation();" style="cursor: pointer;">${friend.name}</div>
                            <div class="chat-username">@${friend.username}</div>
                            <div class="chat-last-message">Click to start chat</div>
                        </div>
                        <div class="online-status-indicator" id="online-status-${friend.id}"></div>
                    </div>
                `).join('');
                
                // Fetch and update status for each friend
                chats.forEach(friend => {
                    updateFriendStatus(friend.id);
                });
            } else {
                chatList.innerHTML = '<div class="no-chats">No users found. <button onclick="startNewChat()" class="new-chat-link">Find users to chat with</button></div>';
            }
        }

        function searchChats() {
            const searchTerm = document.querySelector('.search-input').value.toLowerCase();
            const filteredChats = allChats.filter(chat =>
                chat.name.toLowerCase().includes(searchTerm)
            );
            displayChats(filteredChats);
        }

        async function openChat(userId) {
            // Remove active class from all chat items
            document.querySelectorAll('.chat-item').forEach(item => item.classList.remove('active'));

            // Find and activate the chat item for this user
            const chatItem = document.querySelector(`.chat-info[onclick*="'${userId}'"]`);
            if (chatItem) {
                // Find the parent chat-item and add active class
                const parentItem = chatItem.closest('.chat-item');
                if (parentItem) {
                    parentItem.classList.add('active');
                }
            }

            currentChatUser = userId;

            // Join the chat room
            socket.emit('join', { room: `chat_${userId}` });

            // Update chat header info
            const friend = allChats.find(f => f.id === userId);
            if (friend) {
                document.querySelector('.current-chat-name').textContent = friend.name;
                document.querySelector('.current-chat-avatar').src = friend.image || 'https://via.placeholder.com/32';
                // Fetch real status instead of hardcoding
                updateFriendStatus(userId);
            }

            // Load chat messages
            await loadChatMessages(userId);

            // Update chat history
            chatHistory.lastChat = userId;
            localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
        }

        async function loadChatMessages(userId) {
            try {
                const response = await fetch(`/api/messages/${userId}`);
                const messages = await response.json();
                displayMessages(messages);
            } catch (error) {
                console.error('Error loading messages:', error);
            }
        }

        function displayMessages(messages) {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = messages.map(msg => {
                let messageContent = '';

                // Handle file attachments
                if (msg.file_attachment) {
                    if (msg.file_type === 'image') {
                        messageContent = `<img src="${msg.file_attachment}" alt="Image" style="max-width: 300px; max-height: 300px; border-radius: 8px; cursor: pointer;" onclick="openImageLightbox('${msg.file_attachment}')">`;
                    } else if (msg.file_type === 'video') {
                        messageContent = `<video controls style="max-width: 300px; max-height: 300px; border-radius: 8px;">
                            <source src="${msg.file_attachment}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>`;
                    } else if (msg.file_type === 'pdf') {
                        messageContent = `<a href="${msg.file_attachment}" target="_blank" style="display: inline-block; padding: 10px; background: #f0f0f0; border-radius: 8px; text-decoration: none; color: #333;">
                            📄 PDF Document
                        </a>`;
                    } else {
                        messageContent = `<a href="${msg.file_attachment}" target="_blank" style="display: inline-block; padding: 10px; background: #f0f0f0; border-radius: 8px; text-decoration: none; color: #333;">
                            📎 Download File
                        </a>`;
                    }
                } else if (msg.code_snippet) {
                    messageContent = `<div class="message-text code-message"><pre><code>${escapeHtml(msg.code_snippet)}</code></pre></div>`;
                } else {
                    messageContent = msg.content || '';
                }

                return `
                    <div class="message ${msg.sender_id === '{{ user.id }}' ? 'sent' : 'received'}">
                        ${msg.sender_id !== '{{ user.id }}' ? `<img src="${msg.sender_image || 'https://via.placeholder.com/32'}" alt="Profile" class="message-avatar">` : ''}
                        <div class="message-content">
                            <div class="message-text">${messageContent}</div>
                            <div class="message-time">${formatTime(msg.created_at)}</div>
                        </div>
                    </div>
                `;
            }).join('');
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function displayMessage(data) {
            const chatMessages = document.getElementById('chatMessages');
            const isCurrentUser = data.sender_id === '{{ user.id }}';

            let messageContent = '';

            // Handle file attachments
            if (data.file_attachment) {
                if (data.file_type === 'image') {
                    messageContent = `<img src="${data.file_attachment}" alt="Image" style="max-width: 300px; max-height: 300px; border-radius: 8px; cursor: pointer;" onclick="openImageLightbox('${data.file_attachment}')">`;
                } else if (data.file_type === 'video') {
                    messageContent = `<video controls style="max-width: 300px; max-height: 300px; border-radius: 8px;">
                        <source src="${data.file_attachment}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>`;
                } else if (data.file_type === 'pdf') {
                    messageContent = `<a href="${data.file_attachment}" target="_blank" style="display: inline-block; padding: 10px; background: #f0f0f0; border-radius: 8px; text-decoration: none; color: #333;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle; margin-right: 5px;">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14,2 14,8 20,8"/>
                            <line x1="16" y1="13" x2="8" y2="13"/>
                            <line x1="16" y1="17" x2="8" y2="17"/>
                            <polyline points="10,9 9,9 8,9"/>
                        </svg>
                        PDF Document
                    </a>`;
                } else {
                    messageContent = `<a href="${data.file_attachment}" target="_blank" style="display: inline-block; padding: 10px; background: #f0f0f0; border-radius: 8px; text-decoration: none; color: #333;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle; margin-right: 5px;">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14,2 14,8 20,8"/>
                            <line x1="16" y1="13" x2="8" y2="13"/>
                            <line x1="16" y1="17" x2="8" y2="17"/>
                            <polyline points="10,9 9,9 8,9"/>
                        </svg>
                        Download File
                    </a>`;
                }
            } else if (data.code_snippet) {
                messageContent = `<div class="message-text code-message"><pre><code>${escapeHtml(data.code_snippet)}</code></pre></div>`;
            } else {
                messageContent = data.message;
            }

            const messageElement = document.createElement('div');
            messageElement.className = `message ${isCurrentUser ? 'sent' : 'received'}`;
            messageElement.innerHTML = `
                ${!isCurrentUser ? `<img src="${data.sender_image || 'https://via.placeholder.com/32'}" alt="Profile" class="message-avatar">` : ''}
                <div class="message-content">
                    <div class="message-text">${messageContent}</div>
                    <div class="message-time">${formatTime(data.timestamp)}</div>
                </div>
            `;

            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();

            if (!currentChatUser) {
                alert('Please select a chat first.');
                return;
            }

            // If there's a message, send it
            if (message) {
                // Use the new API endpoint instead of socket emit
                fetch('/api/send-message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        receiver_id: currentChatUser,
                        content: message,
                        code_snippet: null
                    })
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.success) {
                            input.value = '';
                        } else {
                            alert('Failed to send message: ' + (data.error || 'Unknown error'));
                        }
                    })
                    .catch(error => {
                        console.error('Error sending message:', error);
                        alert('Failed to send message. Please try again.');
                    });
            }
        }

        function handleChatEnter(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function attachFile() {
            document.getElementById('fileInput').click();
        }

        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (!file) return;

            if (!currentChatUser) {
                alert('Please select a chat first.');
                document.getElementById('fileInput').value = ''; // Clear the input
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            // Show uploading message
            const chatMessages = document.getElementById('chatMessages');
            const uploadingMessage = document.createElement('div');
            uploadingMessage.className = 'message sent';
            uploadingMessage.innerHTML = `
                <div class="message-content">
                    <div class="message-text">Uploading file...</div>
                </div>
            `;
            chatMessages.appendChild(uploadingMessage);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // Upload file first
            fetch('/api/upload-file', {
                method: 'POST',
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // Remove uploading message
                    uploadingMessage.remove();

                    if (data.success) {
                        // Send message with file attachment
                        return fetch('/api/send-message', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                receiver_id: currentChatUser,
                                content: '',
                                file_attachment: data.file_path,
                                file_type: data.file_type
                            })
                        })
                            .then(response => {
                                if (!response.ok) {
                                    throw new Error('Network response was not ok');
                                }
                                return response.json();
                            })
                            .then(sendData => {
                                if (sendData.success) {
                                    // Clear file input
                                    document.getElementById('fileInput').value = '';
                                } else {
                                    alert('Failed to send file: ' + (sendData.error || 'Unknown error'));
                                }
                            });
                    } else {
                        alert('Failed to upload file: ' + (data.error || 'Unknown error'));
                        // Clear file input
                        document.getElementById('fileInput').value = '';
                    }
                })
                .catch(error => {
                    // Remove uploading message
                    uploadingMessage.remove();
                    console.error('Error uploading file:', error);
                    alert('Failed to upload file. Please try again.');
                    // Clear file input
                    document.getElementById('fileInput').value = '';
                });
        }

        function shareCodeInChat() {
            if (!currentChatUser) {
                alert('Please select a chat first.');
                return;
            }

            // Get code from session storage or prompt user
            const code = sessionStorage.getItem('uploadedCode') || '';
            if (code) {
                // Send code as a message
                fetch('/api/send-message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        receiver_id: currentChatUser,
                        content: 'Check out this code:',
                        code_snippet: code
                    })
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.success) {
                            // Clear the input
                            document.getElementById('chatInput').value = '';
                        } else {
                            alert('Failed to share code: ' + (data.error || 'Unknown error'));
                        }
                    })
                    .catch(error => {
                        console.error('Error sharing code:', error);
                        alert('Failed to share code. Please try again.');
                    });
            } else {
                alert('No code available to share. Please upload or write some code first.');
            }
        }

        function startVideoCall() {
            alert('Video call feature will be implemented in a future update.');
        }

        function startVoiceCall() {
            alert('Voice call feature will be implemented in a future update.');
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function formatTime(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }

        // Update friend's online status
        function updateFriendStatus(userId) {
            fetch(`/api/user-status/${userId}`)
                .then(response => response.json())
                .then(data => {
                    updateUserPresenceIndicator(data);
                })
                .catch(error => {
                    console.error('Error updating friend status:', error);
                });
        }

        // Load theme and initialize on page load
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
            socket.emit('chat_window_opened', { status: 'online', page: 'chat' });
            
            // Load chats
            loadChats();
        });

        // Handle page visibility changes (tab switching)
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                // User switched to another tab - mark as offline
                if (socket) {
                    socket.emit('chat_window_closed', { status: 'offline', page: 'hidden_tab' });
                }
            } else {
                // User returned to chat tab - mark as online
                if (socket) {
                    socket.emit('chat_window_opened', { status: 'online', page: 'chat' });
                }
            }
        });

        // Handle page unload (closing/navigating away)
        window.addEventListener('beforeunload', function() {
            if (socket) {
                socket.emit('chat_window_closed', { status: 'offline', page: 'navigating_away' });
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
                        // Format as 24-hour HH:mm
                        const hours = lastSeen.getHours().toString().padStart(2, '0');
                        const minutes = lastSeen.getMinutes().toString().padStart(2, '0');
                        statusIndicator.title = `Was online at ${hours}:${minutes}`;
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
                            // Format as 24-hour HH:mm
                            const hours = lastSeen.getHours().toString().padStart(2, '0');
                            const minutes = lastSeen.getMinutes().toString().padStart(2, '0');
                            statusElement.textContent = `Was online at ${hours}:${minutes}`;
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

full_content = top_part + script_content

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(full_content)

print("Successfully reconstructed chat.html")
