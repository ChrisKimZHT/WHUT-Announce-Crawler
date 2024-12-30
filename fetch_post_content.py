import argparse
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def get_post_content(typ: str, url: str) -> tuple[str, dict]:
    for retry in range(3):
        try:
            response = requests.get(url)
            response.encoding = "utf-8"
            break
        except Exception as e:
            print(f"Error fetch post {url}, retry {retry}: {e}")
            time.sleep(2)
    else:
        print(f"Error fetch post {url}: retry 3 times failed")
        return typ, {}

    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    if "<title>欢迎访问武汉理工大学综合信息系统</title>" not in html:
        print(f"Error fetch post {url}: not a post page")
        return typ, {}

    try:
        title = soup.find("div", class_="art_tit").find("h2").text

        author_and_date = soup.find("div", class_="art_info").text  # 发布：能动学院综合办\xa0\xa0时间：2021-04-13\xa0\xa0我要纠错
        author, date = re.search(r"发布：(.+?)\xa0\xa0时间：(.+?)\xa0", author_and_date).groups()

        content = soup.find("div", class_="art_text").text

        image_tags = soup.find("div", class_="art_text").select("img")
        image_urls = [img["src"] for img in image_tags]

        file_tags = soup.find('div', class_='file_box').find_all('a')
        file_urls = [urljoin(url, file_tag.get('href')) for file_tag in file_tags]

        return typ, {
            "url": url,
            "title": title,
            "author": author,
            "date": date,
            "content": content,
            "images": image_urls,
            "files": file_urls
        }
    except Exception as e:
        print(f"Error parse post {url}: {e}")
        return typ, {}


def main():
    with open(args.input, "r", encoding="utf-8") as f:
        post_list = json.load(f)

    job_list = []
    result = {}
    for typ, posts in post_list.items():
        job_list.extend([(typ, post["url"]) for post in posts])
        result[typ] = []
        print(f"{typ}: {len(posts)} posts")

    print(f"Befor filter: {len(job_list)} posts")
    job_list = list(filter(lambda x: x[1].startswith(args.base_url) and x[1].endswith(".shtml"), job_list))
    print(f"After filter: {len(job_list)} posts")

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [executor.submit(get_post_content, *job) for job in job_list]

        for future in tqdm(as_completed(futures), total=len(job_list)):
            typ, post = future.result()
            if post == {}:
                continue
            result[typ].append(post)

    if args.update:
        diff_result = deepcopy(result)
        result = {}

        with open(args.diff_input, "r", encoding="utf-8") as f:
            old_result = json.load(f)

        type_list = list(set(old_result.keys()) | set(diff_result.keys()))
        for typ in type_list:
            result[typ] = diff_result.get(typ, []) + old_result.get(typ, [])

        with open(args.diff_output, "w", encoding="utf-8") as f:
            json.dump(diff_result, f, ensure_ascii=False, indent=2)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", type=str, default="http://i.whut.edu.cn")
    parser.add_argument("--concurrency", type=int, default=32)
    parser.add_argument("--input", type=str, default="./post_list.json")
    parser.add_argument("--output", type=str, default="./post_content.json")
    parser.add_argument("--diff-input", type=str, default="./post_content.json")
    parser.add_argument("--diff-output", type=str, default="./post_content.diff.json")
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()
    main()
