#!/usr/bin/env python3
"""
Script to fix the corrupted chat.html file by removing duplicate content
and adding the proper updateUserPresenceIndicator function with 12-hour time format.
"""

# Read the file
with open('templates/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where the corruption starts (duplicate content)
# The corruption happens after "socket.emit('chat_window_opened', {});"
corruption_marker = "socket.emit('chat_window_opened', {});"

# Find the first occurrence
first_occurrence = content.find(corruption_marker)
if first_occurrence == -1:
    print("Marker not found!")
    exit(1)

# Find the second occurrence (this is where duplication starts)
second_occurrence = content.find(corruption_marker, first_occurrence + len(corruption_marker))

if second_occurrence != -1:
    # Remove everything from the second occurrence to the end
    content_before_corruption = content[:first_occurrence + len(corruption_marker)]
    
    # Add the proper ending
    proper_ending = """

            // Load chats
            loadChats();
        });

        // Handle page visibility changes (tab switching)
        document.addEventListener('visibilitychange', function () {
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
        window.addEventListener('beforeunload', function () {
            if (socket) {
                socket.emit('chat_window_closed', {});
            }
        });

        // Add function to update user presence indicators in real-time
        function updateUserPresenceIndicator(data) {
            // Update sidebar status indicator
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
    </script>
</body>

</html>"""
    
    fixed_content = content_before_corruption + proper_ending
    
    # Write the fixed content
    with open('templates/chat.html', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("Fixed chat.html successfully!")
    print(f"Removed {len(content) - len(fixed_content)} duplicate characters")
else:
    print("No corruption found - file seems OK")
