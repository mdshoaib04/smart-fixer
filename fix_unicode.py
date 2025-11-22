# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace emoji characters with empty strings
replacements = {
    '\U0001f680 ': '',  # Rocket
    '\U0001f4e1 ': '',  # Satellite
    '\U0001f310 ': '',  # Globe
    '\U0001f517 ': '',  # Link
    '\U0001f4bb ': '',  # Laptop
    '\u2705 ': '',      # Check mark
    '\U0001f6d1 ': '',  # Stop sign
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully removed all emojis from app.py")
