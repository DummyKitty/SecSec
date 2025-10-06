# _*_ coding : utf-8 _*_
# @Time: 2025/4/25 16:04
# @Author : Natro92
# @Email : natro92@natro92.fun
# @Blog : https://natro92.fun
# @File : secsec
# @Project : SecSec
import os
from src.Base.args_handler import parse_args
from src.Base.bootstrap import bootstrap

# 检查是否禁用 Gooey
if os.environ.get('DISABLE_GOOEY', '').lower() == '1':
    # 不使用 Gooey，直接运行
    def main():
        bootstrap()
else:
    # 使用 Gooey
    try:
        from gooey import Gooey
    except Exception:
        Gooey = lambda **kwargs: (lambda f: f)

    @Gooey(program_name="SecSec", optional_cols=1, default_size=(900, 700))
    def main():
        bootstrap()

if __name__ == '__main__':
    main()
