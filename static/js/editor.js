let editor;
let currentLanguage = 'python';
let currentProfession = 'student';
let socket;

document.addEventListener('DOMContentLoaded', function() {
    editor = CodeMirror.fromTextArea(document.getElementById('codeEditor'), {
        mode: 'python',
        theme: 'monokai',
        lineNumbers: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 4,
        tabSize: 4,
        lineWrapping: true,
        extraKeys: {"Ctrl-Space": "autocomplete"}
    });
    
    editor.on("inputRead", function(cm, change) {
        if (change.text[0].length > 0) {
            cm.showHint({hint: CodeMirror.hint.anyword, completeSingle: false});
        }
    });

    const uploadedCode = sessionStorage.getItem('uploadedCode');
    const detectedLanguage = sessionStorage.getItem('detectedLanguage');
    
    if (uploadedCode) {
        editor.setValue(uploadedCode);
        currentLanguage = detectedLanguage || 'Unknown';
        updateEditorMode(currentLanguage);
        sessionStorage.removeItem('uploadedCode');
        sessionStorage.removeItem('detectedLanguage');
    }

    editor.on('change', async function() {
        const code = editor.getValue();
        if (code.trim().length > 10) {
            const response = await fetch('/api/detect-language', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code: code})
            });
            const data = await response.json();
            currentLanguage = data.language;
            updateEditorMode(currentLanguage);
        }
    });

    socket = io();
    
    socket.on('receive_message', function(data) {
        displayMessage(data);
    });

    setInterval(trackTime, 60000);
    
    const theme = localStorage.getItem('theme') || 'light';
    if (theme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
        editor.setOption('theme', 'monokai');
        document.querySelector('.moon').style.display = 'none';
        document.querySelector('.sun').style.display = 'block';
    }
});

function updateEditorMode(language) {
    const modeMap = {
        'Python': 'python',
        'JavaScript': 'javascript',
        'Java': 'text/x-java',
        'C++': 'text/x-c++src',
        'C': 'text/x-csrc',
        'C#': 'text/x-csharp',
        'Ruby': 'ruby',
        'PHP': 'php',
        'Swift': 'swift',
        'Go': 'go',
        'Rust': 'rust',
        'SQL': 'sql',
        'R': 'r',
        'Shell': 'shell',
        'HTML': 'htmlmixed',
        'CSS': 'css'
    };
    
    const mode = modeMap[language] || 'python';
    editor.setOption('mode', mode);
}

async function reviewCode() {
    const code = editor.getValue();
    if (!code.trim()) {
        alert('Please enter some code first!');
        return;
    }
    
    showLoading('Reviewing your code...');
    
    try {
        const response = await fetch('/api/review', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                code: code,
                language: currentLanguage,
                profession: currentProfession
            })
        });
        
        const data = await response.json();
        typewriterEffect(data.result);
    } catch (error) {
        showError('Failed to review code. Please try again.');
    }
}

async function explainCode() {
    const code = editor.getValue();
    if (!code.trim()) {
        alert('Please enter some code first!');
        return;
    }
    
    showLoading('Explaining your code...');
    
    try {
        const response = await fetch('/api/explain', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                code: code,
                language: currentLanguage,
                profession: currentProfession
            })
        });
        
        const data = await response.json();
        typewriterEffect(data.result);
    } catch (error) {
        showError('Failed to explain code. Please try again.');
    }
}

async function compileCode() {
    const code = editor.getValue();
    if (!code.trim()) {
        alert('Please enter some code first!');
        return;
    }
    
    showLoading('Checking compilation...');
    
    try {
        const response = await fetch('/api/compile', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                code: code,
                language: currentLanguage,
                profession: currentProfession
            })
        });
        
        const data = await response.json();
        typewriterEffect(data.result);
    } catch (error) {
        showError('Failed to compile code. Please try again.');
    }
}

async function askQuestion() {
    const question = document.getElementById('qnaInput').value;
    if (!question.trim()) return;
    
    const code = editor.getValue();
    
    try {
        const response = await fetch('/api/question', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                question: question,
                code: code.trim() ? code : null,
                language: currentLanguage
            })
        });
        
        const data = await response.json();
        typewriterEffect(data.result);
        document.getElementById('qnaInput').value = '';
    } catch (error) {
        showError('Failed to get answer. Please try again.');
    }
}

