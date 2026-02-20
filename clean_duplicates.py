#!/usr/bin/env python3
"""
Clean up duplicate functions in profile.html
"""

def clean_duplicates():
    with open('templates/profile.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove duplicate post modal functions (keep only the last one)
    lines = content.split('\n')
    cleaned_lines = []
    skip_until = None
    
    for i, line in enumerate(lines):
        if skip_until and i < skip_until:
            continue
            
        if 'function openPostModal(postId) {' in line:
            # Check if this is a duplicate by looking ahead
            is_duplicate = False
            for j in range(i+1, min(i+20, len(lines))):
                if 'function openPostModal(postId) {' in lines[j]:
                    is_duplicate = True
                    skip_until = j
                    break
            
            if not is_duplicate:
                cleaned_lines.append(line)
            else:
                # Skip this duplicate and find the end of the function
                for k in range(i, len(lines)):
                    if lines[k].strip() == '}' and 'function closePostModal() {' in ''.join(lines[max(0,k-10):k]):
                        skip_until = k + 1
                        break
        else:
            cleaned_lines.append(line)
    
    # Write cleaned content
    with open('templates/profile.html', 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    print("✅ Duplicate functions removed")

if __name__ == '__main__':
    clean_duplicates()