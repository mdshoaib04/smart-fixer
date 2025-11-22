"""
Script to apply all chat fixes together
"""

# Read the file
with open('templates/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Change data.message to data.content
content = content.replace(
    "messageContent = data.message;",
    "messageContent = data.content || data.message || '';"
)

# Fix 2: Change data.file_path to data.file_url
content = content.replace(
    "file_attachment: data.file_path,",
    "file_attachment: data.file_url,"
)

# Write back
with open('templates/chat.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully applied all fixes!")
print("- Fixed message content field (data.content)")
print("- Fixed file upload field (data.file_url)")
