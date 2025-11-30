import os
import glob
import json
import re
from bs4 import BeautifulSoup

# --- Configuration ---
CONFIG_FILE = 'class_map.json'
SEARCH_ROOT = '..' # Parent directory
OUTPUT_SUFFIX = '_modified'
EXCLUDE_DIRS = ['__pycache__', '.git', 'node_modules', 'venv', '.venv'] # Common exclusions
# ---------------------

def load_class_map(config_path):
    """Loads the element-to-class mapping from the JSON configuration file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        print("Please create a class_map.json file with your desired class mappings.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{config_path}'. Please check the syntax.")
        return None

def parse_selector(selector):
    """
    Parses a CSS-like selector string and returns a dict with:
    - tag: the HTML tag name (or None for universal)
    - id: the element ID (or None)
    - classes: list of class names (or empty list)
    
    Supports formats like:
    - 'div' (just tag)
    - '#my-id' (just ID)
    - '.my-class' (just class)
    - 'div#my-id' (tag + ID)
    - 'div.my-class' (tag + class)
    - 'div.class1.class2' (tag + multiple classes)
    - 'div#my-id.my-class' (tag + ID + class)
    """
    result = {
        'tag': None,
        'id': None,
        'classes': []
    }
    
    # Extract ID (matches #identifier)
    id_match = re.search(r'#([\w-]+)', selector)
    if id_match:
        result['id'] = id_match.group(1)
        selector = selector.replace(id_match.group(0), '')
    
    # Extract classes (matches .classname)
    class_matches = re.findall(r'\.([\w-]+)', selector)
    if class_matches:
        result['classes'] = class_matches
        for match in class_matches:
            selector = selector.replace(f'.{match}', '', 1)
    
    # What remains should be the tag name (if any)
    selector = selector.strip()
    if selector and not selector.startswith('#') and not selector.startswith('.'):
        result['tag'] = selector
    
    return result

def element_matches_selector(element, selector_info):
    """
    Checks if a BeautifulSoup element matches the parsed selector criteria.
    """
    # Check tag name
    if selector_info['tag'] and element.name != selector_info['tag']:
        return False
    
    # Check ID
    if selector_info['id']:
        element_id = element.get('id')
        if element_id != selector_info['id']:
            return False
    
    # Check classes
    if selector_info['classes']:
        element_classes = element.get('class', [])
        for required_class in selector_info['classes']:
            if required_class not in element_classes:
                return False
    
    return True

def find_matching_elements(soup, selector):
    """
    Finds all elements in the soup that match the given selector.
    Supports simple selectors and descendant selectors (space-separated).
    
    Examples:
    - 'div' - all div elements
    - 'div#carousel' - div with id="carousel"
    - 'div.carousel-item' - div with class="carousel-item"
    - 'div.class1.class2' - div with both classes
    - 'div img' - img elements that are descendants of div elements
    """
    # Check if this is a descendant selector (contains space)
    if ' ' in selector.strip():
        parts = selector.strip().split()
        
        # Start with all elements matching the first selector
        parent_selector = parts[0]
        parent_info = parse_selector(parent_selector)
        
        # Find all parent elements
        parents = []
        for element in soup.find_all():
            if element_matches_selector(element, parent_info):
                parents.append(element)
        
        # For each subsequent selector part, find descendants
        current_elements = parents
        for part in parts[1:]:
            child_info = parse_selector(part)
            next_elements = []
            
            for parent in current_elements:
                for descendant in parent.find_all():
                    if element_matches_selector(descendant, child_info) and descendant not in next_elements:
                        next_elements.append(descendant)
            
            current_elements = next_elements
        
        return current_elements
    else:
        # Simple selector (no descendants)
        selector_info = parse_selector(selector)
        matching_elements = []
        
        for element in soup.find_all():
            if element_matches_selector(element, selector_info):
                matching_elements.append(element)
        
        return matching_elements

def apply_classes_to_html(html_content, class_map):
    """Parses HTML content and applies classes based on the provided map."""
    soup = BeautifulSoup(html_content, 'html.parser')
    modified_count = 0

    # Iterate over the mapping: { 'selector': ['class-a', 'class-b', ...] }
    for selector, classes_to_add in class_map.items():
        if not classes_to_add:
            continue

        # Find all elements matching the selector
        matching_elements = find_matching_elements(soup, selector)
        
        for element in matching_elements:
            # 1. Get existing classes
            existing_classes = element.get('class', [])
            
            # 2. Convert existing_classes list to a set for easy addition and deduplication
            class_set = set(existing_classes)

            # 3. Add the new classes, ignoring duplicates
            for cls in classes_to_add:
                class_set.add(cls)

            # 4. Update the element's class attribute
            element['class'] = sorted(list(class_set))  # Sort for consistency
            modified_count += 1
        
        if matching_elements:
            print(f"   ✓ '{selector}' matched {len(matching_elements)} element(s)")
            
    print(f" -> Applied classes to {modified_count} total element(s).")
    # Return the nicely formatted HTML string
    return soup.prettify()

def find_html_files(root_dir, exclude_dirs=None):
    """
    Recursively finds all HTML files starting from root_dir,
    excluding the script's own directory and other specified directories.
    """
    if exclude_dirs is None:
        exclude_dirs = []
    
    # Get the absolute path of the script's directory to exclude it
    script_dir = os.path.abspath(os.path.dirname(__file__))
    
    html_files = []
    root_abs = os.path.abspath(root_dir)
    
    for dirpath, dirnames, filenames in os.walk(root_abs):
        # Get absolute path of current directory
        current_dir_abs = os.path.abspath(dirpath)
        
        # Skip the script's directory
        if current_dir_abs == script_dir:
            print(f" -> Skipping script directory: {dirpath}")
            dirnames[:] = []  # Don't recurse into subdirectories
            continue
        
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        # Find HTML files in current directory
        for filename in filenames:
            if filename.endswith('.html') and OUTPUT_SUFFIX not in filename:
                html_files.append(os.path.join(dirpath, filename))
    
    return html_files

def process_files():
    """Main function to iterate through files and apply changes."""
    
    class_map = load_class_map(CONFIG_FILE)
    if class_map is None:
        return

    print(f"Starting class injection using config from: {CONFIG_FILE}")
    print(f"Searching for HTML files in: {os.path.abspath(SEARCH_ROOT)}")
    print(f"Excluding directories: {', '.join(EXCLUDE_DIRS)}")
    print(f"Excluding script directory: {os.path.abspath(os.path.dirname(__file__))}\n")
    
    # Find all HTML files recursively
    html_files = find_html_files(SEARCH_ROOT, EXCLUDE_DIRS)
    
    if not html_files:
        print("No HTML files found matching the criteria. Aborting.")
        return
    
    print(f"Found {len(html_files)} HTML file(s) to process:\n")
    for f in html_files:
        print(f"  - {f}")
    print()

    for filepath in html_files:
        print(f"\nProcessing file: {filepath}")
        
        # Skip the output files created in previous runs
        if OUTPUT_SUFFIX in filepath:
            print(" -> Skipping previously modified output file.")
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            modified_content = apply_classes_to_html(content, class_map)
            
            # Determine the output filename
            name, ext = os.path.splitext(filepath)
            output_filepath = f"{name}{OUTPUT_SUFFIX}{ext}"
            
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(modified_content)
                
            print(f" -> Successfully saved modified file to: {output_filepath}")

        except Exception as e:
            print(f" -> An error occurred while processing {filepath}: {e}")
            
    print("\nProcessing complete.")

if __name__ == '__main__':
    process_files()
