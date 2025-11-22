"""
Fix user presence display issues:
1. Remove "Offline" text below username
2. Fix click handlers (profile pic, name, chat area)
3. Ensure status dots work correctly
"""

# Read the file
with open('templates/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the displayChats function - remove status text, fix click handlers
old_chat_item = '''                    <div class="chat-item">
                        <img src="${friend.image || 'https://via.placeholder.com/40'}" alt="Profile" class="chat-avatar" onclick="window.location.href='/user/${friend.id}'" style="cursor: pointer;">
                        <div class="chat-info" onclick="openChat('${friend.id}')" style="cursor: pointer;">
                            <div class="chat-name" onclick="window.location.href='/user/${friend.id}'; event.stopPropagation();" style="cursor: pointer;">${friend.name}</div>
                            <div class="chat-username">@${friend.username}</div>
                            <div class="chat-last-message" id="status-text-${friend.id}">Offline</div>
                        </div>
                        <div class="online-status-indicator" id="online-status-${friend.id}"></div>
                    </div>'''

new_chat_item = '''                    <div class="chat-item">
                        <div style="position: relative;">
                            <img src="${friend.image || 'https://via.placeholder.com/40'}" alt="Profile" class="chat-avatar" onclick="openImageLightbox('${friend.image || 'https://via.placeholder.com/40'}'); event.stopPropagation();" style="cursor: pointer;">
                            <div class="online-status-indicator" id="online-status-${friend.id}"></div>
                        </div>
                        <div class="chat-info" onclick="openChat('${friend.id}')" style="cursor: pointer; flex: 1;">
                            <div class="chat-name" onclick="window.location.href='/user/${friend.id}'; event.stopPropagation();" style="cursor: pointer;">${friend.name}</div>
                            <div class="chat-username">@${friend.username}</div>
                        </div>
                    </div>'''

content = content.replace(old_chat_item, new_chat_item)

# 2. Update CSS for chat-item to use flexbox properly
old_chat_item_css = '''.chat-item {
            display: flex;
            align-items: center;
            padding: 12px;
            cursor: pointer;
            border-radius: 8px;
            transition: background-color 0.2s;
            margin-bottom: 4px;
        }'''

new_chat_item_css = '''.chat-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            cursor: pointer;
            border-radius: 8px;
            transition: background-color 0.2s;
            margin-bottom: 4px;
        }'''

content = content.replace(old_chat_item_css, new_chat_item_css)

# 3. Update the online status indicator CSS to position correctly
old_status_css = '''.online-status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #6c757d; /* Grey for offline */
            border: 2px solid var(--card-bg);
            position: absolute;
            bottom: 2px;
            right: 2px;
        }'''

new_status_css = '''.online-status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: #6c757d; /* Grey for offline */
            border: 2px solid var(--bg-primary);
            position: absolute;
            bottom: 0;
            right: 0;
        }'''

content = content.replace(old_status_css, new_status_css)

# 4. Remove the updateUserStatus function that updates status text (we don't need it anymore)
# Instead, simplify it to only update the dot
old_update_function = '''        // Update user online status
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
        }'''

new_update_function = '''        // Update user online status
        function updateUserStatus(userId, isOnline, lastSeen) {
            const statusDot = document.getElementById(`online-status-${userId}`);
            
            if (!statusDot) return;
            
            if (isOnline) {
                statusDot.classList.add('online');
            } else {
                statusDot.classList.remove('online');
            }
        }'''

content = content.replace(old_update_function, new_update_function)

# 5. Update the chat header status to show online/offline with last seen
# Find and update the current-chat-status display
old_header_status = "document.querySelector('.current-chat-status').textContent = 'Online';"
new_header_status = '''const friend = allChats.find(f => f.id === userId);
            if (friend) {
                document.querySelector('.current-chat-name').textContent = friend.name;
                document.querySelector('.current-chat-avatar').src = friend.image || 'https://via.placeholder.com/32';
                
                // Fetch and display real-time status
                fetch(`/api/user-status/${userId}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            const statusEl = document.querySelector('.current-chat-status');
                            if (data.is_online) {
                                statusEl.textContent = 'Online';
                                statusEl.style.color = '#28a745';
                            } else if (data.last_seen) {
                                statusEl.textContent = getLastSeenText(data.last_seen);
                                statusEl.style.color = '#6c757d';
                            } else {
                                statusEl.textContent = 'Offline';
                                statusEl.style.color = '#6c757d';
                            }
                        }
                    })
                    .catch(err => console.error('Error fetching status:', err));
            }'''

# This replacement is more complex, let's find the exact context
content = content.replace(
    '''            // Update chat header info
            const friend = allChats.find(f => f.id === userId);
            if (friend) {
                document.querySelector('.current-chat-name').textContent = friend.name;
                document.querySelector('.current-chat-avatar').src = friend.image || 'https://via.placeholder.com/32';
                document.querySelector('.current-chat-status').textContent = 'Online';
            }''',
    '''            // Update chat header info
            ''' + new_header_status
)

# Write back
with open('templates/chat.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully fixed user presence display!")
print("- Removed 'Offline' text below usernames")
print("- Fixed click handlers:")
print("  * Profile pic -> Opens in lightbox")
print("  * Name -> Goes to user profile")
print("  * Rest of area -> Opens chat")
print("- Updated status dot positioning")
print("- Simplified status update function")
print("- Added real-time status to chat header")
