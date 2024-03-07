import os
import sys

def check_structure(required_dirs):
    """
    Check whether the directory structure is correct.
    """

    for dir in required_dirs:
        if not os.path.exists(dir):
            print(f"Error: directory '{dir}' not exists.")
            return False

    return True

if __name__ == "__main__":
    required_dirs = sys.argv[1:]  # Read dir args
    if not check_structure(required_dirs):
        exit(1)