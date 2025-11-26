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
document.addEventListener('click', function (event) {
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
let currentLanguage = 'python'; // Default to Python
let currentProfession = 'student';
let socket;
let languageDetectionTimeout = null;

// Update the display of the detected language
function updateLanguageDisplay(language) {
    // Language display has been removed per user request
    // Function kept for potential future use
    console.log('Detected language:', language);
}

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
    }
    document.getElementById('outputContent').innerHTML = '<p class="placeholder">Click Compile to execute your code...</p>';
    document.getElementById('outputActions').style.display = 'none';
    document.getElementById('inputContainer').style.display = 'none';
    isInteractiveProgram = false;
    currentExecId = null;
}

// Test Gemini API function
async function testGeminiAPI() {
    showLoading('Testing Gemini AI connection...');

    try {
        const response = await fetch('/api/test-gemini', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();
        typewriterEffect(data.result);
        showOutputActions(); // Show copy, share, listen buttons
    } catch (error) {
        showError('Failed to test Gemini API. Please try again.');
    }
}

// Get code from current editor
function getCurrentCode() {
    const code = editor ? editor.getValue() : '';
    console.log('Current code:', code);
    return code;
}

document.addEventListener('DOMContentLoaded', function () {
    editor = CodeMirror.fromTextArea(document.getElementById('codeEditor'), {
        mode: 'python',
        theme: 'monokai',
        lineNumbers: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 4,
        tabSize: 4,
        lineWrapping: true,
        extraKeys: { "Ctrl-Space": "autocomplete" },
        viewportMargin: Infinity, // Optimize for large files
        styleActiveLine: true,
        highlightSelectionMatches: { showToken: /\w/, annotateScrollbar: true },
        hintOptions: {
            completeSingle: false,
            alignWithWord: true,
            closeOnUnfocus: true,
            closeCharacters: /[\s()\[\]{};:>,]/,
            hint: getCustomHint
        }
    });

    // Enhanced autocomplete that shows automatically while typing
    editor.on("inputRead", function (cm, change) {
        if (change.text[0].match(/[a-zA-Z_0-9.]/)) {
            CodeMirror.commands.autocomplete(cm, null, { completeSingle: false });
        }
        // Don't send activity event - we want users to stay offline when on editor page
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
    editor.on('change', function () {
        clearTimeout(languageDetectionTimeout);
        languageDetectionTimeout = setTimeout(async function () {
            const code = editor.getValue();
            if (code.trim().length > 10) {
                try {
                    const response = await fetch('/api/detect-language', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ code: code })
                    });
                    const data = await response.json();
                    if (data.success) {
                        currentLanguage = data.language;
                        updateEditorMode(currentLanguage);
                        // updateLanguageDisplay removed per user request
                    }
                } catch (error) {
                    console.error('Language detection failed:', error);
                }
            } else if (code.trim().length === 0) {
                // If code is empty, reset to default
                currentLanguage = 'python';
                updateEditorMode(currentLanguage);
                // updateLanguageDisplay removed per user request
            }
        }, 1000); // Wait 1 second after user stops typing
    });

    // Initialize Socket.IO for real-time chat functionality
    socket = io();

    // IMPORTANT: Mark user as offline for chat since they're on editor page (not chat page)
    // This ensures users only show as "online" when actually on the chat page
    socket.emit('chat_window_closed', {});

    // Set up periodic offline status updates to ensure user stays offline
    setInterval(function () {
        if (socket) {
            socket.emit('chat_window_closed', {});
        }
    }, 60000); // Send offline update every minute

    socket.on('receive_message', function (data) {
        displayMessage(data);

        // Update chat badge when a new message arrives
        updateChatBadge();
    });

    socket.on('user_joined', function (data) {
        console.log(data.user + ' joined the chat');
    });

    socket.on('user_left', function (data) {
        console.log(data.user + ' left the chat');
    });

    // Listen for new notifications
    socket.on('new_notification', function (data) {
        if (data.user_id === '{{ user.id }}') {
            // Update notification badge
            updateNotificationBadge();

            // Show notification alert
            showNotification('You have a new notification!', 'info');
        }
    });

    // Listen for user presence updates
    socket.on('user_presence_update', function (data) {
        // Handle presence updates if needed
        console.log('User presence update:', data);
    });

    // Listen for new chat messages
    socket.on('new_chat_message', function (data) {
        // Update chat badge when a new message arrives
        updateChatBadge();
        displayMessage(data);
    });
    // Listen for execution output (interactive programs)
    socket.on('execution_output', function (data) {
        if (data.session_id === currentSessionId) {
            const outputContent = document.getElementById('outputContent');

            // Create output element
            const outputLine = document.createElement('div');
            outputLine.style.cssText = 'font-family: monospace; white-space: pre-wrap;';

            if (data.type === 'stderr') {
                outputLine.style.color = '#ff4757'; // Red for errors
            } else {
                outputLine.style.color = 'var(--text-color)';
            }

            outputLine.textContent = data.output;
            outputContent.appendChild(outputLine);

            // Auto-scroll to bottom
            outputContent.scrollTop = outputContent.scrollHeight;

            // Check if we should show input container
            if (shouldShowInputContainer(data.output)) {
                // Focus input if it looks like a prompt
                if (qnaInput) {
                    qnaInput.placeholder = "Enter input for your program...";
                    qnaInput.focus();
                }
            }
        }
    });

    // Listen for execution finished
    socket.on('execution_finished', function (data) {
        if (data.session_id === currentSessionId) {
            isInteractiveProgram = false;
            currentSessionId = null;

            const outputContent = document.getElementById('outputContent');
            const finishedLine = document.createElement('div');
            finishedLine.style.cssText = 'color: var(--text-secondary-color); font-style: italic; margin-top: 10px; border-top: 1px solid var(--border-color); padding-top: 5px;';
            finishedLine.textContent = 'Program finished.';
            outputContent.appendChild(finishedLine);
            outputContent.scrollTop = outputContent.scrollHeight;

            showOutputActions();
            if (qnaInput) qnaInput.placeholder = "Ask a question about your code...";
        }
    });
});