function handleQnAEnter(event) {
    if (event.key === 'Enter') {
        askQuestion();
    }
}

function showLoading(message) {
    const output = document.getElementById('outputContent');
    output.innerHTML = `<p class="placeholder">${message}</p>`;
}

function showError(message) {
    const output = document.getElementById('outputContent');
    output.innerHTML = `<p style="color: #f56565;">${message}</p>`;
}

function typewriterEffect(text) {
    const output = document.getElementById('outputContent');
    output.innerHTML = '';
    
    let i = 0;
    const speed = 10;
    
    function type() {
        if (i < text.length) {
            output.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
            output.scrollTop = output.scrollHeight;
        }
    }
    
    type();
}

async function updateProfession() {
    const select = document.getElementById('professionSelect');
    currentProfession = select.value;
    
    await fetch('/api/update-profession', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({profession: currentProfession})
    });
}

function toggleMenu() {
    const menu = document.getElementById('dropdownMenu');
    menu.classList.toggle('active');
}

function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    if (newTheme === 'dark') {
        editor.setOption('theme', 'monokai');
        document.querySelector('.moon').style.display = 'none';
        document.querySelector('.sun').style.display = 'block';
    } else {
        editor.setOption('theme', 'eclipse');
        document.querySelector('.moon').style.display = 'block';
        document.querySelector('.sun').style.display = 'none';
    }
}

function toggleProfile() {
    const modal = document.getElementById('profileModal');
    modal.classList.add('active');
    loadProfile();
}

function toggleChat() {
    const modal = document.getElementById('chatModal');
    modal.classList.add('active');
    loadFriendsForChat();
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function showTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tabName + 'Tab').classList.add('active');
    
    if (tabName === 'posts') loadPosts();
    if (tabName === 'explore') loadExplorePosts();
    if (tabName === 'friends') loadFriends();
    if (tabName === 'notifications') loadNotifications();
    if (tabName === 'time') loadTimeSpent();
}

async function loadProfile() {
    const response = await fetch('/api/profile');
    const data = await response.json();
}

async function updateProfile() {
    const bio = document.getElementById('bioInput').value;
    const profession = document.getElementById('professionSelect').value;
    
    await fetch('/api/update-profile', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({bio, profession})
    });
    
    alert('Profile updated!');
}

