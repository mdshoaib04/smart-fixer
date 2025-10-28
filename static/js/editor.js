// Navigation history management
let navigationHistory = JSON.parse(sessionStorage.getItem('navigationHistory') || '[]');
let currentOutput = '';
let selectedFriends = [];

function updateNavigationHistory() {
    const currentPath = window.location.pathname;
    if (navigationHistory.length === 0 || navigationHistory[navigationHistory.length - 1] !== currentPath) {
        navigationHistory.push(currentPath);
        if (navigationHistory.length > 10) { // Keep only last 10 pages
            navigationHistory.shift();
        }
        sessionStorage.setItem('navigationHistory', JSON.stringify(navigationHistory));
    }
}

function goBack() {
    // If user is in any option of main page, go back to main page
    // If user is in main page, go back to upload code page
    if (navigationHistory.length > 1) {
        navigationHistory.pop(); // Remove current page
        const previousPage = navigationHistory.pop(); // Get previous page
        sessionStorage.setItem('navigationHistory', JSON.stringify(navigationHistory));
        window.location.href = previousPage || '/upload-or-write';
    } else {
        // If no history, go to upload page
        window.location.href = '/upload-or-write';
    }
}

function toggleMenu() {
    const dropdownMenu = document.getElementById('dropdownMenu');
    dropdownMenu.classList.toggle('active');
}

// Close dropdown menu when clicking outside
document.addEventListener('click', function(event) {
    const menuIcon = document.querySelector('.menu-icon');
    const dropdownMenu = document.getElementById('dropdownMenu');
    
    if (!menuIcon.contains(event.target) && !dropdownMenu.contains(event.target)) {
        dropdownMenu.classList.remove('active');
    }
});

// Theme toggle function
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

let editor;
let currentLanguage = 'python';
let currentProfession = 'student';
let socket;
let languageDetectionTimeout = null;

// Define language-specific keywords and functions for autocomplete
const languageHints = {
    python: [
        'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally',
        'import', 'from', 'as', 'return', 'yield', 'with', 'lambda', 'and', 'or', 'not',
        'True', 'False', 'None', 'print', 'len', 'range', 'list', 'dict', 'set', 'tuple',
        'int', 'str', 'float', 'bool', 'open', 'read', 'write', 'append', 'close',
        'read_csv', 'read_excel', 'read_json', 'read_html', 'read_hdf', 'read_feather',
        'read_parquet', 'read_pickle', 'read_clipboard', 'read_gbq', 'read_msgpack', 'read_fwf'
    ],
    javascript: [
        'function', 'const', 'let', 'var', 'if', 'else', 'for', 'while', 'try', 'catch',
        'return', 'new', 'this', 'class', 'extends', 'import', 'export', 'async', 'await',
        'true', 'false', 'null', 'undefined', 'console.log', 'document', 'window', 'fetch',
        'Promise', 'Array', 'Object', 'String', 'Number', 'Boolean', 'Map', 'Set',
        'setTimeout', 'setInterval', 'addEventListener', 'querySelector', 'getElementById'
    ],
    java: [
        'public', 'private', 'protected', 'class', 'interface', 'extends', 'implements',
        'static', 'final', 'void', 'int', 'boolean', 'String', 'if', 'else', 'for', 'while',
        'try', 'catch', 'finally', 'return', 'new', 'this', 'super', 'System.out.println',
        'ArrayList', 'HashMap', 'List', 'Map', 'Set', 'Exception', 'Override', 'null', 'true', 'false'
    ],
    cpp: [
        'int', 'float', 'double', 'char', 'bool', 'void', 'class', 'struct', 'enum',
        'if', 'else', 'for', 'while', 'switch', 'case', 'break', 'continue', 'return',
        'try', 'catch', 'throw', 'new', 'delete', 'public', 'private', 'protected',
        'template', 'namespace', 'using', 'std', 'cout', 'cin', 'vector', 'string',
        'map', 'set', 'auto', 'const', 'static', 'virtual', 'override', 'true', 'false', 'nullptr'
    ]
};

