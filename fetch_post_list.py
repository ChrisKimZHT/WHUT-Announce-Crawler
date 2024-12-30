import argparse
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def get_page_count(typ: str) -> int:
    url = f"{args.base_url}/{typ}"
    try:
        response = requests.get(url)
        response.encoding = "utf-8"

        html = response.text
        page_count = re.search(r"var countPage = (\d+)", html).group(1)

        return int(page_count)
    except Exception as e:
        print(f"Error parse page count {url}: {e}")
        return 0


def process_one_page(typ: str, page: int) -> tuple[str, list]:
    url = f"{args.base_url}/{typ}"
    if page > 0:
        url += f"/index_{page}.shtml"

    for retry in range(3):
        try:
            response = requests.get(url, timeout=args.timeout)
            response.encoding = "utf-8"
            break
        except Exception as e:
            print(f"Error fetch post list {url}, retry {retry}: {e}")
            time.sleep(2)
    else:
        print(f"Error fetch post list {url}: retry 3 times failed")
        return typ, []

    try:
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        links = soup.find("ul", class_="normal_list2").select("li > span > a")

        return typ, [{
            "title": link.get_text(),
            "url": urljoin(f"{args.base_url}/{typ}/", link["href"])
        } for link in links]
    except Exception as e:
        print(f"Error parse post list {url}: {e}")
        return typ, []


def main():
    page_list = []
    result = {}
    diff_result = {}

    type_list = args.type_list.split(",")
    for typ in type_list:
        max_page = get_page_count(typ)
        page_list.extend(zip([typ] * max_page, range(1, max_page)))
        result[typ] = []
        diff_result[typ] = []
        print(f"{typ}: {max_page} pages")

    if not args.update:
        # important: ensure 0 page is in the front, otherwise the update fetch will be incorrect
        for typ in type_list:
            result[typ].extend(process_one_page(typ, 0)[1])

        # full fetch, using multi-threading
        with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            futures = {executor.submit(process_one_page, page_type, page_number) for page_type, page_number in page_list}

            for future in tqdm(as_completed(futures), total=len(page_list), dynamic_ncols=True):
                typ, page_result = future.result()
                result[typ].extend(page_result)
    else:
        # update fetch, using single-threading
        if args.diff_input is None:
            print("Error: input file is required for update fetch")
            return
        with open(args.diff_input, "r", encoding="utf-8") as f:
            old_result = json.load(f)

        old_head = {}
        for typ, posts in old_result.items():
            old_head[typ] = {"head": posts[0]["url"], "status": False}
        print("Old head:", old_head)

        for page_type, page_number in tqdm(page_list, dynamic_ncols=True):
            if old_head[page_type]["status"]:
                continue
            typ, page_result = process_one_page(page_type, page_number)
            for post in page_result:
                if post["url"] == old_head[page_type]["head"]:
                    old_head[page_type]["status"] = True
                    break
                diff_result[typ].append(post)

        with open(args.diff_output, "w", encoding="utf-8") as f:
            json.dump(diff_result, f, ensure_ascii=False, indent=2)

        type_list = list(set(old_result.keys()) | set(diff_result.keys()))
        for typ in type_list:
            result[typ] = diff_result.get(typ, []) + old_result.get(typ, [])

    for typ in type_list:
        print(f"{typ}: {len(result[typ])} posts")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", type=str, default="http://i.whut.edu.cn")
    parser.add_argument("--type-list", type=str, default="xxtg,xytg,bmxw,lgjz")
    parser.add_argument("--concurrency", type=int, default=32)
    parser.add_argument("--timeout", type=int, default=5)
    parser.add_argument("--output", type=str, default="./post_list.json")
    parser.add_argument("--diff-input", type=str, default="./post_list.json")
    parser.add_argument("--diff-output", type=str, default="./post_list.diff.json")
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()
    main()
