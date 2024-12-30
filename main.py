import argparse
import glob
import os

# hard code the data directory and file paths
DATA_DIR = "./data"
POST_LIST = f"{DATA_DIR}/post_list.json"
POST_LIST_DIFF = f"{DATA_DIR}/post_list.diff.json"
POST_CONTENT = f"{DATA_DIR}/post_content.json"
POST_CONTENT_DIFF = f"{DATA_DIR}/post_content.diff.json"


def fetch_post_list(is_update: bool):
    if is_update:
        command = [
            "python", "fetch_post_list.py",
            "--update",
            "--diff-input", POST_LIST,
            "--diff-output", POST_LIST_DIFF,
            "--output", POST_LIST,
            "--base-url", args.base_url,
            "--type-list", args.type_list,
            "--concurrency", str(args.concurrency),
            "--timeout", str(args.timeout)
        ]
    else:
        command = [
            "python", "fetch_post_list.py",
            "--output", POST_LIST,
            "--base-url", args.base_url,
            "--type-list", args.type_list,
            "--concurrency", str(args.concurrency),
            "--timeout", str(args.timeout)
        ]
    os.system(" ".join(command))


def fetch_post_content(is_update: bool):
    if is_update:
        command = [
            "python", "fetch_post_content.py",
            "--update",
            "--input", POST_LIST_DIFF,
            "--output", POST_CONTENT,
            "--diff-input", POST_CONTENT,
            "--diff-output", POST_CONTENT_DIFF,
            "--base-url", args.base_url,
            "--concurrency", str(args.concurrency),
            "--timeout", str(args.timeout)
        ]
    else:
        command = [
            "python", "fetch_post_content.py",
            "--input", POST_LIST,
            "--output", POST_CONTENT,
            "--base-url", args.base_url,
            "--concurrency", str(args.concurrency),
            "--timeout", str(args.timeout)
        ]
    os.system(" ".join(command))


def main():
    if args.force_refetch:
        input(f"This will delete all json in {DATA_DIR}, press Enter to continue")
        json_files = glob.glob(os.path.join(DATA_DIR, '*.json'))
        for file_path in json_files:
            os.remove(file_path)

    is_update = False
    if os.path.exists(POST_LIST) and os.path.exists(POST_CONTENT):
        is_update = True
    print(f"Start {'update' if is_update else 'initial'} fetching")

    fetch_post_list(is_update)
    fetch_post_content(is_update)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", type=str, default="http://i.whut.edu.cn")
    parser.add_argument("--type-list", type=str, default="xxtg,xytg,bmxw,lgjz")
    parser.add_argument("--concurrency", type=int, default=32)
    parser.add_argument("--force-refetch", action="store_true")
    parser.add_argument("--timeout", type=int, default=5)
    args = parser.parse_args()
    main()