// Profile dropdown toggle
function toggleProfileDropdown() {
    const profileDropdown = document.getElementById('profileDropdown');
    profileDropdown.classList.toggle('active');
}

// ... (rest of functions) ...

// Open Chat Function
function openChat() {
    window.location.href = '/chat';
}

// Helper functions (previously nested, now global)
async function updateNotificationBadge() {
    try {
        const response = await fetch('/api/notifications/unread-count');
        const data = await response.json();
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            badge.textContent = data.count;
            badge.style.display = data.count > 0 ? 'flex' : 'none';
        }
    } catch (error) {
        console.error('Failed to update notification badge:', error);
    }
}

// Update chat badge
async function updateChatBadge() {
    try {
        const response = await fetch('/api/chats/unread-count');
        const data = await response.json();
        const badge = document.getElementById('chatBadge');
        if (badge) {
            badge.textContent = data.count;
            badge.style.display = data.count > 0 ? 'flex' : 'none';
        }
    } catch (error) {
        console.error('Failed to update chat badge:', error);
    }
}

// Show notification (placeholder)
function showNotification(message, type) {
    // This is a placeholder - in a full implementation, this would show a notification
    console.log(`${type}: ${message}`);
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
async function showTranslate() {
    const translateModal = document.getElementById('translateModal');
    translateModal.classList.add('active');

    // Auto-detect language from editor content
    const code = editor.getValue();
    const fromLangLabel = document.getElementById('fromLang');

    if (code.trim()) {
        fromLangLabel.innerHTML = '<span class="loading-dots">Detecting...</span>';
        try {
            // Use the existing currentLanguage if it was already detected by the editor
            // Or call API if needed (but editor usually detects it)

            // For now, let's use the currentLanguage variable which is updated by the editor's change listener
            // But let's double check with a quick API call to be sure for the modal
            const response = await fetch('/api/detect-language', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: code })
            });
            const data = await response.json();

            if (data.success) {
                const detectedLang = data.language.charAt(0).toUpperCase() + data.language.slice(1);
                fromLangLabel.textContent = `${detectedLang} (auto-detected)`;
                // Update currentLanguage global just in case
                currentLanguage = data.language;
            } else {
                fromLangLabel.textContent = `${currentLanguage} (auto-detected)`;
            }
        } catch (e) {
            console.error("Detection failed", e);
            fromLangLabel.textContent = `${currentLanguage} (auto-detected)`;
        }
    } else {
        fromLangLabel.textContent = "No code to detect";
    }
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

    fileInput.onchange = function (event) {
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
                reader.onload = function (e) {
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
    reader.onload = function (e) {
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
    reader.onload = function (e) {
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
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

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
document.addEventListener('click', function (event) {
    // Don't send activity event - we want users to stay offline when on editor page

    const profileLogo = document.querySelector('.profile-logo');
    const profileDropdown = document.getElementById('profileDropdown');

    if (!profileLogo.contains(event.target) && !profileDropdown.contains(event.target)) {
        profileDropdown.classList.remove('active');
    }
});

// Show loading indicator
function showLoading(message) {
    const outputContent = document.getElementById('outputContent');
    outputContent.style.padding = '1.5rem';
    outputContent.style.overflow = 'auto';
    outputContent.innerHTML = `<div class="loading">${message}</div>`;
    document.getElementById('outputActions').style.display = 'none';
    document.getElementById('inputContainer').style.display = 'none';
}

// Show error message
function showError(message) {
    const outputContent = document.getElementById('outputContent');
    outputContent.style.padding = '1.5rem';
    outputContent.style.overflow = 'auto';
    outputContent.innerHTML = `<div class="error">${message}</div>`;
    document.getElementById('outputActions').style.display = 'none';
    // Don't hide input container for interactive programs
    // document.getElementById('inputContainer').style.display = 'none';
}

// Show output actions (copy, share, listen)
function showOutputActions() {
    document.getElementById('outputActions').style.display = 'flex';
    // Hide input container by default
    document.getElementById('inputContainer').style.display = 'none';
}

// Typewriter effect for output with proper formatting
function typewriterEffect(text) {
    const outputContent = document.getElementById('outputContent');
    outputContent.innerHTML = '';
    currentOutput = text;

    // Preserve line breaks - convert \n to <br>
    // But we'll do this during typewriter effect to maintain animation
    let i = 0;
    const speed = 10; // typing speed in milliseconds
    let htmlContent = '';

    function typeWriter() {
        if (i < text.length) {
            const char = text.charAt(i);

            // Handle line breaks
            if (char === '\n') {
                htmlContent += '<br>';
            } else if (char === '\r') {
                // Skip carriage return, handle with \n
            } else {
                // Escape HTML characters
                if (char === '<') {
                    htmlContent += '&lt;';
                } else if (char === '>') {
                    htmlContent += '&gt;';
                } else if (char === '&') {
                    htmlContent += '&amp;';
                } else {
                    htmlContent += char;
                }
            }

            outputContent.innerHTML = htmlContent;
            outputContent.scrollTop = outputContent.scrollHeight;
            i++;
            setTimeout(typeWriter, speed);
        } else {
            // Final formatting - ensure proper spacing and line breaks
            outputContent.innerHTML = formatOutputText(htmlContent);
            showOutputActions(); // Show copy, share, listen buttons when done
        }
    }

    typeWriter();
}

// Format output text for better readability - ensure each point on new line
function formatOutputText(text) {
    let formatted = text;

    // Split text by <br> first to process line by line
    let parts = formatted.split('<br>');
    let processedParts = [];

    for (let part of parts) {
        let trimmed = part.trim();
        if (!trimmed) {
            processedParts.push('');
            continue;
        }

        // Check if this part has multiple bullet points on same line
        // Pattern: "text • point1 • point2" or "• point1 • point2"
        let bulletMatches = trimmed.match(/[•\-\*]\s+[^•\-\*]+/g);
        if (bulletMatches && bulletMatches.length > 1) {
            // Split by bullet points
            let bulletSplit = trimmed.split(/([•\-\*]\s+)/);
            let currentLine = '';
            for (let i = 0; i < bulletSplit.length; i++) {
                if (bulletSplit[i].match(/^[•\-\*]\s+$/)) {
                    // This is a bullet marker
                    if (currentLine.trim() && !currentLine.trim().match(/^[•\-\*]\s+/)) {
                        processedParts.push(currentLine.trim());
                        currentLine = '';
                    }
                    currentLine = bulletSplit[i];
                    if (i + 1 < bulletSplit.length) {
                        currentLine += bulletSplit[i + 1].trim();
                        i++; // Skip next as we've processed it
                    }
                    processedParts.push(currentLine.trim());
                    currentLine = '';
                } else if (bulletSplit[i].trim()) {
                    currentLine += bulletSplit[i];
                }
            }
            if (currentLine.trim()) {
                processedParts.push(currentLine.trim());
            }
        }
        // Check if this part has multiple numbered items
        else if (trimmed.match(/\d+\.\s+.*\d+\.\s+/)) {
            // Split by numbered items
            let numSplit = trimmed.split(/(\d+\.\s+)/);
            for (let i = 0; i < numSplit.length; i += 2) {
                if (numSplit[i] && numSplit[i + 1]) {
                    processedParts.push((numSplit[i] + numSplit[i + 1]).trim());
                }
            }
        }
        else {
            // Regular line - ensure bullet points and numbers are properly formatted
            // If line starts with bullet or number, keep as is
            if (trimmed.match(/^[•\-\*]\s+/) || trimmed.match(/^\d+\.\s+/)) {
                processedParts.push(trimmed);
            }
            // If line has bullet/number in middle, split it
            else if (trimmed.match(/[•\-\*]\s+/) || trimmed.match(/\d+\.\s+/)) {
                // Split by bullet
                let splitByBullet = trimmed.split(/([•\-\*]\s+)/);
                if (splitByBullet.length > 1) {
                    let beforeBullet = splitByBullet[0].trim();
                    if (beforeBullet) {
                        processedParts.push(beforeBullet);
                    }
                    for (let j = 1; j < splitByBullet.length; j += 2) {
                        if (splitByBullet[j] && splitByBullet[j + 1]) {
                            processedParts.push((splitByBullet[j] + splitByBullet[j + 1]).trim());
                        }
                    }
                } else {
                    processedParts.push(trimmed);
                }
            }
            else {
                processedParts.push(trimmed);
            }
        }
    }

    formatted = processedParts.join('<br>');

    // Final cleanup - ensure proper spacing
    formatted = formatted.replace(/(<br>\s*){3,}/g, '<br><br>');

    // Format section headers
    formatted = formatted.replace(/([^<])([A-Z][^:]*:)\s*(<br>|$)/g, '$1<br><strong>$2</strong><br>');

    // Format code blocks
    formatted = formatted.replace(/(```[\s\S]*?```)/g, '<pre style="background: rgba(0,0,0,0.1); padding: 10px; border-radius: 5px; margin: 10px 0; overflow-x: auto; white-space: pre-wrap; font-family: monospace;">$1</pre>');

    return formatted;
}

// Render HTML in output area
function renderHTML(htmlContent) {
    const outputContent = document.getElementById('outputContent');
    outputContent.innerHTML = `
        <iframe 
            srcdoc="${htmlContent.replace(/"/g, '&quot;')}" 
            style="width:100%; height:400px; border:none;">
        </iframe>
    `;
    showOutputActions();
}

// Handle input for interactive programs
function handleInput() {
    const input = document.getElementById('userInput').value;
    if (input) {
        // Show the input in the output area
        const outputContent = document.getElementById('outputContent');
        outputContent.innerHTML += `\n> ${input}`;

        // In a real implementation, we would send this input to the running process
        // For now, we'll just clear the input field and scroll
        document.getElementById('userInput').value = '';
        outputContent.scrollTop = outputContent.scrollHeight;
    }
}

// Update profession
function updateProfession() {
    currentProfession = document.getElementById('professionSelect').value;
}

// Update editor mode based on language
function updateEditorMode(language) {
    const modeMap = {
        'python': 'python',
        'javascript': 'javascript',
        'java': 'text/x-java',
        'c++': 'text/x-c++src',
        'cpp': 'text/x-c++src',
        'c': 'text/x-csrc',
        'html': 'htmlmixed',
        'css': 'css',
        'php': 'php',
        'ruby': 'ruby',
        'go': 'go',
        'rust': 'rust',
        'swift': 'swift',
        'sql': 'sql',
        'shell': 'shell'
    };

    const mode = modeMap[language.toLowerCase()] || 'python';
    editor.setOption('mode', mode);
}

// Review code function
async function reviewCode() {
    const code = getCurrentCode();
    if (!code.trim()) {
        showError('Please enter some code to review.');
        return;
    }

    showLoading('Reviewing your code...');

    try {
        const response = await fetch('/api/review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code: code,
                language: currentLanguage,
                profession: currentProfession
            })
        });

        const data = await response.json();
        if (data.success) {
            typewriterEffect(data.result);
        } else {
            showError(data.result || 'Failed to review code.');
        }
    } catch (error) {
        showError('Failed to review code. Please try again.');
        console.error('Review error:', error);
    }
}

// Explain code function
async function explainCode() {
    const code = getCurrentCode();
    if (!code.trim()) {
        showError('Please enter some code to explain.');
        return;
    }

    showLoading('Explaining your code...');

    try {
        const response = await fetch('/api/explain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code: code,
                language: currentLanguage,
                profession: currentProfession
            })
        });

        const data = await response.json();
        if (data.success) {
            typewriterEffect(data.result);
        } else {
            showError(data.result || 'Failed to explain code.');
        }
    } catch (error) {
        showError('Failed to explain code. Please try again.');
        console.error('Explain error:', error);
    }
}

