import asyncio
import sys
import traceback
from typing import List

import telegram

# This is a module to make custom tasks with the propose of
# save custom variables inside the instance of the task.

OK_RESULT = '👍 bien'


class TaskData:
    def __init__(self):
        self.result = None
        self.chat_id = None
        self.is_muted = False
        self.root_message_id = None
        self.is_virgin = True
        self.ignore_errors = True
        self.bot = None
        self.disable_notifications = True
        self.timeout = 60
        self.chat_data = None
        self.meta_globals = None
        self.telegram_message = None

    def send_message(self, text):
        self.bot.send_message(chat_id=self.chat_id,
                              text=text[:telegram.constants.MAX_MESSAGE_LENGTH],
                              reply_to_message_id=self.root_message_id,
                              disable_notification=self.disable_notifications,
                              # parse_mode='HTML',
                              timeout=self.timeout
                              )

        # This means that this task has used at least one send_message
        self.is_virgin = False

def get() -> TaskData:
    return __get_task_att('__data')

def get_all() -> List[TaskData]:
    task_datas = []
    tasks = asyncio.all_tasks()
    for t in tasks:
        if hasattr(t, '__data'):
            task_datas.append(getattr(t, '__data'))
    return []

def __get_task_att(attname):
    task = asyncio.current_task()
    if hasattr(task, attname):
        return getattr(task, attname)
    else:
        return None


def __set_task_att(task, attname, value):
    setattr(task, attname, value)


messages_pending_to_send: List[str] = []


class TaskDataLogger:
    def __init__(self, console_stdout):
        self.line = ""
        self.console_stdout = console_stdout

    def write(self, text):
        if text == '\n':
            self.println(self.line)
            self.line = ''
            return

        self.line += text

    def flush(self):
        self.console_stdout.flush()

    def println(self, text):
        tdata = get()

        # Shortcut Console write
        def cwrite(string):
            self.console_stdout.write(string)

        if tdata == None:
            # This means that we are outside a custom task, so
            # let's use the console stdout
            cwrite('Non custom task > ')
            cwrite(text)
            cwrite('\n')
            return

        cwrite('tdataid={} chatid={} > '.format(id(tdata), tdata.chat_id))
        cwrite(text)
        cwrite('\n')

        if tdata.is_muted or tdata.bot is None or tdata.chat_id is None:
            return

        if text == '':
            return  # Todo: ¿Esto es correcto?

        try:
            tdata.send_message(text)
        except Exception as e:
            cwrite('Last text wasn\'t sended for the next reason: ')
            cwrite(traceback.format_exc())
            cwrite('\n')


def start_using_task_data_logger():
    sys.stdout = TaskDataLogger(sys.stdout)


def stop_using_task_data_logger():
    raise Exception('TODO')


# Create a new task, and run it, with a TaskData object inside.
# So, inside this execution of the task, you can use 'task_data.get()' to
# get the TaskData instance.
def create_task(coro):
    task = asyncio.create_task(coro)

    # Let's create a new instance of TaskData and attach it to the task
    __set_task_att(task, '__data', TaskData())

    return task
