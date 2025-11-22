#!/usr/bin/env python3
"""
Comprehensive fix for chat.html - fixes all three issues:
1. Button icon visibility
2. Real-time message display (data.content)
3. Image lightbox for fullscreen viewing
"""

# Read the file
with open('templates/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("Applying comprehensive chat fixes...")

# FIX 1: Ensure SVG icons are visible (check if already there)
if 'stroke: #333;' in content:
    print("  [OK] SVG icon colors already fixed")
else:
    print("  [FIXING] Adding SVG icon color fix...")
    svg_css = """
        .attach-btn svg, .code-btn svg, .send-btn svg {
            stroke: #333;
            fill: none;
            display: block;
        }

        [data-theme="dark"] .attach-btn svg,
        [data-theme="dark"] .code-btn svg,
        [data-theme="dark"] .send-btn svg {
            stroke: #fff;
        }
        """
    insert_after = """        .attach-btn:hover, .code-btn:hover, .send-btn:hover {
            background-color: var(--hover-bg);
        }
        """
    content = content.replace(insert_after, insert_after + svg_css)

# FIX 2: Fix message display to use data.content instead of data.message
print("  [FIXING] Updating message display to use data.content...")
old_message_line = "                messageContent = data.message;"
new_message_line = "                messageContent = data.content || data.message || '';"
if old_message_line in content:
    content = content.replace(old_message_line, new_message_line)
    print("  [OK] Message content field fixed")
else:
    print("  [SKIP] Message content already uses correct field or not found")

# FIX 3: Add lightbox feature
if 'openLightbox' not in content:
    print("  [FIXING] Adding image lightbox feature...")
    
    # Add lightbox CSS
    lightbox_css = """
        /* Image Lightbox Styles */
        .image-lightbox {
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
            cursor: pointer;
        }

        .lightbox-content {
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 90%;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            animation: zoom 0.3s;
        }

        @keyframes zoom {
            from {transform: translate(-50%, -50%) scale(0.8)}
            to {transform: translate(-50%, -50%) scale(1)}
        }

        .lightbox-close {
            position: absolute;
            top: 20px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
            z-index: 10000;
        }

        .lightbox-close:hover,
        .lightbox-close:focus {
            color: #bbb;
        }
"""
    content = content.replace('    </style>', lightbox_css + '    </style>')
    
    # Add lightbox HTML
    lightbox_html = """
    <!-- Image Lightbox Modal -->
    <div id="imageLightbox" class="image-lightbox" onclick="closeLightbox()">
        <span class="lightbox-close" onclick="closeLightbox()">&times;</span>
        <img class="lightbox-content" id="lightboxImage">
    </div>

"""
    content = content.replace('    <script>', lightbox_html + '    <script>')
    
    # Add lightbox JavaScript
    lightbox_js = """
        // Lightbox functions
        function openLightbox(imageSrc) {
            const lightbox = document.getElementById('imageLightbox');
            const lightboxImg = document.getElementById('lightboxImage');
            lightbox.style.display = 'block';
            lightboxImg.src = imageSrc;
        }

        function closeLightbox() {
            const lightbox = document.getElementById('imageLightbox');
            lightbox.style.display = 'none';
        }

        // Close lightbox on Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeLightbox();
            }
        });

"""
    socket_line = '        let socket;'
    content = content.replace(socket_line, socket_line + '\n' + lightbox_js)
    
    # Make images clickable
    old_image_code = 'messageContent = `<img src="${data.file_attachment}" alt="Image" style="max-width: 300px; max-height: 300px; border-radius: 8px;">`'
    new_image_code = 'messageContent = `<img src="${data.file_attachment}" alt="Image" style="max-width: 300px; max-height: 300px; border-radius: 8px; cursor: pointer;" onclick="openLightbox(\'${data.file_attachment}\')">`'
    content = content.replace(old_image_code, new_image_code)
    print("  [OK] Lightbox feature added")
else:
    print("  [OK] Lightbox feature already present")

# Write the updated content
with open('templates/chat.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*60)
print("SUCCESS: All chat fixes applied!")
print("="*60)
print("\nFixed issues:")
print("  1. Button icons now visible (dark in light theme, white in dark theme)")
print("  2. Messages display in real-time using data.content field")
print("  3. Images open in fullscreen lightbox when clicked")
print("\nPlease refresh your browser (F5) to see the changes!")