// Global variable to track if we're running an interactive program
let isInteractiveProgram = false;
let programExecutionId = null;
let currentExecId = null; // Store current execution ID for interactive programs
let currentSessionId = null; // For socket-based interactive programs

// Compile code function
// Store execution session ID
let executionSessionId = null;
let waitingForPreInput = false;
let preExecutionInput = null;

document.addEventListener('DOMContentLoaded', function () {
    // Listen for execution output
    socket.on('execution_output', function (data) {
        if (data.session_id === currentSessionId) {
            const outputContent = document.getElementById('outputContent');
            // Remove placeholder if present
            const placeholder = outputContent.querySelector('.placeholder');
            if (placeholder) {
                outputContent.innerHTML = '';
            }

            // Append output
            // Convert newlines to <br> and handle basic ANSI codes if needed (simplified here)
            const text = data.output.replace(/\n/g, '<br>').replace(/ /g, '&nbsp;');
            const span = document.createElement('span');
            span.innerHTML = text;
            outputContent.appendChild(span);

            // Auto-scroll to bottom
            outputContent.scrollTop = outputContent.scrollHeight;

            // Update search bar placeholder to indicate input is expected
            const qnaInput = document.getElementById('qnaInput');
            if (qnaInput) {
                qnaInput.placeholder = "Program running... Type input here and press Enter";
                qnaInput.focus();
            }
        }
    });

    // Listen for execution finished
    socket.on('execution_finished', function (data) {
        if (data.session_id === currentSessionId) {
            // Execution finished
            const outputContent = document.getElementById('outputContent');
            const finishedMsg = document.createElement('div');
            finishedMsg.className = 'execution-status';
            finishedMsg.innerHTML = '<br><em>Program finished with exit code 0</em>';
            finishedMsg.style.color = '#888';
            finishedMsg.style.marginTop = '10px';
            outputContent.appendChild(finishedMsg);

            // Reset search bar
            const qnaInput = document.getElementById('qnaInput');
            if (qnaInput) {
                qnaInput.placeholder = "Ask a question about your code...";
                qnaInput.value = '';
            }

            // Show output actions
            showOutputActions();

            currentSessionId = null;
            isInteractiveProgram = false;
        }
    });
});