// Custom hint function that combines language keywords with document words
function getCustomHint(cm, options) {
    const cursor = cm.getCursor();
    const line = cm.getLine(cursor.line);
    const start = cursor.ch;
    let end = cursor.ch;
    
    // Find the start of the current word
    while (start && /[\w\.$]/.test(line.charAt(start - 1))) --start;
    
    // Get the current word being typed
    const word = line.slice(start, end);
    const wordLower = word.toLowerCase();
    
    // Get language-specific keywords
    const language = currentLanguage.toLowerCase();
    const keywords = languageHints[language] || languageHints.python;
    
    // Get all words from the document
    const docWords = {};
    for (let i = 0; i < cm.lineCount(); i++) {
        const lineText = cm.getLine(i);
        const words = lineText.split(/[^\w\.]+/);
        for (let j = 0; j < words.length; j++) {
            if (words[j] && words[j].length > 1) {
                docWords[words[j]] = true;
            }
        }
    }
    
    // Combine keywords and document words
    const list = [];
    
    // Add matching keywords first (with higher priority)
    for (let i = 0; i < keywords.length; i++) {
        if (keywords[i].toLowerCase().indexOf(wordLower) === 0) {
            list.push({
                text: keywords[i],
                displayText: keywords[i],
                className: 'cm-keyword-hint',
                priority: 100
            });
        }
    }
    
    // Add matching document words
    for (const word in docWords) {
        if (word.toLowerCase().indexOf(wordLower) === 0 && !keywords.includes(word)) {
            list.push({
                text: word,
                displayText: word,
                className: 'cm-word-hint',
                priority: 50
            });
        }
    }
    
    // Sort by priority and then alphabetically
    list.sort((a, b) => {
        if (a.priority !== b.priority) return b.priority - a.priority;
        return a.text.localeCompare(b.text);
    });
    
    return {
        list: list,
        from: CodeMirror.Pos(cursor.line, start),
        to: CodeMirror.Pos(cursor.line, end)
    };
}

// Clear code function
function clearCode() {
    if (editor) {
        editor.setValue('');
        document.getElementById('outputContent').innerHTML = '<p class="placeholder">Click Review, Explain, or Compile to see AI analysis...</p>';
        document.getElementById('outputActions').style.display = 'none';
    }
}

// Test Gemini API function
async function testGeminiAPI() {
    showLoading('Testing Gemini AI connection...');
    
    try {
        const response = await fetch('/api/test-gemini', {
            method: 'GET',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        typewriterEffect(data.result);
        showOutputActions(); // Show copy, share, listen buttons
    } catch (error) {
        showError('Failed to test Gemini API. Please try again.');
    }
}

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
        extraKeys: {"Ctrl-Space": "autocomplete"},
        viewportMargin: Infinity, // Optimize for large files
        styleActiveLine: true,
        highlightSelectionMatches: {showToken: /\w/, annotateScrollbar: true},
        hintOptions: {
            completeSingle: false,
            alignWithWord: true,
            closeOnUnfocus: true,
            closeCharacters: /[\s()\[\]{};:>,]/,
            hint: getCustomHint
        }
    });
    
    // Enhanced autocomplete that shows automatically while typing
    editor.on("inputRead", function(cm, change) {
        if (change.text[0].match(/[a-zA-Z_0-9.]/)) {
            CodeMirror.commands.autocomplete(cm, null, {completeSingle: false});
        }
        // Send activity event when user types
        if (socket) {
            socket.emit('user_activity', {});
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

    // Debounced language detection for better performance
    editor.on('change', function() {
        clearTimeout(languageDetectionTimeout);
        languageDetectionTimeout = setTimeout(async function() {
            const code = editor.getValue();
            if (code.trim().length > 10) {
                try {
                    const response = await fetch('/api/detect-language', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({code: code})
                    });
                    const data = await response.json();
                    currentLanguage = data.language;
                    updateEditorMode(currentLanguage);
                } catch (error) {
                    console.error('Language detection failed:', error);
                }
            }
        }, 1000); // Wait 1 second after user stops typing
    });

    // Initialize Socket.IO for real-time chat functionality
    socket = io();
    
    // Send user activity event to update presence
    socket.emit('user_activity', {});
    
    // Set up periodic activity updates
    setInterval(function() {
        if (socket) {
            socket.emit('user_activity', {});
        }
    }, 60000); // Send activity update every minute
    
    socket.on('receive_message', function(data) {
        displayMessage(data);
    });

    socket.on('user_joined', function(data) {
        console.log(data.user + ' joined the chat');
    });

    socket.on('user_left', function(data) {
        console.log(data.user + ' left the chat');
    });
    
    // Listen for new notifications
    socket.on('new_notification', function(data) {
        if (data.user_id === '{{ user.id }}') {
            // Update notification badge
            updateNotificationBadge();
            
            // Show notification alert
            showNotification('You have a new notification!', 'info');
        }
    });
    
    // Listen for user presence updates
    socket.on('user_presence_update', function(data) {
        // Handle presence updates if needed
        console.log('User presence update:', data);
    });
});

// Profile dropdown toggle
function toggleProfileDropdown() {
    const profileDropdown = document.getElementById('profileDropdown');
    profileDropdown.classList.toggle('active');
}

// Close profile dropdown when clicking outside
document.addEventListener('click', function(event) {
    const profileLogo = document.querySelector('.profile-logo');
    const profileDropdown = document.getElementById('profileDropdown');
    
    if (!profileLogo.contains(event.target) && !profileDropdown.contains(event.target)) {
        profileDropdown.classList.remove('active');
    }
});

// Toggle chat - now navigates to chat page
function toggleChat() {
    window.location.href = '/chat';
}

// Open notifications
function openNotifications() {
    window.location.href = '/notifications';
}

