import os

from sqlalchemy import create_engine, event
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
    engine = create_engine(database_url, connect_args={"check_same_thread": False})

    # 🚀 تفعيل وضع WAL السحري لتسريع SQLite ومنع التجميد عند تنفيذ أوامر متزامنة
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute(
            "PRAGMA journal_mode=WAL"
        )  # يسمح بالقراءة والكتابة معاً بدون توقف
        cursor.execute("PRAGMA synchronous=NORMAL")  # تسريع الحفظ
        cursor.execute("PRAGMA temp_store=MEMORY")  # استخدام الرام للعمليات المؤقتة
        cursor.close()

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
