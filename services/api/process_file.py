import os
import pathlib
import hashlib
import sys
from typing import List, Set

# --- Configuration: Define supported extensions using a set ---
# This set should contain all extensions in lowercase, without leading dots.
# Populate this with your "Tier 1", "Tier 2", etc. extensions.
SUPPORTED_EXTENSIONS: Set[str] = {
    "pdf", "docx", "doc", "rtf", "odt", "txt", "md",
    "pptx", "ppt", "xlsx", "xls", "csv", "py", "sql",
    "js", "ts", "cs", "java", "go", "sh", "ps1",
    "json", "xml", "yaml", "yml", "toml", "html", "htm",
    "eml", "msg", "vtt", "srt"
}

# --- Utility Function: Recursive File Discovery (as discussed previously) ---
def get_all_files_recursive(root_folder_path: pathlib.Path) -> List[pathlib.Path]:
    """
    Recursively gets all file paths in a given root folder.
    Returns a list of pathlib.Path objects.
    """
    file_paths = []
    # Use rglob('*') to get all files and directories recursively
    # Then filter for only files using .is_file()
    for p in root_folder_path.rglob('*'):
        if p.is_file():
            file_paths.append(p)
    return file_paths


# --- Main Processing Logic ---
def main():
    if len(sys.argv) < 2:
        raw_input_path = input("File or Folder Path: ")
    else:
        raw_input_path = sys.argv[1]    

    # Use pathlib to correctly handle paths regardless of OS
    input_path = pathlib.Path(raw_input_path)

    # Validate path existence
    if not input_path.exists():
        print(f"\033[91mError: Path not found at: '{input_path}'\033[0m")
        return

    files_to_process: List[pathlib.Path] = []

    # Determine if input is a file, folder, or something else
    if input_path.is_file():
        # Input is a single file
        file_extension = input_path.suffix.lstrip('.').lower() # Get extension, remove dot, lowercase

        if file_extension in SUPPORTED_EXTENSIONS:
            print(f"Processing single file: '{input_path}' (Type: '{file_extension}')")
            files_to_process.append(input_path)
        else:
            print(f"\033[91mError: File type '{file_extension}' not supported for single file processing.\033[0m")
            return

    elif input_path.is_dir():
        # Input is a folder, so we'll walk it recursively
        print(f"Processing folder recursively: '{input_path}'")
        all_found_files = get_all_files_recursive(input_path)
        
        # Filter files from the folder based on supported extensions
        for found_file in all_found_files:
            file_extension = found_file.suffix.lstrip('.').lower()
            if file_extension in SUPPORTED_EXTENSIONS:
                files_to_process.append(found_file)
            else:
                # Optionally, print a message for ignored files in folders
                #print(f"  Skipping: '{found_file}' (Type: '{file_extension}' not supported)")
                pass # Silently skip unsupported types in folders

        if not files_to_process:
            print(f"\033[93mWarning: No supported files found in folder '{input_path}'.\033[0m")
            return

    else:
        # Input is neither a file nor a directory (e.g., a broken symlink, device)
        print(f"\033[91mError: Input path '{input_path}' is not a file or a directory.\033[0m")
        return

    # --- Process the collected files ---
    print(f"\n--- Hashing {len(files_to_process)} Supported Files ---")
    for current_file_path in files_to_process:
        try:
            with open(current_file_path, mode='rb') as f: # Use 'rb' for binary read
                hashed_content = hashlib.file_digest(f, "sha256").hexdigest() # Get hex string
                print(f"File: '{current_file_path}'\n  Hash: {hashed_content}\n")
        except IOError as e:
            print(f"\033[91mError processing '{current_file_path}': {e}\033[0m")
        except Exception as e:
            print(f"\033[91mAn unexpected error occurred with '{current_file_path}': {e}\033[0m")


if __name__ == "__main__":
    main()