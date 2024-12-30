import argparse
import json
import re
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

    try:
        response = requests.get(url)
        response.encoding = "utf-8"

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

    type_list = args.type_list.split(",")
    for typ in type_list:
        max_page = get_page_count(typ)
        page_list.extend(zip([typ] * max_page, range(max_page)))
        result[typ] = []
        print(f"{typ}: {max_page} pages")

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = {executor.submit(process_one_page, page_type, page_number) for page_type, page_number in page_list}

        for future in tqdm(as_completed(futures), total=len(page_list)):
            typ, page_result = future.result()
            result[typ].extend(page_result)

    for typ in type_list:
        print(f"{typ}: {len(result[typ])} posts")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", type=str, default="http://i.whut.edu.cn")
    parser.add_argument("--type-list", type=str, default="xxtg,xytg,bmxw,lgjz")
    parser.add_argument("--concurrency", type=int, default=32)
    parser.add_argument("--output", type=str, default="./post_list.json")
    args = parser.parse_args()
    main()
