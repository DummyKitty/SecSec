# _*_ coding : utf-8 _*_
# @Time: 2025/4/25 17:23
# @Author : Natro92
# @Email : natro92@natro92.fun
# @Blog : https://natro92.fun
# @File : file_manager
# @Project : SecSec
import os

from config import FILE_SAVE_PATH

# 添加缓存集合记录已检查过的目录
_checked_directories = set()


def is_image_folder_created(folder_name, base_path=None):
    """
    判断图片文件夹是否创建
    :param folder_name: 文件夹名称 (如 'freebuf', 'xianzhi', 'butian')
    :param base_path: 基础保存路径，如果为None则使用配置文件中的路径
    :return:
    """
    if base_path is None:
        base_path = FILE_SAVE_PATH
    
    images_path = os.path.join(base_path, folder_name, 'images')
    
    if not os.path.exists(images_path):
        try:
            os.makedirs(images_path, exist_ok=True)
            print(f"[*] Info - 已创建 {folder_name} 图片目录: {images_path}")
        except OSError as e:
            print(f"[!] Error - 创建 {folder_name} 图片目录失败: {images_path}, 错误: {e}")
            raise


def ensure_directory_exists(path):
    """
    确保目标路径的所有目录都存在，如果不存在则递归创建
    添加缓存标识，避免重复检查和创建相同的目录
    :param path: 目标路径（可以是文件路径或目录路径）
    """
    directory = os.path.dirname(path)  # 获取目录部分

    # 如果目录已经检查过，直接返回
    if directory in _checked_directories:
        return

    # 添加到已检查集合
    _checked_directories.add(directory)

    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)  # 递归创建所有缺失的目录
            print(f"目录已创建: {directory}")
        except OSError as e:
            print(f"创建目录失败: {directory}, 错误: {e}")
    elif directory:
        print(f"目录已存在: {directory}")
    else:
        print("目标路径为当前目录，无需创建")