async function compileCode(input = null) {
    console.log('compileCode function called');

    const code = getCurrentCode();
    console.log('Code to compile:', code);

    if (!code.trim()) {
        console.log('No code to compile');
        showError('Please enter some code to compile.');
        return;
    }

    showLoading('Executing your code...');

    // Auto-detect language from content if possible (to handle incorrect dropdown selection)
    if (code.includes('public class') && code.includes('static void main')) {
        currentLanguage = 'java';
        console.log('Auto-detected Java');
    } else if (code.includes('#include') && code.includes('<iostream>')) {
        currentLanguage = 'cpp';
        console.log('Auto-detected C++');
    } else if (code.includes('#include') && code.includes('<stdio.h>')) {
        currentLanguage = 'c';
        console.log('Auto-detected C');
    }

    // Pre-execution input check REMOVED to allow true interactive mode
    // The backend will now handle interactivity via WebSockets

    // Generate session ID for this execution
    executionSessionId = Date.now().toString();
    currentSessionId = executionSessionId;
    isInteractiveProgram = true;

    // Update search bar placeholder
    const qnaInput = document.getElementById('qnaInput');
    if (qnaInput) {
        qnaInput.placeholder = "Program running... Type input here and press Enter";
    }

    try {
        console.log('Sending request to /api/execute with data:', {
            code: code,
            language: currentLanguage,
            session_id: executionSessionId
        });

        const response = await fetch('/api/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code: code,
                language: currentLanguage,
                session_id: executionSessionId,
                stdin: input || preExecutionInput || ""
            })
        });

        // Clear pre-input state
        preExecutionInput = null;
        waitingForPreInput = false;

        // Log the response for debugging
        console.log('API Response Status:', response.status);
        console.log('API Response Object:', response);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error Response Text:', errorText);
            showError(`API Error: ${response.status} ${response.statusText} - ${errorText}`);
            isInteractiveProgram = false;
            return;
        }

        const data = await response.json();
        console.log('API Response Data:', data);

        if (data.success) {
            // Handle web languages (HTML, CSS, JSP) - show in iframe in output frame AND open in new tab
            if (data.type === 'web' && (data.url || data.file_path)) {
                isInteractiveProgram = false;
                currentExecId = null;
                const outputContent = document.getElementById('outputContent');
                // Clear any existing content and set up iframe container
                outputContent.innerHTML = '';
                outputContent.style.padding = '0';
                outputContent.style.overflow = 'hidden';
                outputContent.style.height = '100%';

                // Use the correct URL property
                const url = data.url || data.file_path;

                // Show in iframe within the output frame
                const iframe = document.createElement('iframe');
                iframe.src = url;
                iframe.style.cssText = 'width:100%; height:100%; min-height:500px; border:none; background: white; display:block;';
                iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-forms allow-popups');
                outputContent.appendChild(iframe);

                // Open in new browser tab as requested
                window.open(url, '_blank');

                showOutputActions();
                hideInputContainer();

                // Reset search bar
                if (qnaInput) qnaInput.placeholder = "Ask a question about your code...";
            }
            // Handle Piston/Cloud execution output
            else if (data.type === 'piston' || data.output) {
                isInteractiveProgram = false;
                currentExecId = null;
                const outputContent = document.getElementById('outputContent');
                outputContent.style.padding = '1.5rem';
                outputContent.style.overflow = 'auto';

                // Display the output directly
                typewriterEffect(data.output || data.result || 'Code executed successfully.');

                hideInputContainer();

                // Reset search bar
                if (qnaInput) qnaInput.placeholder = "Ask a question about your code...";
            }
            // Handle interactive programs - terminal-like interface
            else if (data.type === 'interactive') {
                // Output will be streamed via socket
                const outputContent = document.getElementById('outputContent');
                outputContent.innerHTML = ''; // Clear loading message
                outputContent.style.padding = '1.5rem';
                outputContent.style.overflow = 'auto';

                // Focus search bar for input
                if (qnaInput) qnaInput.focus();
            }
            // Handle regular output
            else if (data.type === 'output') {
                isInteractiveProgram = false;
                currentExecId = null;
                const outputContent = document.getElementById('outputContent');
                outputContent.style.padding = '1.5rem';
                outputContent.style.overflow = 'auto';
                // Show actual output - check if result exists and has content
                const result = data.result || '';
                if (result && result.trim().length > 0) {
                    // We have actual output - show it
                    typewriterEffect(result);
                } else if (result === '' || result === null || result === undefined) {
                    // Truly no output - show message
                    outputContent.innerHTML = '<div style="color: var(--text-color); padding: 20px; text-align: center;"><p>✅ Code executed successfully.</p><p style="color: var(--text-secondary-color); font-size: 0.9em; margin-top: 10px;">No output was produced by the program.</p></div>';
                    showOutputActions();
                } else {
                    // Fallback - show whatever we got
                    typewriterEffect(result);
                }
                hideInputContainer();
            }
            // Handle errors
            else if (data.type === 'error') {
                isInteractiveProgram = false;
                currentExecId = null;
                const outputContent = document.getElementById('outputContent');
                outputContent.style.padding = '1.5rem';
                outputContent.style.overflow = 'auto';
                showError(data.result);
                hideInputContainer();
            }
            // Default - show result
            else {
                isInteractiveProgram = false;
                currentExecId = null;
                const outputContent = document.getElementById('outputContent');
                outputContent.style.padding = '1.5rem';
                outputContent.style.overflow = 'auto';
                typewriterEffect(data.result || 'Code executed successfully.');
                hideInputContainer();
            }
        } else {
            isInteractiveProgram = false;
            currentExecId = null;
            showError(data.result || data.error || 'Failed to execute code.');
            if (qnaInput) qnaInput.placeholder = "Ask a question about your code...";
        }
    } catch (error) {
        console.error('Error compiling code:', error);
        showError('Failed to connect to the server. Please try again.');
        isInteractiveProgram = false;
        if (qnaInput) qnaInput.placeholder = "Ask a question about your code...";
    }
}

