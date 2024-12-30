# WHUT-Announce-Crawler

武汉理工大学校内综合信息网 (i.whut.edu.cn) 爬虫，可将全站所有公告爬取保存为以下结构的 JSON 文件。支持多线程，支持差量更新。

```json5
[
  {
    "url": "",     // 原文链接
    "title": "",   // 标题
    "author": "",  // 发布单位
    "date": "",    // 发布日期
    "content": "", // 正文
    "images": [],  // 正文中的图片
    "files": []    // 附件
  }
]
```

## 自动运行

- 安装依赖：`pip install -r requirements.txt`
- 运行爬虫：`python main.py`

首次运行会爬取所有公告，之后运行会自动检测新公告并更新。

可用参数：

| 参数              | 类型         | 默认值                 | 说明                       |
| ----------------- | ------------ | ---------------------- | -------------------------- |
| `--base-url`      | `str`        | `http://i.whut.edu.cn` | 基础链接                   |
| `--type-list`     | `str`        | `xxtg,xytg,bmxw,lgjz`  | 爬取的公告类型，逗号分隔   |
| `--concurrency`   | `int`        | `32`                   | 爬取线程数，别把学校爬炸了 |
| `--force-refetch` | `store_true` | 否                     | 强制重新爬取               |
| `--timeout`       | `int`        | `5`                    | 请求超时时间               |

## 手动运行

自动运行会使用默认值处理可调参数，如果要灵活控制，可以手动调用爬虫文件 `fetch_post_list.py` 和 `fetch_post_content.py`。

`fetch_post_list.py` 用于获取公告列表，可用参数：

| 参数            | 类型         | 默认值                  | 说明                               |
| --------------- | ------------ | ----------------------- | ---------------------------------- |
| `--base-url`    | `str`        | `http://i.whut.edu.cn`  | 基础链接                           |
| `--type-list`   | `str`        | `xxtg,xytg,bmxw,lgjz`   | 爬取的公告类型，逗号分隔           |
| `--concurrency` | `int`        | `32`                    | 爬取线程数，别把学校爬炸了         |
| `--timeout`     | `int`        | `5`                     | 请求超时时间                       |
| `--output`      | `str`        | `./post_list.json`      | 输出的**新公告列表**路径           |
| `--diff-input`  | `str`        | `./post_list.json`      | 差量更新输入的**旧公告列表**路径   |
| `--diff-output` | `str`        | `./post_list.diff.json` | 差量更新输出的**差异公告列表**路径 |
| `--update`      | `store_true` | 否                      | 差量更新模式                       |

`fetch_post_content.py` 用于获取公告内容，可用参数：

| 参数            | 类型   | 默认值                     | 说明                               |
| --------------- | ------ | -------------------------- | ---------------------------------- |
| `--base-url`    | `str`  | `http://i.whut.edu.cn`     | 基础链接                           |
| `--concurrency` | `int`  | `32`                       | 爬取线程数，别把学校爬炸了         |
| `--timeout`     | `int`  | `5`                        | 请求超时时间                       |
| `--input`       | `str`  | `./post_list.json`         | 输入的**要爬取的公告列表**路径     |
| `--output`      | `str`  | `./post_content.json`      | 输出的**公告内容**路径             |
| `--diff-input`  | `str`  | `./post_content.json`      | 差量更新输入的**旧公告内容**路径   |
| `--diff-output` | `str`  | `./post_content.diff.json` | 差量更新输出的**差异公告内容**路径 |
| `--update`      | `bool` | 否                         | 差量更新模式                       |