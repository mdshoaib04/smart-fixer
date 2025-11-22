"""
Script to add image lightbox functionality to chat.html
"""

# Read the file
with open('templates/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add lightbox modal HTML before </body>
lightbox_html = '''
    <!-- Image Lightbox Modal -->
    <div id="imageLightbox" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 2000; justify-content: center; align-items: center;" onclick="closeImageLightbox()">
        <img id="lightboxImage" src="" style="max-width: 90%; max-height: 90%; object-fit: contain;" onclick="event.stopPropagation()">
        <button onclick="closeImageLightbox()" style="position: absolute; top: 20px; right: 30px; background: none; border: none; color: white; font-size: 40px; cursor: pointer; z-index: 2001;">&times;</button>
    </div>
</body>'''

content = content.replace('</body>', lightbox_html)

# 2. Add lightbox JavaScript functions before </script>
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

# 3. Make images clickable - find and replace the image display line
old_image_line = '                    messageContent = `<img src="${data.file_attachment}" alt="Image" style="max-width: 300px; border-radius: 8px;">`'
new_image_line = '                    messageContent = `<img src="${data.file_attachment}" alt="Image" style="max-width: 300px; border-radius: 8px; cursor: pointer;" onclick="openImageLightbox(\'${data.file_attachment}\')">`'

content = content.replace(old_image_line, new_image_line)

# Write back
with open('templates/chat.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully added image lightbox functionality!")
print("- Added lightbox modal HTML")
print("- Added JavaScript functions")
print("- Made images clickable")