// Show dictionary modal
function showDictionary() {
    const dictionaryModal = document.getElementById('dictionaryModal');
    dictionaryModal.classList.add('active');
}

// Show translate modal
function showTranslate() {
    const translateModal = document.getElementById('translateModal');
    translateModal.classList.add('active');
}

// Show history modal
function showHistory() {
    const historyModal = document.getElementById('historyModal');
    historyModal.classList.add('active');
}

// Open profile page
function openProfile() {
    window.location.href = '/profile';
}

// Open posts page
function openPosts() {
    window.location.href = '/posts';
}

// Open explore page
function openExplore() {
    window.location.href = '/explore';
}

// Logout function
function logout() {
    window.location.href = '/logout';
}

// Close modal function
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Attach file function
function attachFile() {
    // Create a hidden file input
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*,video/*,.pdf,.doc,.docx,.txt,.py,.js,.html,.css,.java,.cpp,.c';
    fileInput.style.display = 'none';
    
    fileInput.onchange = function(event) {
        const file = event.target.files[0];
        if (file) {
            // Handle file based on type
            if (file.type.startsWith('image/')) {
                displayImagePreview(file);
            } else if (file.type.startsWith('video/')) {
                displayVideoPreview(file);
            } else {
                // For other files, just send the file info
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Send file info as message
                    const message = `📎 File attached: ${file.name} (${formatFileSize(file.size)})`;
                    document.getElementById('chatInput').value = message;
                };
                reader.readAsDataURL(file);
            }
        }
    };
    
    document.body.appendChild(fileInput);
    fileInput.click();
    document.body.removeChild(fileInput);
}

// Display image preview
function displayImagePreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        // Create image preview modal
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.id = 'imagePreviewModal';
        modal.innerHTML = `
            <div class="modal-content" style="background: transparent; box-shadow: none; max-width: 90vw; max-height: 90vh;">
                <span class="close" onclick="closeModal('imagePreviewModal')" style="color: white; font-size: 2rem; position: absolute; top: 10px; right: 20px; cursor: pointer;">&times;</span>
                <img src="${e.target.result}" style="max-width: 100%; max-height: 80vh; border-radius: 10px; box-shadow: 0 0 30px rgba(0,0,0,0.5);" onclick="closeModal('imagePreviewModal')">
                <p style="text-align: center; color: white; margin-top: 10px;">${file.name}</p>
            </div>
        `;
        document.body.appendChild(modal);
    };
    reader.readAsDataURL(file);
}

// Display video preview
function displayVideoPreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        // Create video preview modal
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.id = 'videoPreviewModal';
        modal.innerHTML = `
            <div class="modal-content" style="background: transparent; box-shadow: none; max-width: 90vw; max-height: 90vh;">
                <span class="close" onclick="closeModal('videoPreviewModal')" style="color: white; font-size: 2rem; position: absolute; top: 10px; right: 20px; cursor: pointer;">&times;</span>
                <video controls style="max-width: 100%; max-height: 80vh; border-radius: 10px; box-shadow: 0 0 30px rgba(0,0,0,0.5);">
                    <source src="${e.target.result}" type="${file.type}">
                    Your browser does not support the video tag.
                </video>
                <p style="text-align: center; color: white; margin-top: 10px;">${file.name}</p>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Play video when modal is shown
        const video = modal.querySelector('video');
        setTimeout(() => {
            video.play();
        }, 500);
    };
    reader.readAsDataURL(file);
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Share code in chat
function shareCodeInChat() {
    // Get code from session storage or prompt user
    const code = sessionStorage.getItem('uploadedCode') || '';
    if (code) {
        document.getElementById('chatInput').value = 'Check out this code:\n```\n' + code + '\n```';
    } else {
        alert('No code available to share. Please upload or write some code first.');
    }
}

// Send message
function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (message) {
        // In a real implementation, this would send the message via socket
        // For now, we'll just add it to the chat display
        const chatMessages = document.getElementById('chatMessages');
        const now = new Date();
        const timeString = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        chatMessages.innerHTML += `
            <div class="message sent">
                <div class="message-content">
                    <div class="message-text">${message.replace(/\n/g, '<br>')}</div>
                    <div class="message-time">${timeString}</div>
                </div>
            </div>
        `;
        chatMessages.scrollTop = chatMessages.scrollHeight;
        input.value = '';
    }
}

// Handle enter key in chat
function handleChatEnter(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Start new chat
function startNewChat() {
    // For now, redirect to explore to find users to chat with
    window.location.href = '/explore';
}

// Add user activity tracking for various interactions
document.addEventListener('click', function(event) {
    // Send activity event on any user interaction
    if (socket) {
        socket.emit('user_activity', {});
    }
    
    const profileLogo = document.querySelector('.profile-logo');
    const profileDropdown = document.getElementById('profileDropdown');
    
    if (!profileLogo.contains(event.target) && !profileDropdown.contains(event.target)) {
        profileDropdown.classList.remove('active');
    }
});
