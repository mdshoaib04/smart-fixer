document.addEventListener('DOMContentLoaded', () => {
    const friendsList = document.getElementById('friends');
    const messagesContainer = document.getElementById('messages');
    const messageInput = document.getElementById('chat-message-input');
    const sendMessageBtn = document.getElementById('send-message-btn');

    let currentChatFriendId = null; // To keep track of the friend whose chat is open

    async function fetchFriends() {
        try {
            const response = await fetch('/friends');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const friends = await response.json();
            displayFriends(friends);
        } catch (error) {
            console.error('Error fetching friends:', error);
            friendsList.innerHTML = '<li>Error loading friends.</li>';
        }
    }

    function displayFriends(friends) {
        friendsList.innerHTML = '';
        if (friends.length === 0) {
            friendsList.innerHTML = '<li>No friends yet.</li>';
            return;
        }
        friends.forEach(friend => {
            const listItem = document.createElement('li');
            listItem.innerText = friend.username;
            listItem.dataset.friendId = friend.id;
            listItem.addEventListener('click', () => {
                currentChatFriendId = friend.id;
                messagesContainer.innerHTML = ''; // Clear previous messages
                fetchMessages(friend.id);
            });
            friendsList.appendChild(listItem);
        });
    }

    async function fetchMessages(friendId) {
        try {
            const response = await fetch(`/api/messages/${friendId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const messages = await response.json();
            displayMessages(messages);
        } catch (error) {
            console.error('Error fetching messages:', error);
            messagesContainer.innerHTML = '<p>Error loading messages.</p>';
        }
    }

    function displayMessages(messages) {
        messagesContainer.innerHTML = '';
        messages.forEach(msg => {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');
            // Assuming current user ID is 1 for now
            messageDiv.classList.add(msg.sender_id === 1 ? 'sent' : 'received');
            
            if (msg.is_code_snippet) {
                const pre = document.createElement('pre');
                const code = document.createElement('code');
                code.textContent = msg.content;
                pre.appendChild(code);
                messageDiv.appendChild(pre);
            } else {
                messageDiv.innerText = msg.content;
            }
            messagesContainer.appendChild(messageDiv);
        });
        messagesContainer.scrollTop = messagesContainer.scrollHeight; // Scroll to bottom
    }

    sendMessageBtn.addEventListener('click', async () => {
        const content = messageInput.value.trim();
        if (!content || !currentChatFriendId) return;

        const isCodeSnippet = content.includes('```');

        try {
            const response = await fetch('/api/messages', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    receiver_id: currentChatFriendId,
                    content: content,
                    is_code_snippet: isCodeSnippet
                })
            });

            const result = await response.json();
            if (response.ok) {
                messageInput.value = ''; // Clear input
                fetchMessages(currentChatFriendId); // Refresh messages
            } else {
                alert(`Error sending message: ${result.message}`);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('An error occurred while sending the message.');
        }
    });

    fetchFriends();
});