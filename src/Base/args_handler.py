# _*_ coding : utf-8 _*_
# @Time: 2025/4/25 16:24
# @Author : Natro92
# @Email : natro92@natro92.fun
# @Blog : https://natro92.fun
# @File : Args
# @Project : SecSec

import argparse
import json

from colorama import Fore

from src.Crawler.Base.crawler_init import init_chrome
from src.Crawler.Freebuf.crawler_run import run_freebuf_crawler
from src.Crawler.Xianzhi.crawler_run import run_xianzhi_crawler
from src.Crawler.Butian.crawler_run import run_butian_crawler
from config import FILE_SAVE_PATH, FREEBUF_CATEGORY, FREEBUF_PAGE_START, FREEBUF_PAGE_END
from config import XIANZHI_PAGE_START, XIANZHI_PAGE_END, XIANZHI_400_SLEEP, XIANZHI_PIC_BLACKLIST
from config import BUTIAN_CATEGORY, BUTIAN_PAGE_START, BUTIAN_PAGE_END

try:
    from gooey import GooeyParser
except Exception:
    # 回退到 argparse，确保命令行可用
    GooeyParser = argparse.ArgumentParser
from src.Utils.log_manager import success


def print_splash():
    print(f'''
    {Fore.CYAN}______{Fore.RESET}_____        {Fore.CYAN}____{Fore.RESET}______           
     {Fore.CYAN}____{Fore.RESET}  ___/____________  ___/___________
      {Fore.CYAN}__{Fore.RESET}____ \\_  _ \\  ___/____ \\_  _ \\  ___/
       {Fore.CYAN}_{Fore.RESET}___/ //  __/ /__ ____/ //  __/ /__  
       /____/ \\___/\\___/ /____/ \\___/\\___/  
                       @Natro92 - https://natro92.fun - natro92@natro92.fun
    ''')


def print_help():
    """
    打印帮助信息
    :return:
    """
    print(f'''
    {Fore.CYAN}______{Fore.RESET}_____        {Fore.CYAN}____{Fore.RESET}______           
     {Fore.CYAN}____{Fore.RESET}  ___/____________  ___/___________
      {Fore.CYAN}__{Fore.RESET}____ \\_  _ \\  ___/____ \\_  _ \\  ___/
       {Fore.CYAN}_{Fore.RESET}___/ //  __/ /__ ____/ //  __/ /__  
       /____/ \\___/\\___/ /____/ \\___/\\___/  
                       @Natro92 - https://natro92.fun - natro92@natro92.fun
    Usage: SecSec.py [freebuf|xianzhi|butian|init] [options]

Options:
-h, --help          显示帮助
freebuf             爬取FreeBuf文章
xianzhi             爬取先知社区文章
butian              爬取补天社区文章
init                初始化Chrome浏览器
    ''')


def parse_args():
    """
    解析命令行参数（Gooey 子命令：先选择模块，再填写参数）
    """
    parser = GooeyParser(add_help=True, description='请选择要运行的模块')

    subparsers = parser.add_subparsers(dest='module', help='模块', metavar='模块')

    # init 子命令
    p_init = subparsers.add_parser('init', help='初始化 Chrome 浏览器')

    # freebuf 子命令
    p_freebuf = subparsers.add_parser('freebuf', help='爬取 FreeBuf 文章')
    p_freebuf.add_argument('--file_save_path', type=str, default=FILE_SAVE_PATH, help='文件保存路径')
    p_freebuf.add_argument('--freebuf_category', type=str, default=','.join(FREEBUF_CATEGORY), help='FreeBuf分类(逗号分隔)')
    p_freebuf.add_argument('--freebuf_page_start', type=int, default=FREEBUF_PAGE_START, help='FreeBuf起始页')
    p_freebuf.add_argument('--freebuf_page_end', type=int, default=FREEBUF_PAGE_END, help='FreeBuf结束页(包含)')
    p_freebuf.add_argument('--freebuf_page_config', type=str, default='', help='FreeBuf分页配置(JSON, 优先级高于起止页)')

    # xianzhi 子命令
    p_xz = subparsers.add_parser('xianzhi', help='爬取 先知 社区文章')
    p_xz.add_argument('--file_save_path', type=str, default=FILE_SAVE_PATH, help='文件保存路径')
    p_xz.add_argument('--xianzhi_page_start', type=int, default=XIANZHI_PAGE_START, help='先知起始页')
    p_xz.add_argument('--xianzhi_page_end', type=int, default=XIANZHI_PAGE_END, help='先知结束页(包含)')
    p_xz.add_argument('--xianzhi_400_sleep', choices=['true', 'false'], default=('true' if XIANZHI_400_SLEEP else 'false'), help='先知400超时后睡眠')
    p_xz.add_argument('--xianzhi_pic_blacklist', type=str, default=','.join(XIANZHI_PIC_BLACKLIST), help='先知图片黑名单(逗号分隔)')

    # butian 子命令
    p_bt = subparsers.add_parser('butian', help='爬取 补天 社区文章')
    p_bt.add_argument('--file_save_path', type=str, default=FILE_SAVE_PATH, help='文件保存路径')
    p_bt.add_argument('--butian_category', type=str, default=','.join(BUTIAN_CATEGORY), help='补天分类(逗号分隔)：article,share')
    p_bt.add_argument('--butian_page_start', type=int, default=BUTIAN_PAGE_START, help='补天起始页(含)')
    p_bt.add_argument('--butian_page_end', type=int, default=BUTIAN_PAGE_END, help='补天结束页(不含)')

    args = parser.parse_args()

    if not getattr(args, 'module', None):
        print_splash()
        return

    if args.module == 'init':
        print(success("初始化Chrome浏览器..."))
        init_chrome()
        return

    if args.module == 'freebuf':
        print("爬取FreeBuf文章...")
        freebuf_category = [s.strip() for s in args.freebuf_category.split(',') if s.strip()]
        freebuf_page_config = None
        if args.freebuf_page_config and args.freebuf_page_config.strip():
            try:
                freebuf_page_config = json.loads(args.freebuf_page_config)
            except Exception as e:
                print(f"FreeBuf分页配置 JSON 解析失败: {e}")
        run_freebuf_crawler(
            freebuf_category=freebuf_category,
            freebuf_page_start=args.freebuf_page_start,
            freebuf_page_end=args.freebuf_page_end,
            freebuf_page_config=freebuf_page_config,
            file_save_path=args.file_save_path,
        )
        return

    if args.module == 'xianzhi':
        print("爬取先知社区文章...")
        xz_blacklist = [s.strip() for s in args.xianzhi_pic_blacklist.split(',') if s.strip()]
        run_xianzhi_crawler(
            xianzhi_page_start=args.xianzhi_page_start,
            xianzhi_page_end=args.xianzhi_page_end,
            xianzhi_400_sleep=(args.xianzhi_400_sleep.lower() == 'true'),
            file_save_path=args.file_save_path,
            xianzhi_pic_blacklist=xz_blacklist,
        )
        return

    if args.module == 'butian':
        print("爬取补天社区文章...")
        butian_category = [s.strip() for s in args.butian_category.split(',') if s.strip()]
        run_butian_crawler(
            butian_category=butian_category,
            butian_page_start=args.butian_page_start,
            butian_page_end=args.butian_page_end,
            file_save_path=args.file_save_path,
        )
        return


if __name__ == '__main__':
    parse_args()
