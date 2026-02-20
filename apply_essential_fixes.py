#!/usr/bin/env python3
"""
Apply essential fixes to profile.html
"""

def apply_fixes():
    # Read the profile.html file
    with open('templates/profile.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix 1: Remove JavaScript leakage at the end
    if 'showNotification(' in content:
        # Find the problematic section and remove it
        lines = content.split('\n')
        cleaned_lines = []
        skip = False
        for line in lines:
            if 'showNotification(' in line and '</script>' in content[content.find(line):]:
                skip = True
                continue
            if skip and line.strip() == '</script>':
                skip = False
                continue
            if not skip:
                cleaned_lines.append(line)
        content = '\n'.join(cleaned_lines)

    # Fix 2: Fix post click handlers
    content = content.replace("onclick=\"window.location.href='/post/${post.id}'\"", "onclick=\"openPostModal(${post.id})\"")

    # Fix 3: Add proper CSS
    css_fixes = '''
    body {
        overflow-x: hidden;
    }
    
    .profile-page {
        min-height: 100vh;
        overflow-y: auto;
        padding-top: 0;
    }
    
    .profile-header {
        position: relative;
    }
    
    .profile-stats {
        display: flex;
        justify-content: center;
        gap: 40px;
        text-align: center;
        margin-top: 20px;
        width: 100%;
    }
    
    .profile-info {
        margin-top: 20px;
    }
'''

    # Insert CSS fixes
    content = content.replace('</style>', css_fixes + '\n    </style>')

    # Fix 4: Add post modal if not exists
    if 'id="postModal"' not in content:
        modal_html = '''
    <!-- Post Detail Modal -->
    <div id="postModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Post Details</h2>
                <span class="close" onclick="closePostModal()">&times;</span>
            </div>
            <div class="modal-body">
                <div id="postModalContent">
                    <div class="loading">Loading post...</div>
                </div>
            </div>
        </div>
    </div>
    '''
        content = content.replace('</div>\n    </body>', modal_html + '\n    </div>\n    </body>')

    # Fix 5: Add post modal functions if not exists
    if 'function openPostModal' not in content:
        js_functions = '''
    
    // Post Modal Functions
    function openPostModal(postId) {
        const modal = document.getElementById('postModal');
        const content = document.getElementById('postModalContent');
        
        // Show loading
        content.innerHTML = '<div class="loading">Loading post...</div>';
        modal.style.display = 'block';
        
        // Fetch post details
        fetch(`/api/posts/${postId}`)
            .then(response => response.json())
            .then(data => {
                if (data.code) {
                    content.innerHTML = `
                        <div class="post-detail">
                            <pre><code>${escapeHtml(data.code)}</code></pre>
                            <div class="post-meta">
                                <p><strong>Language:</strong> ${data.language || 'Unknown'}</p>
                                <p><strong>Created:</strong> ${new Date(data.created_at).toLocaleDateString()}</p>
                            </div>
                        </div>
                    `;
                } else {
                    content.innerHTML = '<div class="error">Post not found</div>';
                }
            })
            .catch(error => {
                console.error('Error loading post:', error);
                content.innerHTML = '<div class="error">Failed to load post</div>';
            });
    }
    
    function closePostModal() {
        document.getElementById('postModal').style.display = 'none';
    }
    '''
        content = content.replace('</script>', js_functions + '\n    </script>')

    # Write the fixed content back
    with open('templates/profile.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print('✅ Applied essential fixes')

if __name__ == '__main__':
    apply_fixes()