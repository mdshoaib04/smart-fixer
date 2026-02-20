#!/usr/bin/env python3
"""
Fix profile page structural and logic issues
"""

import re

def fix_profile_issues():
    # Read the profile.html file
    with open('templates/profile.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Remove duplicate closing tags and JavaScript leakage
    # Find the problematic section and fix it
    pattern = r'(</script>\s*</body>\s*</html>\s*</body>\s*</html>\s*showNotification.*?})'
    replacement = '</script>\n    </div>\n    </body>\n\n</html>'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Fix 2: Fix post click handlers to use modal instead of 404 navigation
    content = content.replace(
        'onclick="window.location.href=\'/post/${post.id}\'"', 
        'onclick="openPostModal(${post.id})"'
    )
    
    # Fix 3: Add proper CSS for scroll and layout
    css_fixes = """
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
    """
    
    # Insert CSS fixes after the existing style tag
    content = content.replace(
        '</style>',
        css_fixes + '\n    </style>'
    )
    
    # Fix 4: Add post modal HTML
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
    
    # Insert modal before the closing </div> of profile-page
    content = content.replace(
        '</div>\n    </body>',
        modal_html + '\n    </div>\n    </body>'
    )
    
    # Fix 5: Add proper JavaScript functions for post modal
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
    
    # Insert JavaScript functions before the closing </script>
    content = content.replace(
        '</script>',
        js_functions + '\n    </script>'
    )
    
    # Write the fixed content back
    with open('templates/profile.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Profile page issues fixed successfully!")
    print("✅ Fixed scroll and header overlap")
    print("✅ Fixed followers/following positioning")
    print("✅ Removed JavaScript leakage")
    print("✅ Fixed post click to use modal")
    print("✅ Added post modal functionality")

if __name__ == '__main__':
    fix_profile_issues()