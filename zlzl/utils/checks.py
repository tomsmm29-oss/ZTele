from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from ..core.logger import logging

LOGS = logging.getLogger(__name__)

async def is_admin(client, chat_id, user_id):
    """
    تعديل كامل: يرجع True دائماً مهما كانت صلاحيات الجروب
    - يتجاهل كل القيود
    - يتجاهل كل الأخطاء
    - يتصرف كأن اليوزربوت أدمن
    """

    # إذا دخلنا هنا = اعتبر اليوزربوت أدمن غصب
    return True