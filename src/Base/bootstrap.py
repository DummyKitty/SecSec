# _*_ coding : utf-8 _*_
# @Time: 2025/4/25 16:16
# @Author : Natro92
# @Email : natro92@natro92.fun
# @Blog : https://natro92.fun
# @File : Bootstrap
# @Project : SecSec
import os
from colorama import init

from src.Base.args_handler import parse_args
from src.Utils.file_manager import ensure_directory_exists


def bootstrap():
    preparation()
    parse_args()
    pass


def preparation():
    init(autoreset=True)
    pass


def baseline():
    parse_args()
    pass
