import json
import sys
import os
from pathlib import Path

# Platform-specific keyboard input handling
try:
    import tty
    import termios
    
    def get_key():
        """Get a single keypress on Unix/Linux/Mac"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
            # Handle arrow keys (escape sequences)
            if key == '\x1b':
                next_chars = sys.stdin.read(2)
                if next_chars == '[C':  # Right arrow
                    return 'right'
                elif next_chars == '[D':  # Left arrow
                    return 'left'
            return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    UNIX_LIKE = True
except ImportError:
    # Windows fallback
    import msvcrt
    
    def get_key():
        """Get a single keypress on Windows"""
        key = msvcrt.getch()
        if key == b'\xe0':  # Arrow key prefix on Windows
            key = msvcrt.getch()
            if key == b'M':  # Right arrow
                return 'right'
            elif key == b'K':  # Left arrow
                return 'left'
        return key.decode('utf-8', errors='ignore')
    
    UNIX_LIKE = False


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if UNIX_LIKE else 'cls')


def display_match(title, title_desc, match, match_index, total_matches):
    """Display a title and one of its matches side by side"""
    clear_screen()
    
    # Terminal width
    try:
        term_width = os.get_terminal_size().columns
    except:
        term_width = 80
    
    column_width = min(term_width // 2 - 2, 60)
    
    print("=" * term_width)
    print(f" MATCH VALIDATION ({match_index + 1}/{total_matches})".center(term_width))
    print("=" * term_width)
    print()
    
    # Format title section
    title_lines = wrap_text(f"TITLE: {title}", column_width)
    title_desc_lines = wrap_text(f"\n{title_desc}", column_width)
    
    # Format match section
    match_lines = wrap_text(f"DEVELOPMENT AREA: {match['development area']}", column_width)
    match_desc_lines = wrap_text(f"\n{match['description']}", column_width)
    
    # Combine all lines
    left_lines = title_lines + title_desc_lines
    right_lines = match_lines + match_desc_lines
    
    # Pad to same length
    max_lines = max(len(left_lines), len(right_lines))
    left_lines += [''] * (max_lines - len(left_lines))
    right_lines += [''] * (max_lines - len(right_lines))
    
    # Print side by side
    for left, right in zip(left_lines, right_lines):
        left_padded = left.ljust(column_width)
        print(f"{left_padded}  │  {right}")
    
    print()
    print("─" * term_width)
    print()
    print("Is this a good match?")
    print("  [Y] Yes / ← Left Arrow    |    [N] No / → Right Arrow    |    [Q] Quit")
    print()


def wrap_text(text, width):
    """Simple word wrapping"""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + len(current_line) <= width:
            current_line.append(word)
            current_length += len(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines if lines else ['']


def load_data(input_path):
    """Load JSON data from file"""
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_results(output_path, data):
    """Save validated data to output file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_output_path(input_path):
    """Generate output filename"""
    path = Path(input_path)
    stem = path.stem
    suffix = path.suffix
    return path.parent / f"{stem}_validated{suffix}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_matches.py <input_json_file>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found")
        sys.exit(1)
    
    # Load data
    try:
        all_data = load_data(input_path)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file - {e}")
        sys.exit(1)
   
    
    output_data = []
    for data in all_data:
        # Add validation field to each match
        if 'matches' in data:
            for match in data['matches']:
                if 'validated' not in match:
                    match['validated'] = None
        
        title = data.get('title', 'Untitled')
        description = data.get('description', 'No description')
        matches = data.get('matches', [])
        
        if not matches:
            print("No matches found in the data")
            sys.exit(0)
        
        # Process each match
        current_index = 0
        
        # Skip already validated matches
        while current_index < len(matches) and matches[current_index].get('validated') is not None:
            current_index += 1
        
        while current_index < len(matches):
            match = matches[current_index]
            display_match(title, description, match, current_index, len(matches))
            
            # Get user input
            key = get_key().lower()
            
            if key in ['y', 'left']:
                match['validated'] = True
                current_index += 1
            elif key in ['n', 'right']:
                match['validated'] = False
                current_index += 1
            elif key in ['q', '\x03']:  # q or Ctrl+C
                print("\nSaving progress and exiting...")
                break
            # Ignore other keys, wait for valid input

        output_data.append(data)
        
    # Save results
    output_path = get_output_path(input_path)
    save_results(output_path, output_data)
    
    clear_screen()
    print("=" * 60)
    print(" VALIDATION COMPLETE".center(60))
    print("=" * 60)
    print()
    print(f"Results saved to: {output_path}")
    print()
    
    # Summary
    validated_count = sum(1 for m in matches if m.get('validated') is True)
    rejected_count = sum(1 for m in matches if m.get('validated') is False)
    pending_count = sum(1 for m in matches if m.get('validated') is None)
    
    print(f"Validated as good match: {validated_count}")
    print(f"Validated as poor match: {rejected_count}")
    print(f"Pending validation:      {pending_count}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Progress saved.")
        sys.exit(0)