// Render HTML in output area
function renderHTML(htmlContent) {
    const outputContent = document.getElementById('outputContent');
    outputContent.innerHTML = `
        <iframe 
            srcdoc="${htmlContent.replace(/"/g, '&quot;')}" 
            style="width:100%; height:400px; border:none;"
            sandbox="allow-scripts allow-same-origin">
        </iframe>
    `;
    showOutputActions();
}

// Show input container for interactive programs
function showInputContainer() {
    document.getElementById('inputContainer').style.display = 'flex';
    document.getElementById('userInput').focus();
}

// Hide input container
function hideInputContainer() {
    document.getElementById('inputContainer').style.display = 'none';
    document.getElementById('userInput').value = '';
}

// Check if we should show the input container based on the output
function shouldShowInputContainer(output) {
    if (!output) return false;

    // Common patterns that indicate a program is waiting for input
    const inputIndicators = [
        'Enter', 'input', 'please', 'num', 'value', 'choice',
        'select', 'option', 'enter a', 'enter the', 'provide',
        'type', 'insert', 'write', 'key in'
    ];

    // Check if output ends with a prompt character
    if (output.trim().endsWith(':') || output.trim().endsWith('?')) {
        return true;
    }

    // Check for common input indicators
    const lowerOutput = output.toLowerCase();
    return inputIndicators.some(indicator => lowerOutput.includes(indicator));
}

