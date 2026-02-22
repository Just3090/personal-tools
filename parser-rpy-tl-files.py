import sys
import os

def parse_source_file(filepath, skip_tags=False):
    """
    Parses the source Ren'Py translation file to extract both dialogue blocks
    and user interface string translations.
    
    Args:
        filepath (str): The absolute or relative path to the source translation file.
        skip_tags (bool): Determines the extraction mapping strategy for dialogues.
        
    Returns:
        tuple: A dictionary containing dialogue translations and a dictionary 
               containing string translations.
    """
    translations_dialogue = {}
    translations_strings = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file_descriptor:
            lines = file_descriptor.readlines()
    except FileNotFoundError:
        print(f"Error: Target source file '{filepath}' could not be located.")
        sys.exit(1)
    except Exception as exception:
        print(f"Error: An unexpected I/O error occurred while reading '{filepath}': {exception}")
        sys.exit(1)

    current_block_type = None
    current_tag = None
    original_text_buffer = None
    current_old_string = None

    for line in lines:
        stripped_line = line.strip()

        # Identify the start and type of a translation block
        if stripped_line.startswith("translate ") and stripped_line.endswith(":"):
            if " strings:" in stripped_line:
                current_block_type = "strings"
            else:
                current_block_type = "dialogue"
                current_tag = stripped_line.split()[-1].strip(":")
                original_text_buffer = None
            continue

        if current_block_type == "dialogue" and current_tag:
            # Dialogue parsing logic (handles trailing attributes like 'nointeract')
            if stripped_line.startswith("#") and not original_text_buffer:
                original_text_buffer = stripped_line
            elif not stripped_line.startswith("#") and stripped_line != "" and original_text_buffer:
                if skip_tags:
                    translations_dialogue[original_text_buffer] = line.rstrip()
                else:
                    translations_dialogue[current_tag] = (original_text_buffer, line.rstrip())
                
                # Reset block state.
                current_tag = None
                original_text_buffer = None
                
        elif current_block_type == "strings":
            # Menu and UI strings parsing logic
            if stripped_line.startswith("old "):
                current_old_string = stripped_line
            elif stripped_line.startswith("new ") and current_old_string:
                translations_strings[current_old_string] = line.rstrip()
                current_old_string = None

    return translations_dialogue, translations_strings


def patch_target_file(filepath, translations_dialogue, translations_strings, skip_tags=False):
    """
    Applies extracted translations to a target Ren'Py file, supporting both
    standard dialogue tags and UI string blocks. Overwrites the target file in place.
    
    Args:
        filepath (str): Path to the target file to be patched.
        translations_dialogue (dict): The dictionary containing dialogue mappings.
        translations_strings (dict): The dictionary containing string mappings.
        skip_tags (bool): Determines the application mapping strategy for dialogues.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file_descriptor:
            lines = file_descriptor.readlines()
    except Exception as exception:
        print(f"Error reading target file '{filepath}': {exception}")
        sys.exit(1)

    output_lines = []
    current_block_type = None
    current_tag = None
    original_text_in_target = None
    current_old_string = None

    for line in lines:
        stripped_line = line.strip()

        if stripped_line.startswith("translate ") and stripped_line.endswith(":"):
            if " strings:" in stripped_line:
                current_block_type = "strings"
            else:
                current_block_type = "dialogue"
                current_tag = stripped_line.split()[-1].strip(":")
                original_text_in_target = None
            output_lines.append(line)
            continue

        if current_block_type == "dialogue" and current_tag:
            if stripped_line.startswith("#") and not original_text_in_target:
                original_text_in_target = stripped_line
                output_lines.append(line)
            elif not stripped_line.startswith("#") and stripped_line != "" and original_text_in_target:
                translated_line = None
                
                if skip_tags and original_text_in_target in translations_dialogue:
                    translated_line = translations_dialogue[original_text_in_target]
                elif not skip_tags and current_tag in translations_dialogue:
                    # Validate against the original text to prevent structural mismatches
                    stored_original, stored_translation = translations_dialogue[current_tag]
                    if stored_original == original_text_in_target:
                        translated_line = stored_translation

                if translated_line:
                    # Extract leading whitespace to maintain structural indentation
                    indentation = line[:len(line) - len(line.lstrip())]
                    output_lines.append(f"{indentation}{translated_line.lstrip()}\n")
                else:
                    output_lines.append(line)

                # Reset block state
                current_tag = None
                original_text_in_target = None
            else:
                output_lines.append(line)

        elif current_block_type == "strings":
            if stripped_line.startswith("old "):
                current_old_string = stripped_line
                output_lines.append(line)
            elif stripped_line.startswith("new ") and current_old_string:
                # Detect empty string translation blocks accurately
                is_empty_translation = stripped_line in ['new ""', "new ''"]
                
                if is_empty_translation and current_old_string in translations_strings:
                    translated_line = translations_strings[current_old_string]
                    indentation = line[:len(line) - len(line.lstrip())]
                    output_lines.append(f"{indentation}{translated_line.lstrip()}\n")
                else:
                    output_lines.append(line)
                
                current_old_string = None
            else:
                output_lines.append(line)
        else:
            output_lines.append(line)

    try:
        with open(filepath, 'w', encoding='utf-8') as file_descriptor:
            file_descriptor.writelines(output_lines)
    except Exception as exception:
        print(f"Error writing to '{filepath}': {exception}")
        sys.exit(1)


def main():
    """
    Main execution entry point for the translation patching routine.
    """
    args = [arg for arg in sys.argv[1:] if not arg.startswith('--')]
    flags = [arg for arg in sys.argv[1:] if arg.startswith('--')]

    if len(args) != 2:
        print("Usage: python parser-rpy-tl-files.py [--skip-tags] <base_file> <target_file>")
        print("Example: python3 main.py --skip-tags file1.rpy file2.rpy")
        sys.exit(1)

    base_file_path, target_file_path = args
    skip_tags = '--skip-tags' in flags
    
    mode = "by original text" if skip_tags else "by tag"
    print(f"Initializing patch procedure... (Execution Mode: {mode})")
    print(f"             Base File:       {base_file_path}")
    print(f"   Target File to Patch:      {target_file_path}")
    
    translations_dialogue, translations_strings = parse_source_file(base_file_path, skip_tags)
    
    total_translations = len(translations_dialogue) + len(translations_strings)
    if total_translations == 0:
        print("Warning: No valid translations were detected in the base file. Terminating process.")
        sys.exit(0)
        
    print(f"Successfully extracted {len(translations_dialogue)} dialogue blocks and {len(translations_strings)} string blocks.")
    
    patch_target_file(target_file_path, translations_dialogue, translations_strings, skip_tags)
    print("Patch process completed successfully.")


if __name__ == "__main__":
    main()
