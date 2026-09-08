import importlib.util
import sys
from pathlib import Path

from ..core.logger import logging

LOGS = logging.getLogger(__name__)


def load_module(shortname, plugin_path=None):
    if shortname.startswith("__"):
        return
    try:
        if plugin_path is None:
            path = Path(f"zlzl/plugins/{shortname}.py")
            name = f"zlzl.plugins.{shortname}"
        else:
            path = Path(f"{plugin_path}/{shortname}.py")
            name = f"{plugin_path.replace('/', '.')}.{shortname}"

        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules[name] = mod
        LOGS.info(f"تم تحميل الملف: {shortname}")
    except Exception as e:
        LOGS.error(f"خطأ في تحميل {shortname}: {e}")


def remove_plugin(shortname):
    name = f"zlzl.plugins.{shortname}"
    if name in sys.modules:
        del sys.modules[name]