// Handle input for interactive programs - terminal-like experience
async function handleTerminalInput() {
    const terminalInput = document.getElementById('terminalInput');
    const input = terminalInput.value;
    // Allow empty string, '0', and any other input
    if (input === null || input === undefined) return;

    const terminalOutput = document.getElementById('terminalOutput');
    const inputLine = document.createElement('div');
    inputLine.style.cssText = 'color: var(--accent-color); font-family: monospace;';
    inputLine.textContent = `$ ${input}`;
    terminalOutput.appendChild(inputLine);

    // Clear input field
    terminalInput.value = '';

    // Scroll to bottom
    terminalOutput.scrollTop = terminalOutput.scrollHeight;

    // Send input to backend
    if (currentExecId) {
        try {
            const response = await fetch('/api/execute/input', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    exec_id: currentExecId,
                    input: input
                })
            });

            const data = await response.json();

            if (data.success) {
                // Append output to terminal
                if (data.result) {
                    const outputLine = document.createElement('div');
                    outputLine.style.cssText = 'color: var(--text-color); font-family: monospace; margin-top: 5px;';
                    outputLine.textContent = data.result;
                    terminalOutput.appendChild(outputLine);
                }

                // Check if program finished
                if (data.finished) {
                    isInteractiveProgram = false;
                    currentExecId = null;
                    // Remove input line
                    const inputLineDiv = document.getElementById('terminalInputLine');
                    if (inputLineDiv) {
                        inputLineDiv.style.display = 'none';
                    }
                    showOutputActions();
                } else {
                    // Keep input line visible for more input
                    terminalInput.focus();
                }
            } else {
                const errorLine = document.createElement('div');
                errorLine.style.cssText = 'color: #ff4757; font-family: monospace; margin-top: 5px;';
                errorLine.textContent = `Error: ${data.error || 'Unknown error'}`;
                terminalOutput.appendChild(errorLine);
            }

            terminalOutput.scrollTop = terminalOutput.scrollHeight;
        } catch (error) {
            const errorLine = document.createElement('div');
            errorLine.style.cssText = 'color: #ff4757; font-family: monospace; margin-top: 5px;';
            errorLine.textContent = `Error: ${error.message}`;
            terminalOutput.appendChild(errorLine);
            terminalOutput.scrollTop = terminalOutput.scrollHeight;
        }
    }
}

