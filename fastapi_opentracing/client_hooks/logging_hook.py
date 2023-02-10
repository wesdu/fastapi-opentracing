import logging
from fastapi_opentracing import sync_get_current_span
_logging_log = logging.Logger._log

ERROR = "ERROR"
WARNING = "WARNING"
INFO = "INFO"
DEBUG = "DEBUG"

error_level = [ERROR]

def _logging_wrapper(self, level, msg, args, exc_info=None, extra=None, stack_info=False,
             stacklevel=1):
    _logging_log(self, level, msg, args, exc_info, extra, stack_info, stacklevel)
    
    level_name = logging._levelToName.get(level)
    if level_name in error_level:
        parent_span = sync_get_current_span()
        if parent_span is not None:
            parent_span.set_tag(key="error", value="yes")
            parent_span.log_kv({"event": "error", "message": msg, "level": level_name})

def install_patch():
    logging.Logger._log = _logging_wrapper