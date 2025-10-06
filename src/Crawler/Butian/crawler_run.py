# _*_ coding : utf-8 _*_
# @Time: 2025/4/25 23:34
# @Author : Natro92
# @Email : natro92@natro92.fun
# @Blog : https://natro92.fun
# @File : crawler_run
# @Project : SecSec

import os
import random
import re
import threading
import time

import markdownify
import requests
from bs4 import BeautifulSoup
from colorama import Fore
from tqdm import tqdm, trange

from config import *
from src.Crawler.Base.crawler_init import init_local_chrome
from src.Utils.file_manager import ensure_directory_exists, is_image_folder_created
from src.Utils.log_manager import fail
from src.Utils.text_builder import filename_filter


def run_butian_crawler(
        butian_category=None,
        butian_page_start=None,
        butian_page_end=None,
        file_save_path=None,
):
    """
    运行 Butian 爬虫
    :return:
    """
    driver_local = init_local_chrome()

    # 参数覆盖配置
    butian_category = butian_category if butian_category is not None else BUTIAN_CATEGORY
    butian_page_start = butian_page_start if butian_page_start is not None else BUTIAN_PAGE_START
    butian_page_end = butian_page_end if butian_page_end is not None else BUTIAN_PAGE_END
    file_save_path = file_save_path if file_save_path is not None else FILE_SAVE_PATH

    if not butian_category:
        tqdm.write(fail("[!] Error - 未配置 Butian 分类，请检查 config.py 文件"))
        exit(1)
    if not butian_page_start or not butian_page_end:
        tqdm.write(fail("[!] Error - 未配置 Butian 初始页数，请检查 config.py 文件"))
        exit(1)

    butian_crawler_main(driver_local, butian_category, butian_page_start, butian_page_end, file_save_path)
    driver_local.quit()


def butian_crawler_main(driver, butian_category, butian_page_start, butian_page_end, file_save_path):
    """
    处理 Butian 文章
    :param driver: 浏览器驱动
    """
    base_url = r'https://forum.butian.net/{category}/{post_index}'
    is_image_folder_created('butian', file_save_path)

    for category in butian_category:
        for post_index in trange(butian_page_start, butian_page_end, desc='[+] 正在爬取 Butian 文章'):
            url = base_url.format(category=category, post_index=post_index)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            title_tag = soup.find('title')
            post_title = filename_filter(title_tag.text) if title_tag else None
            if not post_title or ('404' in post_title):
                tqdm.write(Fore.RED + f'[!] Error - {post_index} 未找到该文章' + Fore.RESET)
                continue

            post_title = post_title[8:]
            filename = os.path.join(file_save_path, 'butian', f'{post_index}-{post_title}.md')
            if os.path.exists(filename):
                tqdm.write(f'[*] Info - {post_index}-{post_title} 已经爬取过，跳过')
                continue

            img_tags = soup.find_all('img')
            download_images(img_tags, os.path.join(file_save_path, 'butian', 'images'), random.choice(CRAWLER_HEADERS))
            md_content = markdownify.markdownify(driver.page_source)
            # 依据标题与评论标记切分正文，去掉导航/注册等头部与评论区及其后
            md_content = split_content(md_content, post_title)
            md_content = process_images(md_content, img_tags)
            md_content = beautify_md(md_content)
            save_post(post_index, post_title, md_content, filename)

            actual_sleep_time = SLEEP_TIME + random.uniform(-SLEEP_TIME_DELTA, SLEEP_TIME_DELTA)
            time.sleep(actual_sleep_time)


def check_split_strings(md_content, post_title):
    """
    检查分割字符串
    :param md_content: Markdown内容
    :param post_title: 文章标题
    :return: 分割字符串
    """
    if len(post_title) * '=' in md_content:
        return len(post_title) * '='
    else:
        return len(post_title) * '-'


def split_content(md_content, post_title):
    """
    按规则切分正文：
    - 去掉头部（导航/登录/注册等），从标题开始
    - 去掉尾部（评论区及其后/站点页脚）
    :param md_content: Markdown全文
    :param post_title: 文章标题（已过滤非法文件名字符）
    :return: 切分后的正文
    """
    if not md_content:
        return md_content

    text = md_content.replace('\r\n', '\n').replace('\r', '\n')

    # 1) 定位正文开始：优先匹配 ATX 标题（###/##/#），再匹配 setext 标题（===/--- 下划线）
    title_candidates = [
        f"###### {post_title}",
        f"##### {post_title}",
        f"#### {post_title}",
        f"### {post_title}",
        f"## {post_title}",
        f"# {post_title}",
    ]

    start_idx = -1
    for pat in title_candidates:
        start_idx = text.find(pat)
        if start_idx != -1:
            break

    if start_idx == -1:
        # 尝试 setext 风格：标题行 + 下划线
        underline_eq = f"\n{len(post_title) * '='}\n"
        underline_dash = f"\n{len(post_title) * '-'}\n"
        title_pos = text.find(post_title)
        if title_pos != -1:
            ueq_pos = text.find(underline_eq, title_pos)
            udash_pos = text.find(underline_dash, title_pos)
            if ueq_pos != -1 and ueq_pos - title_pos < 200:
                start_idx = title_pos
            elif udash_pos != -1 and udash_pos - title_pos < 200:
                start_idx = title_pos

    if start_idx == -1:
        # 退化：尝试从第一个正文常见小节开始（如 0x00/0x01）
        for sec_pat in ['\n0x00', '\n0x01', '\n前言', '\n\n### ']:
            pos = text.find(sec_pat)
            if pos != -1:
                start_idx = pos
                break

    if start_idx == -1:
        start_idx = 0

    content_after_start = text[start_idx:]

    # 2) 定位正文结束：遇到评论/页脚/站点信息等标记时截断
    tail_markers = [
        '\n* 发表于 ',
        '\n发表于 ',
        '\n条评论',
        '\n评论\n',
        '\n0 条评论',
        '\n请先 [登录] 后评论',
        '\n请先 [登录] 后发送私信',
        '\n目录\n--',
        '\n奇安信攻防社区',
        '\nsitemap',
        'Copyright',
        '站长统计',
        '加载中',
        '发送私信',
        '举报此文章',
        '由极验提供技术支持',
    ]

    end_idx = -1
    for marker in tail_markers:
        pos = content_after_start.find(marker)
        if pos != -1:
            end_pos = pos
            if end_idx == -1 or end_pos < end_idx:
                end_idx = end_pos

    if end_idx != -1:
        content_after_start = content_after_start[:end_idx]

    return content_after_start


