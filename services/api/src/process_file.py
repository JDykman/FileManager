import os
import pathlib
import hashlib
import sys
from typing import List, Set
from fastapi import FastAPI, HTTPException
import urllib.parse

app = FastAPI()

# --- Configuration: Define supported extensions using a set ---
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

@app.get("/")
def read_root():
    return {"message": "File Processing API is running."}

@app.get("/process-file/")
async def process_file(file_path: str):
    """
    Processes a single file specified by its absolute path.
    The file path must be URL-encoded and passed as a query parameter.

    Args:
        file_path (str): The URL-encoded absolute path to the file.

    Returns:
        dict: A message indicating the status of the file processing.

    Raises:
        HTTPException:
            - 400 Bad Request: If the file path is invalid, unsupported type,
              or points to a directory.
            - 404 Not Found: If the specified file does not exist.
    """
    # 1. Input Validation and Security
    # Decode the URL-encoded path. FastAPI often does this automatically for query parameters,
    # but explicit decoding ensures consistency and handles any edge cases.
    decoded_file_path = urllib.parse.unquote(file_path)

    # Convert the decoded string to a pathlib.Path object
    input_path = pathlib.Path(decoded_file_path)

    # Basic security check: Prevent directory traversal attempts.
    # This is crucial for paths received from users.
    # More sophisticated checks might involve a white-list of allowed base directories.
    if ".." in str(input_path.resolve()): # Resolve to get the absolute path without '..'
        raise HTTPException(
            status_code=400,
            detail="Invalid file path provided. Directory traversal detected."
        )

    # 2. Path Existence Check
    if not input_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Error: Path not found at: '{input_path}'"
        )

    # 3. Path Type Check (File vs. Directory)
    if input_path.is_file():
        file_extension = input_path.suffix.lstrip('.').lower() # Get extension, remove dot, lowercase

        if file_extension in SUPPORTED_EXTENSIONS:
            print(f"Processing single file: '{input_path}' (Type: '{file_extension}')")
            # --- Place your actual file processing logic here ---
            # Example: read file contents, perform some operation
            try:
                # This is just an example. Replace with your actual processing.
                with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Read a small part to confirm access, or process fully
                    content_preview = f.read(100)
                    print(f"File content preview: {content_preview}...")
                message = f"File '{input_path.name}' (type: '{file_extension}') processed successfully."
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing file '{input_path.name}': {e}"
                )
            # ---------------------------------------------------
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Error: File type '{file_extension}' not supported for single file processing. "
                       f"Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
            )

    elif input_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"'{input_path}' is a directory. Use the '/process-folder' endpoint for folders."
            # Or remove this if you only want to process files here.
        )
    else:
        # Input is neither a file nor a directory (e.g., a broken symlink, device)
        raise HTTPException(
            status_code=400,
            detail=f"Error: Input path '{input_path}' is not a valid file or directory type."
        )

    return {"message": message}
@app.get("/process-folder")
def process_folder(folder_path: str):
    input_path = pathlib.Path(folder_path)

    # Validate path existence
    if not input_path.exists():
        print(f"\033[91mError: Path not found at: '{input_path}'\033[0m")
        return

    files_to_process: pathlib.Path

    if input_path.is_file():
        print(f"'{input_path}': is not a file, use '/process-folder' endpoint for folders.")
        return {}
    elif input_path.is_dir():
        # Input is a folder, so we'll walk it recursively
        print(f"Processing folder: '{input_path}'")
        all_found_files = get_all_files_recursive(input_path)
        
        # Filter files from the folder based on supported extensions
        for found_file in all_found_files:
            file_extension = found_file.suffix.lstrip('.').lower()
            if file_extension in SUPPORTED_EXTENSIONS:
                files_to_process.append(found_file)
            else:
                print(f"  Skipping: '{found_file}' (Type: '{file_extension}' not supported)")
                pass # Skip unsupported types in folders
        for current_file_path in files_to_process:
            hash_file(current_file_path)
    else:
        # Input is neither a file nor a directory (e.g., a broken symlink, device)
        print(f"\033[91mError: Input path '{input_path}' is not a type.\033[0m")
        return
    return {"message": f"Processing folder at: {folder_path}"}

def hash_file(file_path:pathlib.Path) -> str:
    try:
        with open(file_path, mode='rb') as f: # Use 'rb' for binary read
            hashed_content = hashlib.file_digest(f, "sha256").hexdigest() # Get hex string
            print(f"File: '{file_path}'\n  Hash: {hashed_content}\n")
    except IOError as e:
        print(f"\033[91mError processing '{file_path}': {e}\033[0m")
    except Exception as e:
        print(f"\033[91mAn unexpected error occurred with '{file_path}': {e}\033[0m")

