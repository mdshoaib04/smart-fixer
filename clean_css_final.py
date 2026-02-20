#!/usr/bin/env python3
"""
Clean up duplicate CSS rules
"""

def clean_css():
    with open('templates/profile.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    cleaned = []
    seen = set()
    
    for line in lines:
        if 'overflow-x: hidden' in line and 'overflow-x: hidden' in seen:
            continue
        if 'overflow-x: hidden' in line:
            seen.add('overflow-x: hidden')
        cleaned.append(line)
    
    with open('templates/profile.html', 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned))
    
    print('Cleaned CSS duplicates')

if __name__ == '__main__':
    clean_css()