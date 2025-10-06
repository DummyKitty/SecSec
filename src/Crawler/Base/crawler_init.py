# _*_ coding : utf-8 _*_
# @Time: 2025/4/25 16:47
# @Author : Natro92
# @Email : natro92@natro92.fun
# @Blog : https://natro92.fun
# @File : crawler_init
# @Project : SecSec
import time

from colorama import Fore
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import platform

from toollib import autodriver

from config import *
from src.Utils.log_manager import success


def init_chrome():
    """
    初始化Chrome浏览器
    :return:
    """
    # 判断是否存在
    if os.path.exists(os.path.join(DRIVER_PATH)):
        print('[*] Info - 已初始化Chrome浏览器，请选择模式 ')
        exit(1)
    print('[*] Info - 正在初始化Chrome浏览器，请稍后... (配置文件约15MB，可以通过开启代理来加速下载)')
    driver_path = autodriver.chromedriver()
    print(success(f"[*] Info - 已成功初始化，ChromeDriver路径: {driver_path}"))


def init_local_chrome():
    # ! 一行配置绕过阿里云机器人验证手动失效，webdriver和普通浏览器参数不同。
    # https://blog.csdn.net/weixin_45081575/article/details/126585575
    # * 创建本机chrome实例，并使用调试模式
    # os.popen('start chrome --remote-debugging-port=9527')
    # time.sleep(5)
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # 检查是否启用无头模式
    if os.environ.get('SELENIUM_HEADLESS', '').lower() == '1':
        options.add_argument("--headless")
        print("[*] Info - 启用无头模式")
    
    # 添加更多稳定性选项
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    
    # 添加调试选项（如果启用调试模式）
    if os.environ.get('SELENIUM_DEBUG', '').lower() == '1':
        options.add_argument("--verbose")
        options.add_argument("--log-level=0")
        print("[*] Info - 启用 Selenium 调试模式")
    
    # 检查 ChromeDriver 是否存在
    if os.path.exists(DRIVER_PATH):
        # 使用本地 ChromeDriver
        service = Service(executable_path=DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        # 使用系统 PATH 中的 ChromeDriver
        driver = webdriver.Chrome(options=options)
    
    print(success("[*] Info - 已成功初始化本机Chrome浏览器"))
    return driver
