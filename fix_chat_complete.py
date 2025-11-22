"""
Complete fix for chat.html - adds lightbox and fixes message persistence
"""

# Read the file
with open('templates/chat.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix the displayMessages function to include file attachments
for i, line in enumerate(lines):
    # Fix 1: Update displayMessages function to render file attachments
    if 'function displayMessages(messages)' in line:
        # Find the function and replace it
        start_idx = i
        # Find the end of the function (look for the closing brace)
        brace_count = 0
        end_idx = i
        for j in range(i, len(lines)):
            if '{' in lines[j]:
                brace_count += lines[j].count('{')
            if '}' in lines[j]:
                brace_count -= lines[j].count('}')
            if brace_count == 0 and j > i:
                end_idx = j
                break
        
        # Replace the entire function
        new_function = '''        function displayMessages(messages) {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = messages.map(msg => {
                let content = '';
                
                // Handle file attachments
                if (msg.file_attachment) {
                    if (msg.file_type === 'image') {
                        content = `<img src="${msg.file_attachment}" alt="Image" style="max-width: 300px; border-radius: 8px; cursor: pointer;" onclick="openImageLightbox('${msg.file_attachment}')">`;
                    } else if (msg.file_type === 'video') {
                        content = `<video controls style="max-width: 300px; border-radius: 8px;">
                            <source src="${msg.file_attachment}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>`;
                    } else if (msg.file_type === 'pdf') {
                        content = `<a href="${msg.file_attachment}" target="_blank" style="display: inline-block; padding: 10px; background: #f0f0f0; border-radius: 8px; text-decoration: none; color: #333;">📄 PDF Document</a>`;
                    } else {
                        content = `<a href="${msg.file_attachment}" target="_blank" style="display: inline-block; padding: 10px; background: #f0f0f0; border-radius: 8px; text-decoration: none; color: #333;">📎 Download File</a>`;
                    }
                } else if (msg.code_snippet) {
                    content = `<div class="message-text code-message"><pre><code>${escapeHtml(msg.code_snippet)}</code></pre></div>`;
                } else {
                    content = msg.content || '';
                }
                
                return `
                <div class="message ${msg.sender_id === '{{ user.id }}' ? 'sent' : 'received'}">
                    ${msg.sender_id !== '{{ user.id }}' ? `<img src="${msg.sender_image || 'https://via.placeholder.com/32'}" alt="Profile" class="message-avatar">` : ''}
                    <div class="message-content">
                        <div class="message-text">${content}</div>
                        <div class="message-time">${formatTime(msg.created_at)}</div>
                    </div>
                </div>`;
            }).join('');
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
'''
        lines[start_idx:end_idx+1] = [new_function]
        break

# Write back
content = ''.join(lines)

# Fix 2: Add onclick to images in displayMessage function
content = content.replace(
    'messageContent = `<img src="${data.file_attachment}" alt="Image" style="max-width: 300px; max-height: 300px; border-radius: 8px;">`',
    'messageContent = `<img src="${data.file_attachment}" alt="Image" style="max-width: 300px; border-radius: 8px; cursor: pointer;" onclick="openImageLightbox(\'${data.file_attachment}\')">`'
)

# Fix 3: Add lightbox modal HTML before </body>
lightbox_html = '''
    <!-- Image Lightbox Modal -->
    <div id="imageLightbox" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 2000; justify-content: center; align-items: center;" onclick="closeImageLightbox()">
        <img id="lightboxImage" src="" style="max-width: 90%; max-height: 90%; object-fit: contain;" onclick="event.stopPropagation()">
        <button onclick="closeImageLightbox()" style="position: absolute; top: 20px; right: 30px; background: none; border: none; color: white; font-size: 40px; cursor: pointer; z-index: 2001;">&times;</button>
    </div>
</body>'''

content = content.replace('</body>', lightbox_html)

# Fix 4: Add lightbox JavaScript functions before </script>
lightbox_js = '''
        // Image lightbox functions
        function openImageLightbox(imageSrc) {
            const lightbox = document.getElementById('imageLightbox');
            const lightboxImage = document.getElementById('lightboxImage');
            lightboxImage.src = imageSrc;
            lightbox.style.display = 'flex';
        }

        function closeImageLightbox() {
            const lightbox = document.getElementById('imageLightbox');
            lightbox.style.display = 'none';
        }

    </script>'''

content = content.replace('    </script>', lightbox_js)

# Fix 5: Fix data.message to data.content
content = content.replace(
    "messageContent = data.message;",
    "messageContent = data.content || data.message || '';"
)

# Fix 6: Fix data.file_path to data.file_url
content = content.replace(
    "file_attachment: data.file_path,",
    "file_attachment: data.file_url,"
)

# Write the final content
with open('templates/chat.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully applied all chat fixes!")
print("- Fixed displayMessages to show file attachments")
print("- Added image onclick for lightbox")
print("- Added lightbox modal HTML")
print("- Added lightbox JavaScript functions")
print("- Fixed message content field (data.content)")
print("- Fixed file upload field (data.file_url)")