def process_images(md_content, img_tags):
    """
    处理图片相关的替换操作，不抽出来复杂度太高了，看的迷糊
    :param md_content: 原始的 Markdown 内容
    :param img_tags: 图片标签列表
    :return: 处理后的 Markdown 内容
    """
    for img_tag in img_tags:
        img_src = img_tag.get("src", "images/default_avatar.jpg")
        img_src = img_src if img_src else None
        if img_src is None:
            continue
        img_name = os.path.basename(img_src).replace('!small', '').split('?')[0].split('#')[0]
        md_content = md_content.replace(img_src, f'images/{img_name}')
    return md_content


def beautify_md(md_content):
    """
    简单美化 Markdown：
    - 去除首尾空白
    - 合并多余空行（>2 合并为 2）
    - 去除行尾多余空格
    """
    if not md_content:
        return md_content

    text = md_content.replace('\r\n', '\n').replace('\r', '\n')
    # 去除行尾空格
    lines = [ln.rstrip() for ln in text.split('\n')]

    # 合并 3+ 连续空行为 2，并移除由 2 个及以上连字符构成的横杠行（如 ----, --）
    compact_lines = []
    empty_run = 0
    for ln in lines:
        if re.fullmatch(r"\s*-{2,}\s*", ln):
            # 去掉 markdown 转换产生的横杠/分隔线/下划线
            continue
        if ln.strip() == '':
            empty_run += 1
        else:
            empty_run = 0
        if empty_run <= 2:
            compact_lines.append(ln)

    result = '\n'.join(compact_lines).strip('\n').strip()
    return result + '\n'


def save_post(post_index, post_title, md_content, filename):
    """
    保存文章内容到文件
    :param post_index: 文章索引
    :param post_title: 文章标题
    :param md_content: 文章内容
    :param filename: 文件保存路径
    """
    ensure_directory_exists(filename)
    with open(filename, 'w', encoding='UTF-8') as f:
        f.write(md_content)
    tqdm.write(Fore.GREEN + f'[*] Info - {post_index}-{post_title} 爬取完成' + Fore.RESET)


def download_images(img_tags, images_path, crawler_headers, max_threads=THREADS_NUM):
    """
    下载图片的函数（多线程，限制线程数量）
    :param img_tags: 图片标签列表
    :param images_path: 图片保存路径
    :param crawler_headers: 请求头
    :param max_threads: 最大线程数量
    """
    session = requests.Session()
    session.headers.update(crawler_headers)

    for img_tag in img_tags:
        img_src = img_tag.get("src", 'images/default_avatar.jpg')
        # 创建一个线程来下载图片
        thread = threading.Thread(target=download_image_with_session, args=(img_src, images_path, session))
        thread.start()


def download_image_with_session(img_src, images_path, session):
    """
    使用session的单个图片下载函数
    :param img_src: 图片的源地址
    :param images_path: 图片保存路径
    :param session: requests.Session 对象
    """
    if not img_src:
        return
    if 'http' not in img_src:
        tqdm.write(Fore.YELLOW + f'[?] Warn - 图片格式错误 {img_src}' + Fore.RESET)
        return
    img_name = os.path.basename(img_src).replace('!small', '').split('?')[0]
    if not img_name:
        tqdm.write(Fore.YELLOW + f'[?] Warn - 图片名称为空 {img_src}' + Fore.RESET)
        return
    image_path = os.path.join(images_path, img_name)
    if os.path.exists(image_path):
        return
    try:
        img_pic = session.get(img_src, timeout=10).content  # 添加超时时间
        with open(image_path, 'wb') as f:
            f.write(img_pic)
    except Exception as e:
        tqdm.write(Fore.RED + f'[!] Error - 无法下载图片从 {img_src}: {e}' + Fore.RESET)
        return


def process_post_reload(category, post_index, post_title, driver, file_save_path=None):
    """
    重新下载某一篇文章
    :param category: 分类
    :param post_index: index
    :param post_title: 标题
    :param driver: 驱动
    :return:
    """
    base_url = r'https://forum.butian.net/{category}/{post_index}'
    file_save_path = file_save_path if file_save_path is not None else FILE_SAVE_PATH
    filename = os.path.join(file_save_path, 'butian',
                            f"{post_index}-{filename_filter(post_title)}.md")
    post_url = base_url.format(category=category, post_index=post_index)
    driver.get(post_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    img_tags = soup.find_all('img')
    is_image_folder_created('butian', file_save_path)
    download_images(img_tags, os.path.join(file_save_path, 'butian', 'images'),
                    random.choice(CRAWLER_HEADERS))
    md_content = markdownify.markdownify(driver.page_source)
    md_content = split_content(md_content, post_title)
    md_content = process_images(md_content, img_tags)
    md_content = beautify_md(md_content)
    save_post(post_index, post_title, md_content, filename)
