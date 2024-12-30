import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from tqdm import tqdm


def download_file(url: str) -> None:
    for retry in range(3):
        try:
            response = requests.get(url)
            break
        except Exception as e:
            print(f"Error fetch file {url}, retry {retry}: {e}")
            time.sleep(2)
    else:
        print(f"Error fetch file {url}: retry 3 times failed")

    file_name = url.removeprefix(f"{args.base_url}/").replace("/", "_")
    with open(f"{args.output}/{file_name}", "wb") as f:
        f.write(response.content)


def main():
    with open(args.input, "r", encoding="utf-8") as f:
        post_content = json.load(f)

    file_list = []
    for _, posts in post_content.items():
        for post in posts:
            file_list.extend(post["files"])

    print(f"Start fetching {len(file_list)} files")

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [executor.submit(download_file, file) for file in file_list]
        for future in tqdm(as_completed(futures), total=len(futures), dynamic_ncols=True):
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", type=str, default="http://i.whut.edu.cn")
    parser.add_argument("--concurrency", type=int, default=32)
    parser.add_argument("--input", type=str, default="./post_content.json")
    parser.add_argument("--output", type=str, default="./data/file")
    args = parser.parse_args()
    main()
