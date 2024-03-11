import os
import re
import sys
import requests
import time
from pathlib import Path

re_url = re.compile(r'[<"](https://github|https://raw.githubusercontent[^>"]*)[>"]')


def get_urls(root_dirs):
    """
    Get URLs from .ttl files in specified directories.
    """
    urls = []
    for root_dir in root_dirs:
        for file_path in Path(root_dir).rglob("*.ttl"):
            for url in re_url.findall(file_path.read_text(encoding="utf8")):
                urls.append((file_path, url.strip('<">'), root_dir))
    return urls


def request_url(method, url):
    """
    Make HTTP request to the given URL with retries.
    """
    for i in range(1, 4):
        ret = method(url)
        if ret.status_code != 429:
            break

        backoff = int(ret.headers["Retry-After"])
        if backoff > 100:
            backoff = 100
        time.sleep(i * backoff)
    return ret

def extract_relative_path(url, root_dir):
    """
    Extracts the relative path from the URL based on the root directory.
    Returns None if an error occurs.
    """
    # Check if root_dir is present in the URL
    if root_dir not in url:
        return None

    # Find the index of the root_dir in the URL
    start_index = url.find(root_dir)
    if start_index == -1:
        return None

    # Extract relative path from start_index
    relative_path = url[start_index:]

    return relative_path

def check_local_file_exists(file_path):
    """
    Check if the file exists locally
    If the file exists locally, it will exist when a PR is merged
    """
    return os.path.exists(file_path)


def main(root_dirs):
    errors = []

    for file_path, url, root_dir in get_urls(root_dirs):

        ret = request_url(requests.head, url)

        if ret.status_code != 200:
            relative_path = extract_relative_path(url, root_dir)

            if relative_path:
                local_file_exists = check_local_file_exists(relative_path)

                if not local_file_exists:
                    errors.append(f"Error: URL {url} in file {file_path} is not accessible, and the corresponding local file does not exist.")
            else:
                errors.append(f"ERROR: the corresponding local file of url {url} does not exist, root_dir {root_dir} is different")

    if errors:
        for error in errors:
            print(error)
        return False
    else:
        return True


if __name__ == "__main__":
    root_dirs = sys.argv[1:]  # Read dir args
    if not main(root_dirs):
        exit(1)
