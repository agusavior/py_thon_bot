import inspect
import os.path
import threading

TEMPLATE_URI = 'template.py'

with open(TEMPLATE_URI, 'r', encoding="utf8") as f:
    TEMPLATE_TEXT = f.read()


async def run_function_or_coroutine(function_or_coroutine, *args):
    # Maybe this function is a coroutine (When the function starts with 'async ')
    iscoroutine = inspect.iscoroutinefunction(function_or_coroutine)

    if iscoroutine:
        return await function_or_coroutine(*args)
    else:
        return function_or_coroutine(*args)


def read_lines_or_create_file(uri):
    if not os.path.exists(uri):
        # Create a file from template
        with open(uri, 'w+', encoding="utf8") as f:
            f.write(TEMPLATE_TEXT)

    with open(uri, "r", encoding="utf8") as f:
        return f.read()


def make_dir_if_not_exists(dirname):
    try:
        # Create target Directory
        os.mkdir(dirname)
    except:
        pass


# Un-used but maybe useful
def th_id():
    return threading.current_thread().ident