async function loadPosts() {
    const response = await fetch('/api/posts');
    const posts = await response.json();
    
    const postsList = document.getElementById('postsList');
    postsList.innerHTML = posts.map(post => `
        <div class="post-card">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <img src="${post.author_image || 'https://via.placeholder.com/40'}" style="width: 30px; height: 30px; border-radius: 50%;">
                <strong>${post.author_name}</strong>
            </div>
            <p>${post.description}</p>
            <div class="post-code">${escapeHtml(post.code)}</div>
            <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                <button onclick="likePost(${post.id})">❤️ ${post.likes}</button>
                <button onclick="showComments(${post.id})">💬 ${post.comments_count}</button>
            </div>
        </div>
    `).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function loadExplorePosts() {
    const response = await fetch('/api/explore-posts');
    const posts = await response.json();
    
    const exploreList = document.getElementById('explorePostsList');
    exploreList.innerHTML = posts.map(post => `
        <div class="post-card explore-post">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <img src="${post.author_image || 'https://via.placeholder.com/40'}" style="width: 40px; height: 40px; border-radius: 50%;">
                <div>
                    <strong>${post.author_name}</strong>
                    <p style="font-size: 0.8rem; color: var(--text-secondary);">${new Date(post.created_at).toLocaleString()}</p>
                </div>
            </div>
            <p>${post.description}</p>
            <div class="post-code">${escapeHtml(post.code).substring(0, 200)}${post.code.length > 200 ? '...' : ''}</div>
            <div style="display: flex; gap: 1.5rem; margin-top: 1rem; align-items: center;">
                <button onclick="likePost(${post.id}, 'explore')" style="display: flex; align-items: center; gap: 0.3rem;">
                    <span>${post.liked ? '❤️' : '🤍'}</span> <span>${post.likes}</span>
                </button>
                <button onclick="toggleComments(${post.id})" style="display: flex; align-items: center; gap: 0.3rem;">
                    💬 <span>${post.comments_count || 0}</span>
                </button>
                <button onclick="sharePost(${post.id})">
                    📤 Share
                </button>
            </div>
            <div id="comments-${post.id}" class="comments-section" style="display: none;"></div>
        </div>
    `).join('');
}

async function likePost(postId, source = 'posts') {
    await fetch(`/api/posts/${postId}/like`, {method: 'POST'});
    if (source === 'explore') loadExplorePosts();
    else loadPosts();
}

async function toggleComments(postId) {
    const commentsDiv = document.getElementById(`comments-${postId}`);
    if (commentsDiv.style.display === 'none') {
        const response = await fetch(`/api/posts/${postId}/comments`);
        const comments = await response.json();
        commentsDiv.innerHTML = `
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color);">
                <input type="text" id="comment-input-${postId}" placeholder="Add a comment..." style="width: 100%; padding: 0.5rem; margin-bottom: 0.5rem;">
                <button onclick="addComment(${postId})">Post Comment</button>
                <div id="comments-list-${postId}">
                    ${comments.map(c => `
                        <div style="padding: 0.5rem; margin-top: 0.5rem; background: var(--bg-secondary); border-radius: 8px;">
                            <strong>${c.author_name}</strong>
                            <p>${c.content}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        commentsDiv.style.display = 'block';
    } else {
        commentsDiv.style.display = 'none';
    }
}

async function addComment(postId) {
    const input = document.getElementById(`comment-input-${postId}`);
    const content = input.value.trim();
    if (!content) return;
    
    await fetch(`/api/posts/${postId}/comment`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({content})
    });
    
    input.value = '';
    toggleComments(postId);
    setTimeout(() => toggleComments(postId), 100);
}

function sharePost(postId) {
    alert('Post link copied! Share with your friends.');
}

function showPostModal() {
    document.getElementById('postModal').classList.add('active');
}

async function createPost() {
    const code = editor.getValue();
    const description = document.getElementById('postDescription').value;
    
    await fetch('/api/posts', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            code: code,
            language: currentLanguage,
            description: description
        })
    });
    
    closeModal('postModal');
    alert('Post shared!');
    loadPosts();
}

async function loadFriends() {
    const response = await fetch('/api/friends');
    const friends = await response.json();
    
    const friendsList = document.getElementById('friendsList');
    friendsList.innerHTML = friends.map(friend => `
        <div class="friend-item">
            <img src="${friend.image || 'https://via.placeholder.com/40'}" class="friend-avatar">
            <div>
                <strong>${friend.name}</strong>
                <p>${friend.email}</p>
            </div>
        </div>
    `).join('');
}

async function sendFriendRequest() {
    const email = document.getElementById('friendEmail').value;
    
    try {
        await fetch('/api/friend-request', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email})
        });
        alert('Friend request sent!');
        document.getElementById('friendEmail').value = '';
    } catch (error) {
        alert('Failed to send request');
    }
}

async function loadNotifications() {
    const response = await fetch('/api/notifications');
    const notifications = await response.json();
    
    const notifsList = document.getElementById('notificationsList');
    notifsList.innerHTML = notifications.map(notif => `
        <div class="notification-item ${notif.read ? '' : 'unread'}">
            <div>
                <p>${notif.content}</p>
                <small>${new Date(notif.created_at).toLocaleString()}</small>
            </div>
            ${notif.type === 'friend_request' ? `
                <div>
                    <button onclick="respondToNotification(${notif.id}, 'accept')">Accept</button>
                    <button onclick="respondToNotification(${notif.id}, 'deny')">Deny</button>
                </div>
            ` : ''}
        </div>
    `).join('');
}

async function respondToNotification(notifId, action) {
    await fetch(`/api/notifications/${notifId}/respond`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action})
    });
    loadNotifications();
    loadFriends();
}

