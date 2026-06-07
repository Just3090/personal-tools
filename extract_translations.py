#!/usr/bin/env python3
import os
import re
import argparse

def parse_rpy_file(file_path, extract_dialogue=True, extract_strings=True):
    """
    Parses a single .rpy file to extract translation pairs.
    Returns a list of tuples: (original_text, translated_text)
    """
    results = []
    
    current_state = None  # 'dialogue', 'strings', or None
    current_english = None
    current_old = None
    
    dialogue_pattern = re.compile(r'^[a-zA-Z0-9_\s]*["\'].*["\']$')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line_raw = line.rstrip('\r\n')
                stripped = line_raw.strip()
                
                if not stripped:
                    continue
                
                has_indent = line_raw.startswith(' ') or line_raw.startswith('\t')
                
                if not has_indent:
                    current_state = None
                    current_english = None
                    current_old = None
                    
                    if stripped.startswith('translate spanish strings:'):
                        current_state = 'strings'
                    elif stripped.startswith('translate spanish ') and stripped.endswith(':'):
                        current_state = 'dialogue'
                    continue
                
                if current_state == 'dialogue' and extract_dialogue:
                    if stripped.startswith('#'):
                        comment_content = stripped[1:].strip()
                        if dialogue_pattern.match(comment_content):
                            current_english = comment_content
                    else:
                        if dialogue_pattern.match(stripped):
                            if current_english is not None:
                                results.append((current_english, stripped))
                                current_english = None
                                
                elif current_state == 'strings' and extract_strings:
                    if stripped.startswith('old '):
                        old_val = stripped[4:].strip()
                        current_old = old_val
                    elif stripped.startswith('new '):
                        new_val = stripped[4:].strip()
                        if current_old is not None:
                            results.append((current_old, new_val))
                            current_old = None
                            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        
    return results

def main():
    parser = argparse.ArgumentParser(
        description="Extract English-Spanish translation pairs from Ren'Py (.rpy) files."
    )
    parser.add_argument(
        "input_path",
        help="Path to the .rpy file or directory containing .rpy files."
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to the output file (if input is a file) or output directory (if input is a directory). "
             "Defaults to generating a file next to the input with '_extracted.txt' suffix."
    )
    parser.add_argument(
        "-t", "--type",
        choices=["all", "dialogue", "strings"],
        default="all",
        help="Type of translations to extract (default: all)."
    )
    
    args = parser.parse_args()
    
    extract_dialogue = args.type in ("all", "dialogue")
    extract_strings = args.type in ("all", "strings")
    
    input_path = args.input_path
    if not os.path.exists(input_path):
        print(f"Error: Input path '{input_path}' does not exist.")
        return
        
    if os.path.isfile(input_path):
        # Determine output file path
        if args.output:
            output_file = args.output
        else:
            base, _ = os.path.splitext(input_path)
            output_file = f"{base}_extracted.txt"
            
        print(f"Processing file: {input_path}")
        pairs = parse_rpy_file(input_path, extract_dialogue, extract_strings)
        
        if not pairs:
            print("No translation pairs found.")
            return
            
        try:
            with open(output_file, 'w', encoding='utf-8') as out:
                for idx, (eng, esp) in enumerate(pairs):
                    out.write(f"{eng}\n")
                    out.write(f"{esp}\n")
                    if idx < len(pairs) - 1:
                        out.write("\n")
            print(f"Successfully extracted {len(pairs)} pairs to: {output_file}")
        except Exception as e:
            print(f"Error writing to output file {output_file}: {e}")
            
    elif os.path.isdir(input_path):
        rpy_files = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.endswith('.rpy')
        ]
        
        if not rpy_files:
            print(f"No .rpy files found in directory: {input_path}")
            return
            
        print(f"Found {len(rpy_files)} .rpy file(s) in directory: {input_path}")
        
        if args.output:
            out_dir = args.output
            os.makedirs(out_dir, exist_ok=True)
        else:
            out_dir = input_path
            
        total_extracted = 0
        for rpy_file in sorted(rpy_files):
            pairs = parse_rpy_file(rpy_file, extract_dialogue, extract_strings)
            if not pairs:
                continue
                
            base_name = os.path.basename(rpy_file)
            name_no_ext, _ = os.path.splitext(base_name)
            output_file = os.path.join(out_dir, f"{name_no_ext}_extracted.txt")
            
            try:
                with open(output_file, 'w', encoding='utf-8') as out:
                    for idx, (eng, esp) in enumerate(pairs):
                        out.write(f"{eng}\n")
                        out.write(f"{esp}\n")
                        if idx < len(pairs) - 1:
                            out.write("\n")
                print(f"  - Extracted {len(pairs)} pairs from '{base_name}' to '{os.path.basename(output_file)}'")
                total_extracted += len(pairs)
            except Exception as e:
                print(f"Error writing to output file {output_file}: {e}")
                
        print(f"Finished directory processing. Total extracted pairs across all files: {total_extracted}")

if __name__ == "__main__":
    main()
