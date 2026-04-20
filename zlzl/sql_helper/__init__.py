import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# تم إيقاف جلب الرابط من الكونفيج الخارجي لفرض قاعدة البيانات المحلية
# from ..Config import Config 
from ..core.logger import logging

LOGS = logging.getLogger(__name__)


def start() -> scoped_session:
    # التعديل السحري: فرض استخدام قاعدة بيانات محلية (SQLite)
    database_url = "sqlite:///ztele.db"
    
    # check_same_thread=False: مهم جداً لتفادي أخطاء تليثون مع SQLite
    engine = create_engine(database_url, connect_args={'check_same_thread': False})
    
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


try:
    BASE = declarative_base()
    SESSION = start()
except Exception as e:
    LOGS.error(
        "فشل في إعداد قاعدة البيانات المحلية SQLite. قد تواجه بعض الميزات مشاكل."
    )
    LOGS.error(str(e))