async function loadTimeSpent() {
    const response = await fetch('/api/time-spent');
    const data = await response.json();
    
    const grid = document.getElementById('contributionGrid');
    const days = 365;
    let html = '<div class="contribution-grid">';
    
    for (let i = days; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        const dayData = data.find(d => d.date === dateStr);
        const active = dayData && dayData.minutes > 0 ? 'active' : '';
        html += `<div class="contribution-day ${active}" title="${dateStr}: ${dayData ? dayData.minutes : 0} min"></div>`;
    }
    
    html += '</div>';
    grid.innerHTML = html;
}

async function trackTime() {
    await fetch('/api/track-time', {method: 'POST'});
}

async function loadFriendsForChat() {
    const response = await fetch('/api/friends');
    const friends = await response.json();
    
    const friendsList = document.getElementById('friendsListChat');
    friendsList.innerHTML = friends.map(friend => `
        <button onclick="openChat('${friend.id}')">${friend.name}</button>
    `).join('');
}

let currentChatUser = null;

async function openChat(userId) {
    currentChatUser = userId;
    socket.emit('join', {room: `chat_${userId}`});
    
    const response = await fetch(`/api/messages/${userId}`);
    const messages = await response.json();
    
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = messages.map(msg => `
        <div class="chat-message">
            <p>${msg.content}</p>
            ${msg.code_snippet ? `<pre>${escapeHtml(msg.code_snippet)}</pre>` : ''}
        </div>
    `).join('');
}

function sendMessage() {
    const message = document.getElementById('chatInput').value;
    const code = editor.getValue();
    
    if (!message.trim() && !code.trim()) return;
    
    socket.emit('send_message', {
        room: `chat_${currentChatUser}`,
        message: message,
        code_snippet: code.trim() ? code : null,
        receiver_id: currentChatUser
    });
    
    document.getElementById('chatInput').value = '';
}

function displayMessage(data) {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML += `
        <div class="chat-message">
            <strong>${data.sender}:</strong>
            <p>${data.message}</p>
            ${data.code_snippet ? `<pre>${escapeHtml(data.code_snippet)}</pre>` : ''}
        </div>
    `;
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showDictionary() {
    document.getElementById('dictionaryModal').classList.add('active');
    toggleMenu();
}

function updateDictionaryLanguage() {
    document.getElementById('dictSearch').value = '';
    document.getElementById('dictionaryContent').innerHTML = '';
}

async function searchDictionary() {
    const language = document.getElementById('dictLanguage').value;
    const searchTerm = document.getElementById('dictSearch').value.trim();
    
    if (!searchTerm) {
        document.getElementById('dictionaryContent').innerHTML = '';
        return;
    }
    
    const response = await fetch('/api/dictionary', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({language, searchTerm})
    });
    
    const data = await response.json();
    document.getElementById('dictionaryContent').innerHTML = `<pre>${data.result}</pre>`;
}

function showTranslate() {
    document.getElementById('translateModal').classList.add('active');
    document.getElementById('fromLang').textContent = currentLanguage;
    toggleMenu();
}

async function translateCode() {
    const code = editor.getValue();
    const toLang = document.getElementById('toLang').value;
    
    if (!code.trim()) {
        alert('Please write some code first!');
        return;
    }
    
    const response = await fetch('/api/translate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            code: code,
            from_lang: currentLanguage,
            to_lang: toLang
        })
    });
    
    const data = await response.json();
    document.getElementById('translateResult').innerHTML = `<pre>${data.result}</pre>`;
}


async function showHistory() {
    document.getElementById('historyModal').classList.add('active');
    toggleMenu();
    
    const response = await fetch('/api/code-history');
    const history = await response.json();
    
    const historyContent = document.getElementById('historyContent');
    historyContent.innerHTML = history.map(item => `
        <div class="history-item">
            <strong>${item.action.toUpperCase()} - ${item.language}</strong>
            <p>${new Date(item.created_at).toLocaleString()}</p>
            <pre>${escapeHtml(item.code.substring(0, 100))}...</pre>
        </div>
    `).join('');
}

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}
