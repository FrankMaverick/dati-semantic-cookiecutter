import os
import re
import sys

def check_filename_format(root_dirs):
    """
    Check whether file and directory names follow the specified format (pattern)
    Args:
        root_dirs (list): A list of root directories to be checked.
    Returns:
        bool: True if all file and directory names match the required format, False otherwise.
    """

    pattern = r'^[\\.a-z0-9 _-]{1,64}$'
    extensions_to_check = ['.ttl', '.rdf', '.csv', '.yaml']

    for root_dir in root_dirs:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                name, extension = os.path.splitext(filename)
                if extension not in extensions_to_check:
                    continue
                if not re.match(pattern, name):
                    print(f"Error: filename '{filename}' in directory '{dirpath}' does not match the required format.")
                    return False
            for dirname in dirnames:
                if not re.match(pattern, dirname):
                    print(f"Error: directory name '{dirname}' in directory '{dirpath}' does not match the required format.")
                    return False

    return True

if __name__ == "__main__":
    root_dirs = sys.argv[1:]  # Read dir args
    if not check_filename_format(root_dirs):
        exit(1)
