import os
import re
import requests
import time
from pathlib import Path
from urllib.parse import urlparse


re_url = re.compile(r'[<"](https://github.*|https://raw.githubusercontent[^>"]*)[>"]')
root_dirs = ["assets/controlled-vocabularies/", "assets/ontologies/", "assets/schemas/"]

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

def check_repository_existence(url):
    # Extract the username and repository name from the URL
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split("/")
    username = path_parts[1]
    repository = path_parts[2]

    # GET request to verify the existence of the repository
    response = requests.get(f"https://api.github.com/repos/{username}/{repository}")

    # The repo exists on Github
    if response.status_code == 200:
        return True
    # The repo doesn't exist on Github
    else:
        return False


def test_url():
    print("Starting URL test...")
    errors = []

    for file_path, url, root_dir in get_urls(root_dirs):
        print(f"Testing URL: {url}")

        ret = request_url(requests.head, url)
        print(f"status_code: {ret}")

        if ret.status_code != 200:
            relative_path = extract_relative_path(url, root_dir)

            if relative_path:
                local_file_exists = check_local_file_exists(relative_path)
                github_repo_exists = check_repository_existence(url)

                if not (local_file_exists and github_repo_exists):
                    errors.append(f"ERROR: URL '{url}' in file '{file_path}' is not accessible, and the corresponding local file does not exist.")
            else:
                errors.append(f"ERROR: the corresponding local file of url '{url}' in file '{file_path}' does not exist, root_dir '{root_dir}' is different")

    if errors:
        print("\nErrors found during URL test:")
        for error in errors:
            print(error)
        assert False, "\n".join(errors)
    else:
        print("URL test completed successfully!")