// Legacy function for backward compatibility
async function handleInput() {
    // Check if we're using terminal input
    const terminalInput = document.getElementById('terminalInput');
    if (terminalInput) {
        await handleTerminalInput();
        return;
    }

    // Fallback to old input container
    const input = document.getElementById('userInput').value;
    if (!input || !input.trim()) return;

    const outputContent = document.getElementById('outputContent');

    // Display user input in terminal-like format with proper formatting
    const inputLine = `<div style="color: var(--accent-color); margin: 5px 0; font-family: monospace;">$ <span style="color: var(--text-color);">${escapeHtml(input)}</span></div>`;
    outputContent.innerHTML += inputLine;
    outputContent.scrollTop = outputContent.scrollHeight;

    // Clear input field
    document.getElementById('userInput').value = '';
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Handle Q&A enter key
function handleQnAEnter(event) {
    if (event.key === 'Enter') {
        // Check if we are in an interactive session
        if (isInteractiveProgram && currentSessionId) {
            const inputField = document.getElementById('qnaInput');
            const input = inputField.value;

            // Display input in output window for better context
            const outputContent = document.getElementById('outputContent');
            const inputDisplay = document.createElement('span');
            inputDisplay.textContent = input + '\n';
            inputDisplay.style.color = '#4CAF50'; // Green color for user input
            inputDisplay.style.fontWeight = 'bold';
            outputContent.appendChild(inputDisplay);
            outputContent.scrollTop = outputContent.scrollHeight;

            // Send input to server
            socket.emit('execution_input', {
                session_id: currentSessionId,
                input: input
            });

            inputField.value = '';
            return;
        }

        // Normal Q&A behavior
        askQuestion();
    }
}

// Ask question function
async function askQuestion() {
    const question = document.getElementById('qnaInput').value.trim();
    const code = getCurrentCode();

    if (!question) {
        showError('Please enter a question.');
        return;
    }

    showLoading('Thinking...');

    try {
        const response = await fetch('/api/question', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: question,
                code: code,
                language: currentLanguage
            })
        });

        const data = await response.json();
        if (data.success) {
            typewriterEffect(data.result);
            document.getElementById('qnaInput').value = '';
        } else {
            showError(data.result || 'Failed to answer question.');
        }
    } catch (error) {
        showError('Failed to answer question. Please try again.');
        console.error('Question error:', error);
    }
}

// Copy output function
function copyOutput() {
    navigator.clipboard.writeText(currentOutput).then(() => {
        // Show confirmation
        const copyBtn = document.querySelector('.output-action-btn');
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> Copied!';
        setTimeout(() => {
            copyBtn.innerHTML = originalText;
        }, 2000);
    });
}

// Share output function
function shareOutput() {
    // For now, just copy to clipboard
    copyOutput();
}

// Listen to output function
function listenOutput() {
    // Simple text-to-speech
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(currentOutput);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        speechSynthesis.speak(utterance);
    } else {
        alert('Text-to-speech not supported in your browser.');
    }
}

