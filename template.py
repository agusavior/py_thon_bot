# Template zone:
from task_data import get as td, get_all as tds
import utils

async def on_slash_command(string):
    tdata = td()

    command = string

    assert command.startswith('/')

    command = command[1:]
    command = command.replace('_', ' ')  # Todo: Pensar en borrar

    words = command.split()

    if len(words) == 0:
        return

    function_name = words[0]

    if function_name not in globals():
        return

    # Let's execute 'function'...
    function = globals()[function_name]

    # We will not ignore the errors
    tdata.ignore_errors = False

    try:
        val = await utils.run_function_or_coroutine(function, *words[1:])
    except Exception as e:
        val = e

    # Let's save the 'val' to send to the user
    tdata.result = val


async def on_message(string):
    return string


def on_post_load_file():
    pass


def on_fatal_error(exception):
    print('Fatal error. ' + str(exception))


def on_each_second():
    pass


def on_finish():
    tdata = td()

    result = tdata.result

    if result is None:
        if tdata.is_virgin:
            print('👍 bien')
        else:
            pass  # Nada
    elif isinstance(result, Exception):
        if not tdata.ignore_errors:
            print(str(result))
        else:
            pass  # Nada
    else:
        print(repr(result))


def get_persistance():
    with open(td().chat_data.uri_of_persistance, "r") as f:
        return f.read()

# End of template zone
