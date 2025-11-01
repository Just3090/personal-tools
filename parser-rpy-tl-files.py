import sys

def parse_source_file(filepath):
    """
    Reads the source file (file1) and extracts all translations
    into a dictionary. The structure is:
    {tag: (original_english_line, translation_line)}
    """
    translations = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: The source file '{filepath}' was not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading '{filepath}': {e}")
        sys.exit(1)

    current_tag = None
    original_text_line = None

    for line in lines:
        stripped_line = line.strip()

        if "translate spanish" in line and "strings" not in line and stripped_line.endswith(":"):
            current_tag = stripped_line.split()[-1].strip(":")
            original_text_line = None
        elif current_tag:
            if stripped_line.startswith("#") and not original_text_line:
                original_text_line = stripped_line
            elif not stripped_line.startswith("#") and stripped_line != "" and original_text_line:
                translations[current_tag] = (original_text_line, line.rstrip())
                current_tag = None
                original_text_line = None

    return translations

def patch_target_file(filepath, translations):
    """
    Reads the target file (file2) and replaces empty translation lines
    if the tag and original text match.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: The target file '{filepath}' was not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading '{filepath}': {e}")
        sys.exit(1)

    output_lines = []
    current_tag = None
    original_text_in_target = None

    for line in lines:
        stripped_line = line.strip()

        if "translate spanish" in line and "strings" not in line and stripped_line.endswith(":"):
            current_tag = stripped_line.split()[-1].strip(":")
            original_text_in_target = None
            output_lines.append(line)
        elif current_tag:
            if stripped_line.startswith("#") and not original_text_in_target:
                original_text_in_target = stripped_line
                output_lines.append(line)
            elif not stripped_line.startswith("#") and stripped_line != "" and not stripped_line.startswith("old ") and not stripped_line.startswith("new "):
                is_empty_translation = stripped_line == '""' or stripped_line.endswith(' ""')

                can_replace = (
                    is_empty_translation and
                    current_tag in translations and
                    original_text_in_target and
                    translations[current_tag][0] == original_text_in_target
                )

                if can_replace:
                    _, translated_line = translations[current_tag]
                    indentation = line[:line.find(stripped_line)]
                    new_line = f"{indentation}{translated_line.strip()}\n"
                    output_lines.append(new_line)
                else:
                    output_lines.append(line)

                current_tag = None
                original_text_in_target = None
            else:
                output_lines.append(line)
        else:
            output_lines.append(line)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
    except Exception as e:
        print(f"Error writing to '{filepath}': {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("How to use: python parser-rpy-tl-files.py <base_file> <base_file_output>")
        print("Example: python3 main.py file1.rpy file2.rpy")
        sys.exit(1)
        
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    
    print(f"Starting the patch process...")
    print(f"             Base File:       {file1_path}")
    print(f"  Output Rewrited File:       {file2_path}")
    
    translations = parse_source_file(file1_path)
    
    if not translations:
        print("No valid files in the file1. Exiting...")
        sys.exit(0)
        
    print(f"Found {len(translations)} translations in '{file1_path}'.")
    
    patch_target_file(file2_path, translations)
    
    print(f"Nice! The file '{file2_path}' has been updated.")

if __name__ == "__main__":
    main()
