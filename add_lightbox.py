#!/usr/bin/env python3
"""
Script to add image lightbox feature to chat.html
"""

# Read the file
with open('templates/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

# CSS for lightbox
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

# Insert CSS before </style>
content = content.replace('    </style>', lightbox_css + '    </style>')

# HTML for lightbox modal
lightbox_html = """
    <!-- Image Lightbox Modal -->
    <div id="imageLightbox" class="image-lightbox" onclick="closeLightbox()">
        <span class="lightbox-close" onclick="closeLightbox()">&times;</span>
        <img class="lightbox-content" id="lightboxImage">
    </div>

"""

# Insert HTML before <script>
content = content.replace('    <script>', lightbox_html + '    <script>')

# JavaScript functions for lightbox
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

# Insert JavaScript after the socket variable declarations
socket_line = '        let socket;'
content = content.replace(socket_line, socket_line + '\n' + lightbox_js)

# Update image display to be clickable
old_image_code = 'messageContent = `<img src="${data.file_attachment}" alt="Image" style="max-width: 300px; max-height: 300px; border-radius: 8px;">';
new_image_code = 'messageContent = `<img src="${data.file_attachment}" alt="Image" style="max-width: 300px; max-height: 300px; border-radius: 8px; cursor: pointer;" onclick="openLightbox(\'${data.file_attachment}\')">';
content = content.replace(old_image_code, new_image_code)

# Write the updated content
with open('templates/chat.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Lightbox feature added successfully!")
print("Features added:")
print("  - CSS styling for fullscreen lightbox")
print("  - HTML modal structure")
print("  - JavaScript functions (openLightbox, closeLightbox)")
print("  - Images are now clickable to open in fullscreen")
print("  - X button to close lightbox")
print("  - ESC key support to close lightbox")
