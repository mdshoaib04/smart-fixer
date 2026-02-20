#!/usr/bin/env python3
"""
Remove duplicate post modal functions, keeping only the last one
"""

def remove_duplicates():
    with open('templates/profile.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by the function definition
    parts = content.split('function openPostModal(postId) {')
    
    if len(parts) > 2:
        # Keep first part + last function
        result = parts[0] + 'function openPostModal(postId) {' + parts[-1]
        with open('templates/profile.html', 'w', encoding='utf-8') as f:
            f.write(result)
        print("✅ Kept only last instance of post modal functions")
    else:
        print("✅ No duplicates found")

if __name__ == '__main__':
    remove_duplicates()