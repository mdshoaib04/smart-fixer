#!/usr/bin/env python3
"""
Clean up duplicate CSS rules
"""

def clean_css():
    with open('templates/profile.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove duplicate CSS rules
    lines = content.split('\n')
    cleaned_lines = []
    seen_rules = set()
    
    for line in lines:
        rule_key = line.strip()
        if 'overflow-x: hidden' in rule_key:
            if 'overflow-x: hidden' in seen_rules:
                continue
            seen_rules.add('overflow-x: hidden')
        elif 'min-height: 100vh' in rule_key:
            if 'min-height: 100vh' in seen_rules:
                continue
            seen_rules.add('min-height: 100vh')
        elif 'overflow-y: auto' in rule_key:
            if 'overflow-y: auto' in seen_rules:
                continue
            seen_rules.add('overflow-y: auto')
        
        cleaned_lines.append(line)
    
    # Write cleaned content
    with open('templates/profile.html', 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    print("✅ Duplicate CSS rules removed")

if __name__ == '__main__':
    clean_css()