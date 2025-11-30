import re
import sys
import os
import subprocess
from datetime import datetime

# --- Configuration ---
# The target directory for the generated HTML file.
HTML_TARGET_DIR = "/Users/gckanter/Library/Mobile Documents/com~apple~CloudDocs/Documents/Automation/Git/gckanter.github.io"
# Format for the date-published field (e.g., 2025-11-12T12:24)
DATE_FORMAT = "%Y-%m-%dT%H:%M" 

def update_frontmatter(key, value, frontmatter_lines, adjacent_key=None):
    """
    Updates a key's value in the frontmatter lines. If the key doesn't exist,
    it is added. If adjacent_key is provided and found, the new key is placed 
    immediately after the adjacent_key, otherwise it is appended to the end.
    """
    is_updated = False
    
    # 1. Try to find and update existing key
    for i, line in enumerate(frontmatter_lines):
        # Match lines that start with the key (case-insensitive)
        if re.match(r'^\s*' + re.escape(key) + r':\s*', line, re.IGNORECASE):
            # Update the line with the new value
            frontmatter_lines[i] = f'{key}: {value}'
            is_updated = True
            break
            
    # 2. If key not found, add it
    if not is_updated:
        new_line = f'{key}: {value}'
        
        if adjacent_key:
            adjacent_index = -1
            # Find the index of the adjacent key
            for i, line in enumerate(frontmatter_lines):
                if re.match(r'^\s*' + re.escape(adjacent_key) + r':\s*', line, re.IGNORECASE):
                    adjacent_index = i
                    break
            
            if adjacent_index != -1:
                # Insert the new line immediately after the adjacent key
                frontmatter_lines.insert(adjacent_index + 1, new_line)
                return # Insertion successful, exit function
        
        # If adjacent_key was not provided, or if the adjacent_key was not found, 
        # append the new key/value pair to the end.
        frontmatter_lines.append(new_line)        

