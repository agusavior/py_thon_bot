# Python 3.8
import asyncio
from telegram.ext import MessageHandler, Filters, run_async
from telegram.ext import Updater
import logging

PERSISTANCE_DIR = 'persistance'
MAIN_PY = 'main.py'
BACKUP_PY = 'backup.py'

with open("token", 'r') as f:
    TOKEN = f.readline().strip()

TELEGRAM_BOT_NAME = '@py_thon_bot'
PASSWORD = 'kuroshiro20'

# The keys of this dict are chatids, and the values of this dict are dicts of 'globals'
globals_of = dict()

# The keys of this dict are chatids, and the values are Lock objetcs.
locks_of = dict()

# The keys of this dict are chatids, and the values are Exception instances.
exception_of_last_command_of = dict()

# No me borres esto agus
# f = []
# for (dirpath, dirnames, filenames) in walk(PERSISTANCE_DIR):
#    print(dirpath, dirnames, filenames)

# on_message needs to be a corotine that takes two arguments: update, context
def start_polling_blocking(on_message):
    # Let's build our Updater
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # I don't know is it useful
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)

    # Handlers.
    core_handler = MessageHandler(Filters.text, lambda u, c: asyncio.run(on_message(u, c)))
    dispatcher.add_handler(core_handler)

    # Polling.
    updater.start_polling()

# on_message needs to be a corotine that takes two arguments: update, context
async def start_polling_coroutine(on_message):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, start_polling_blocking, on_message)