if __name__ == "__main__":
    import requests
    import os
    import time
    import urllib.parse

    # --- Timing for the entire script ---
    overall_start_time = time.monotonic()

    # Assume FastAPI is running on localhost:8000 (e.g., using `uvicorn main:app --reload`)

    # Test with a dummy file (create one for testing)
    test_file_path = pathlib.Path("C:\\temp\\test_document.pdf")
    test_dir_path = pathlib.Path("C:\\temp\\test_folder")

    # Create dummy files and folder for testing
    # This setup block should ideally be run once before all tests.
    if not test_file_path.parent.exists():
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(test_file_path, 'w') as f:
        f.write("This is a test PDF content.")

    if not test_dir_path.exists():
        test_dir_path.mkdir(parents=True, exist_ok=True)


    # region File Processing Test Cases

    print("\n--- Test Case 1: Valid File ---")
    # --- Start timing for THIS test case ---
    test_case_start_time = time.monotonic()
    valid_file_path = str(test_file_path)
    encoded_valid_file_path = urllib.parse.quote(valid_file_path)
    url = f"http://localhost:8000/process-file/?file_path={encoded_valid_file_path}"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")
        # --- End timing for THIS test case ---
        test_case_end_time = time.monotonic()
        test_case_duration = test_case_end_time - test_case_start_time

        if response.status_code == 200:
            print(f"\033[92mPassed in {test_case_duration:.4f} seconds\033[0m")
        else:
            print(f"\033[91mFailed in {test_case_duration:.4f} seconds\033[0m")
    except requests.exceptions.ConnectionError:
        print("Could not connect to FastAPI server. Is it running?")
        # If connection fails, duration is irrelevant for the server side, but still useful for client side
        test_case_end_time = time.monotonic()
        test_case_duration = test_case_end_time - test_case_start_time
        print(f"\033[91mConnection Error after {test_case_duration:.4f} seconds\033[0m")


    print("\n--- Test Case 2: Unsupported File Type ---")
    test_case_start_time = time.monotonic()
    unsupported_file_path = pathlib.Path("C:\\temp\\unsupported.exe")
    with open(unsupported_file_path, 'w') as f:
        f.write("This is an executable.")
    encoded_unsupported_file_path = urllib.parse.quote(str(unsupported_file_path))
    url = f"http://localhost:8000/process-file/?file_path={encoded_unsupported_file_path}"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}") # Print body before pass/fail check
        test_case_end_time = time.monotonic()
        test_case_duration = test_case_end_time - test_case_start_time

        if response.status_code == 400: # Expected failure for unsupported type
            print(f"\033[92mPassed in {test_case_duration:.4f} seconds\033[0m")
        else:
            print(f"\033[91mFailed in {test_case_duration:.4f} seconds\033[0m")
    except requests.exceptions.ConnectionError:
        print("Could not connect to FastAPI server. Is it running?")
        test_case_end_time = time.monotonic()
        test_case_duration = test_case_end_time - test_case_start_time
        print(f"\033[91mConnection Error after {test_case_duration:.4f} seconds\033[0m")
    finally:
        os.remove(unsupported_file_path) # Clean up


    print("\n--- Test Case 3: Non-existent File ---")
    test_case_start_time = time.monotonic()
    non_existent_path = "C:\\temp\\non_existent_file.pdf"
    encoded_non_existent_path = urllib.parse.quote(non_existent_path)
    url = f"http://localhost:8000/process-file/?file_path={encoded_non_existent_path}"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")
        test_case_end_time = time.monotonic()
        test_case_duration = test_case_end_time - test_case_start_time

        if response.status_code == 404: # Expected failure for non-existent file
            print(f"\033[92mPassed in {test_case_duration:.4f} seconds\033[0m")
        else:
            print(f"\033[91mFailed in {test_case_duration:.4f} seconds\033[0m")
    except requests.exceptions.ConnectionError:
        print("Could not connect to FastAPI server. Is it running?")
        test_case_end_time = time.monotonic()
        test_case_duration = test_case_end_time - test_case_start_time
        print(f"\033[91mConnection Error after {test_case_duration:.4f} seconds\033[0m")


    print("\n--- Test Case 4: Directory Input ---")
    test_case_start_time = time.monotonic()
    encoded_dir_path = urllib.parse.quote(str(test_dir_path))
    url = f"http://localhost:8000/process-file/?file_path={encoded_dir_path}"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")
        test_case_end_time = time.monotonic()
        test_case_duration = test_case_end_time - test_case_start_time

        if response.status_code == 400: # Expected failure for directory input
            print(f"\033[92mPassed in {test_case_duration:.4f} seconds\033[0m")
        else:
            print(f"\033[91mFailed in {test_case_duration:.4f} seconds\033[0m")
    except requests.exceptions.ConnectionError:
        print("Could not connect to FastAPI server. Is it running?")
        test_case_end_time = time.monotonic()
        test_case_duration = test_case_end_time - test_case_start_time
        print(f"\033[91mConnection Error after {test_case_duration:.4f} seconds\033[0m")


    print("\n--- Test Case 5: Path Traversal Attempt ---")
    test_case_start_time = time.monotonic()
    traversal_path = "C:\\temp\\..\\..\\windows\\system32\\drivers\\etc\\hosts"
    encoded_traversal_path = urllib.parse.quote(traversal_path)
    url = f"http://localhost:8000/process-file/?file_path={encoded_traversal_path}"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")
        test_case_end_time = time.monotonic()
        test_case_duration = test_case_end_time - test_case_start_time

        if response.status_code == 400: # Expected failure for path traversal
            print(f"\033[92mPassed in {test_case_duration:.4f} seconds\033[0m")
        else:
            print(f"\033[91mFailed in {test_case_duration:.4f} seconds\033[0m")
    except requests.exceptions.ConnectionError:
        print("Could not connect to FastAPI server. Is it running?")
        test_case_end_time = time.monotonic()
        test_case_duration = test_case_end_time - test_case_start_time
        print(f"\033[91mConnection Error after {test_case_duration:.4f} seconds\033[0m")

    # endregion

    #region Folder Processing Test Cases

    #TODO

    #endregion

    #region Cleanup
    # --- Clean up dummy files/folders ---
    try:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        if os.path.exists(test_dir_path):
            os.rmdir(test_dir_path)
        # Only remove C:\temp if it was created by this script and is empty
        if os.path.exists(test_dir_path.parent) and not list(test_dir_path.parent.iterdir()):
            os.rmdir(test_dir_path.parent)
    except OSError as e:
        print(f"Error cleaning up test files: {e}")


    # --- Total execution time for all tests ---
    overall_end_time = time.monotonic()
    total_duration = overall_end_time - overall_start_time
    print(f"\n== Finished all File Tests In {total_duration:.4f} seconds ==")
    #endregion
    

