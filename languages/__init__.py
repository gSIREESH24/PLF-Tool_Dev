from .python_lang import run as python_run
from .js_lang import run as js_run
from .c_lang import run as c_run

LANGUAGE_REGISTRY = {
    "python": python_run,
    "javascript": js_run,
    "c": c_run
}