// Translate code function
// Translate code function
async function translateCode() {
    const code = editor.getValue();
    const toLang = document.getElementById('toLang').value;

    if (!code.trim()) {
        alert('Please enter some code to translate.');
        return;
    }

    // Allow translation even if languages seem same, as user might want to fix syntax or change style
    // But warn if they are exactly the same string
    if (currentLanguage.toLowerCase() === toLang.toLowerCase()) {
        if (!confirm(`Source and target languages appear to be the same (${toLang}). Continue anyway?`)) {
            return;
        }
    }

    const translateResult = document.getElementById('translateResult');
    translateResult.innerHTML = '<div class="loading">Translating code...</div>';

    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code: code,
                from_lang: currentLanguage,
                to_lang: toLang
            })
        });

        const data = await response.json();
        if (data.success) {
            // Create a container with relative positioning for the copy button
            const codeHtml = `
                <div style="position: relative; margin-top: 10px;">
                    <button onclick="copyTranslateCode(this)" style="
                        position: absolute;
                        top: 5px;
                        right: 5px;
                        background: rgba(255, 255, 255, 0.1);
                        border: 1px solid var(--border-color);
                        border-radius: 4px;
                        color: var(--text-color);
                        padding: 4px 8px;
                        font-size: 12px;
                        cursor: pointer;
                        z-index: 10;
                        display: flex;
                        align-items: center;
                        gap: 4px;
                    ">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                        Copy
                    </button>
                    <pre style="padding-top: 30px;"><code id="translateCodeResult">${data.result}</code></pre>
                </div>
            `;
            translateResult.innerHTML = codeHtml;
        } else {
            translateResult.innerHTML = `<div class="error">${data.result || 'Failed to translate code.'}</div>`;
        }
    } catch (error) {
        translateResult.innerHTML = '<div class="error">Failed to translate code. Please try again.</div>';
        console.error('Translation error:', error);
    }
}

// Copy translated code
function copyTranslateCode(btn) {
    const codeElement = document.getElementById('translateCodeResult');
    if (codeElement) {
        const code = codeElement.textContent;
        navigator.clipboard.writeText(code).then(() => {
            // Visual feedback
            const originalHtml = btn.innerHTML;
            btn.innerHTML = `
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                Copied!
            `;
            btn.style.background = 'rgba(46, 204, 113, 0.2)';
            btn.style.borderColor = '#2ecc71';

            setTimeout(() => {
                btn.innerHTML = originalHtml;
                btn.style.background = 'rgba(255, 255, 255, 0.1)';
                btn.style.borderColor = 'var(--border-color)';
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy:', err);
            alert('Failed to copy code to clipboard');
        });
    }
}

// Update dictionary language
function updateDictionaryLanguage() {
    searchDictionary();
}

// Search dictionary
// Search dictionary
async function searchDictionary() {
    const searchTerm = document.getElementById('dictSearch').value.trim();
    const language = document.getElementById('dictLanguage').value;
    const dictionaryContent = document.getElementById('dictionaryContent');

    if (!searchTerm) {
        dictionaryContent.innerHTML = '<p class="placeholder">Enter a term to search for code templates...</p>';
        return;
    }

    dictionaryContent.innerHTML = '<div class="loading">Searching...</div>';

    try {
        const response = await fetch('/api/dictionary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                term: searchTerm,
                language: language
            })
        });

        const data = await response.json();
        if (data.success) {
            // Create a container with relative positioning for the copy button
            const codeHtml = `
                <div style="position: relative; margin-top: 10px;">
                    <button onclick="copyDictionaryCode(this)" style="
                        position: absolute;
                        top: 5px;
                        right: 5px;
                        background: rgba(255, 255, 255, 0.1);
                        border: 1px solid var(--border-color);
                        border-radius: 4px;
                        color: var(--text-color);
                        padding: 4px 8px;
                        font-size: 12px;
                        cursor: pointer;
                        z-index: 10;
                        display: flex;
                        align-items: center;
                        gap: 4px;
                    ">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                        Copy
                    </button>
                    <pre style="padding-top: 30px;"><code id="dictionaryCodeResult">${data.result}</code></pre>
                </div>
            `;
            dictionaryContent.innerHTML = codeHtml;
        } else {
            dictionaryContent.innerHTML = `<div class="error">${data.result || 'Failed to get dictionary content.'}</div>`;
        }
    } catch (error) {
        dictionaryContent.innerHTML = '<div class="error">Failed to get dictionary content. Please try again.</div>';
        console.error('Dictionary error:', error);
    }
}

// Copy dictionary code
function copyDictionaryCode(btn) {
    const codeElement = document.getElementById('dictionaryCodeResult');
    if (codeElement) {
        const code = codeElement.textContent;
        navigator.clipboard.writeText(code).then(() => {
            // Visual feedback
            const originalHtml = btn.innerHTML;
            btn.innerHTML = `
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                Copied!
            `;
            btn.style.background = 'rgba(46, 204, 113, 0.2)';
            btn.style.borderColor = '#2ecc71';

            setTimeout(() => {
                btn.innerHTML = originalHtml;
                btn.style.background = 'rgba(255, 255, 255, 0.1)';
                btn.style.borderColor = 'var(--border-color)';
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy:', err);
            alert('Failed to copy code to clipboard');
        });
    }
}
