#!/usr/bin/env python3
"""
Script to fix SVG icon visibility in chat buttons
"""

# Read the file
with open('templates/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

# CSS to make SVG icons visible
svg_fix_css = """
        .attach-btn svg, .code-btn svg, .send-btn svg {
            stroke: currentColor;
            fill: none;
        }
        """

# Find the button CSS section and add SVG styling after it
old_button_css = """        .attach-btn, .code-btn, .send-btn {
            background: none;
            border: none;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 50%;
            transition: background-color 0.2s;
            color: var(--text-color);
        }
        """

new_button_css = old_button_css + svg_fix_css

content = content.replace(old_button_css, new_button_css)

# Write the updated content
with open('templates/chat.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: SVG icon visibility fixed!")
print("Added CSS rule to make SVG icons visible in buttons")