def extract_title_and_parse_file(md_filepath):
    """
    Reads the file, separates content, extracts the title, and updates frontmatter.
    Returns: (page_title, frontmatter_lines_new, content_to_publish_lines) or (None, None, None) on error.
    """
    try:
        with open(md_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except IOError as e:
        print(f"Error reading file: {e}")
        return None, None, None

    lines = content.splitlines()

    # Find frontmatter indices
    frontmatter_start_index = -1
    frontmatter_end_index = -1
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if frontmatter_start_index == -1:
                frontmatter_start_index = i
            elif frontmatter_end_index == -1 and frontmatter_start_index != -1:
                frontmatter_end_index = i
                break

    if frontmatter_start_index == -1 or frontmatter_end_index == -1:
        print("Error: Could not find valid YAML frontmatter ('---' required at start and end).")
        return None, None, None
        
    # Exclude the '---' lines themselves
    frontmatter_lines = lines[frontmatter_start_index + 1: frontmatter_end_index]
    body_lines_full = lines[frontmatter_end_index + 1:]
    
    
    # --- 1. Extract Title from 'aliases' field ---
    page_title = None
    
    for i, line in enumerate(frontmatter_lines):
        if line.strip().lower().startswith('aliases:'):
            # Look for inline list (aliases: [Title 1, Title 2])
            match = re.match(r'^\s*aliases:\s*\[\s*(.*?)\s*\]', line, re.IGNORECASE)
            if match:
                first_alias = match.group(1).split(',')[0].strip()
                page_title = first_alias.strip('"\'')
                break
            
            # Look for multi-line list format starting on the next line (aliases:\n  - Title 1)
            for j in range(i + 1, len(frontmatter_lines)):
                list_item_match = re.match(r'^\s*-\s*(.+)$', frontmatter_lines[j])
                if list_item_match:
                    page_title = list_item_match.group(1).strip().strip('"\'')
                    break
            if page_title:
                break
                
    if not page_title:
        # Fallback to filename if title cannot be extracted
        page_title = os.path.splitext(os.path.basename(md_filepath))[0]
        print(f"Warning: Could not extract title from 'aliases'. Falling back to filename: '{page_title}'")


    # --- 2. Prepare Frontmatter Updates ---
    
    now_string = datetime.now().strftime(DATE_FORMAT)
    
    update_frontmatter('status', 'published', frontmatter_lines)
    update_frontmatter('date-published', now_string, frontmatter_lines, 'date-created')
    update_frontmatter('obsidianUIMode', 'preview', frontmatter_lines)

    # --- 3. Filter Body Content for Publishing ---
    
    content_to_publish_lines = []
    
    for line in body_lines_full:
        # Filter out lines containing « or » (Requirement 3)
        if '«' in line or '»' in line:
            continue
        
        # Also remove the Obsidian `!createdate` call lines
        if re.match(r'^\s*>\s*\[\!createdate\]', line):
            print("deleting" + line);
            continue
            
        # Also remove the Obsidian title header line
        if re.match(r'^\s*#\s*`=', line):
            print("deleting" + line);
            continue
            
        content_to_publish_lines.append(line)


    return page_title, frontmatter_lines, content_to_publish_lines, body_lines_full

def run_pandoc_conversion(md_content):
    """
    Executes pandoc to convert Markdown content to HTML fragments.
    """
    try:
        # Command: pandoc -f markdown -t html --metadata title="DOC_TITLE" --no-wrap
        # Use HTML fragment generation for body content only
        result = subprocess.run(
            ['pandoc', '-f', 'markdown', '-t', 'html', '--wrap=none'],
            input=md_content.encode('utf-8'),
            capture_output=True,
            check=True
        )
        return result.stdout.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Pandoc error: Could not convert Markdown to HTML.")
        print(f"   Stderr: {e.stderr.decode('utf-8').strip()}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: Pandoc is not installed or not found in your system's PATH.")
        print("Please install Pandoc (https://pandoc.org/install.html) to use this script.")
        sys.exit(1)


def generate_html_content(page_title, md_lines, md_filepath):
    """Generates the final HTML string using Pandoc."""
    
    # 1. Prepare Markdown content for Pandoc
    md_content = '\n'.join(md_lines)
    
    # 2. Run Pandoc conversion
    html_body_fragment = run_pandoc_conversion(md_content)

    # 3. Custom Insertion: Add the extracted title as the first H1 element inside the body
    custom_h1 = f'<h1>{page_title}</h1>'
    
    # The final HTML body content combines the custom H1 with the Pandoc output.
    body_html = f"""
    {custom_h1}
    {html_body_fragment}
    """

    html_filename = os.path.splitext(os.path.basename(md_filepath))[0] + ".html"
    
    # Use Tailwind for basic aesthetics and responsiveness
    html_template = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{page_title}</title>
            <!-- Favicon link referencing the local SVG file -->
            <link rel="icon" type="image/svg+xml" href="favicon.svg">
            <!-- Load Tailwind CSS via CDN -->
            <script src="https://cdn.tailwindcss.com"></script>
            <!-- Configure Tailwind to use 'class' for dark mode and the new accent color -->
    		<script>
    	        tailwind.config = {{
    	            darkMode: 'class', // MUST be 'class' for your JS logic to work
    	            theme: {{
    	                extend: {{
    	                    colors: {{
    	                        // Define your custom accent color
    	                        accent: '#4B6587', // Adjust if your color is different
    	                    }},
    	                    fontFamily: {{
    	                        // Ensure 'Inter' is available globally
    	                        inter: ['Inter', 'sans-serif'],
    	                    }}
    	                }}
    	            }}
    	        }}
    	    </script>
        	<script src="navbar.js" defer></script>
            <script src="theme.js"></script>
        	<link rel="stylesheet" href="style.css">
        </head>
        <body class="antialiased min-h-screen">
            <!-- Header & Navigation -->
        	<div data-include="navbar.html"></div>
            <!-- Main Content Area -->
            <main>
    {body_html}
            </main>
    </body>
    </html>"""
    
    return html_template, html_filename

def main_process():
    if len(sys.argv) < 2:
        print("Usage: python publishing_automation.py <path_to_markdown_file>")
        sys.exit(1)

    md_filepath = sys.argv[1]
    
    # Ensure absolute path is used
    if not os.path.isabs(md_filepath):
        md_filepath = os.path.join(os.getcwd(), md_filepath)
        
    page_title, frontmatter_lines_new, content_to_publish_lines, original_content_lines = extract_title_and_parse_file(md_filepath)
    
    if not page_title:
        sys.exit(1) # Exit if parsing failed

    # --- Step 3: Write Updated Markdown File (Frontmatter changes only) ---
    
    # Reconstruct the Markdown file with updated frontmatter
    updated_md_lines = (
        ['---'] + 
        frontmatter_lines_new + 
        ['---'] + 
        original_content_lines
    )
    
    try:
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_md_lines))
        print(f"\n✅ Successfully updated original Markdown file:")
        print(f"  -> {md_filepath} (Status set to 'Published', date/UIMode updated)")
    except IOError as e:
        print(f"❌ Error updating original Markdown file: {e}")
        sys.exit(1)


    # --- Step 4: Generate and Write HTML File ---
    
    html_template, html_filename = generate_html_content(page_title, content_to_publish_lines, md_filepath)
    html_target_path = os.path.join(HTML_TARGET_DIR, html_filename)

    try:
        os.makedirs(HTML_TARGET_DIR, exist_ok=True)
        with open(html_target_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        print(f"\n✅ Successfully generated HTML file:")
        print(f"  -> Path: {html_target_path}")
        print(f"  -> Page Title: '{page_title}'")
    except IOError as e:
        print(f"❌ Error writing HTML file to target directory: {e}. Check directory permissions.")
        sys.exit(1)

# Ensure the main function is called only when the script is executed directly
if __name__ == "__main__":
    main_process()