"""
Add real-time user presence system to chat
Features:
1. Green dot for online, grey for offline
2. Dynamic "last seen" status
3. Real-time status updates
"""

# Read the file
with open('templates/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add CSS for online/offline status dots
status_css = '''
        .online-status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #6c757d; /* Grey for offline */
            border: 2px solid var(--card-bg);
            position: absolute;
            bottom: 2px;
            right: 2px;
        }
        
        .online-status-indicator.online {
            background-color: #28a745; /* Green for online */
            box-shadow: 0 0 6px rgba(40, 167, 69, 0.6);
        }
        
        .chat-last-message {
            font-size: 0.85em;
            color: var(--text-muted);
            margin-top: 2px;
        }
'''

# Insert CSS before </style>
content = content.replace('</style>', status_css + '    </style>')

# 2. Update displayChats function to show proper status
old_display_chats = '''                        <div class="chat-info" onclick="openChat('${friend.id}')" style="cursor: pointer;">
                            <div class="chat-name" onclick="window.location.href='/user/${friend.id}'; event.stopPropagation();" style="cursor: pointer;">${friend.name}</div>
                            <div class="chat-username">@${friend.username}</div>
                            <div class="chat-last-message">Click to start chat</div>
                        </div>
                        <div class="online-status-indicator" id="online-status-${friend.id}"></div>'''

new_display_chats = '''                        <div class="chat-info" onclick="openChat('${friend.id}')" style="cursor: pointer;">
                            <div class="chat-name" onclick="window.location.href='/user/${friend.id}'; event.stopPropagation();" style="cursor: pointer;">${friend.name}</div>
                            <div class="chat-username">@${friend.username}</div>
                            <div class="chat-last-message" id="status-text-${friend.id}">Offline</div>
                        </div>
                        <div class="online-status-indicator" id="online-status-${friend.id}"></div>'''

content = content.replace(old_display_chats, new_display_chats)

# 3. Add function to update user status with real-time "last seen"
status_update_function = '''
        // Update user online status
        function updateUserStatus(userId, isOnline, lastSeen) {
            const statusDot = document.getElementById(`online-status-${userId}`);
            const statusText = document.getElementById(`status-text-${userId}`);
            
            if (!statusDot) return;
            
            if (isOnline) {
                statusDot.classList.add('online');
                if (statusText) statusText.textContent = 'Online';
            } else {
                statusDot.classList.remove('online');
                if (statusText && lastSeen) {
                    const lastSeenText = getLastSeenText(lastSeen);
                    statusText.textContent = lastSeenText;
                }
            }
        }
        
        // Calculate "last seen" text
        function getLastSeenText(lastSeenTimestamp) {
            const now = new Date();
            const lastSeen = new Date(lastSeenTimestamp);
            const diffMs = now - lastSeen;
            const diffMins = Math.floor(diffMs / 60000);
            
            if (diffMins < 5) {
                return 'Online';
            } else if (diffMins === 5) {
                return 'Online 5 min ago';
            } else if (diffMins < 60) {
                return `Online ${diffMins} min ago`;
            } else if (diffMins < 1440) { // Less than 24 hours
                const hours = Math.floor(diffMins / 60);
                return `Online ${hours} hour${hours > 1 ? 's' : ''} ago`;
            } else {
                const days = Math.floor(diffMins / 1440);
                return `Online ${days} day${days > 1 ? 's' : ''} ago`;
            }
        }
        
        // Fetch and update all user statuses
        async function updateAllUserStatuses() {
            if (!allChats || allChats.length === 0) return;
            
            try {
                const userIds = allChats.map(chat => chat.id);
                const response = await fetch('/api/user-statuses', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_ids: userIds })
                });
                
                if (response.ok) {
                    const statuses = await response.json();
                    statuses.forEach(status => {
                        updateUserStatus(status.user_id, status.is_online, status.last_seen);
                    });
                }
            } catch (error) {
                console.error('Error fetching user statuses:', error);
            }
        }
        
        // Update statuses every 30 seconds
        setInterval(updateAllUserStatuses, 30000);
        
'''

# Insert before the DOMContentLoaded event listener
content = content.replace(
    "        document.addEventListener('DOMContentLoaded', function () {",
    status_update_function + "        document.addEventListener('DOMContentLoaded', function () {"
)

# 4. Call updateAllUserStatuses after loading chats
content = content.replace(
    "displayChats(friends);",
    "displayChats(friends);\n                updateAllUserStatuses();"
)

# Write back
with open('templates/chat.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully added user presence system!")
print("- Added CSS for online/offline status dots")
print("- Updated displayChats to show status text")
print("- Added updateUserStatus function")
print("- Added getLastSeenText function")
print("- Added updateAllUserStatuses function")
print("- Added 30-second status update interval")
