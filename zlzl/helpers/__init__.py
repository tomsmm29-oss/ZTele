from . import fonts
from .aiohttp_helper import AioHttp
from .utils import *

flag = True
# تعديل مايكي: غيرنا الاسم من check إلى retry_count عشان ما يصير تضارب
retry_count = 0

while flag:
    try:
        from .chatbot import *
        from .functions import *
        from .memeifyhelpers import *
        from .progress import *
        from .qhelper import process
        from .tools import *
        from .utils import _format, _zedtools, _zedutils

        break
    except ModuleNotFoundError as e:
        install_pip(e.name)
        # هنا التعديل: نزيد العداد الجديد
        retry_count += 1
        if retry_count > 5:
            break
