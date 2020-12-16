from asyncio import Lock
from os.path import join
import telegram_bot
import task_data
from utils import *

# This is a module to make custom tasks with the propose of
# save custom variables inside the instance of the task.
PERSISTANCE_DIR = 'persistance'

make_dir_if_not_exists(PERSISTANCE_DIR)

class SpecialFunctionException(Exception):
    pass

class ChatData:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.globals = dict()
        self.lock = Lock()
        self.uri_of_persistance = self.uri_from_chatid()
        self.last_result = None

    def uri_from_chatid(self):
        return join(PERSISTANCE_DIR, str(self.chat_id))

    async def run_function_of_globals(self, name, *args):
        if name not in self.globals.keys():
            raise SpecialFunctionException('Undefined function ' + name)

        function_or_coroutine = self.globals[name]
        return await run_function_or_coroutine(function_or_coroutine, *args)


    async def load_from_file(self):
        # Read the code inside that file. Maybe create a new one.
        code = read_lines_or_create_file(self.uri_of_persistance)

        # We make the bot to shut up meanwhile is loading
        # It's like turn off the prints.
        task_data.get().is_muted = True

        # Fill globals_dict with the execution of code
        exec(code, self.globals)

        # Turn on the prints.
        task_data.get().is_muted = False

        await self.run_function_of_globals('on_post_load_file')

    def add_code(self, newcode):
        # Read the code of the file
        code = read_lines_or_create_file(self.uri_of_persistance)

        # Let's append the newcode
        code = code + '\n\n' + newcode

        # Todo: Maybe change the filename to save backups
        pass

        # Save the file again
        with open(self.uri_of_persistance, "w", encoding='utf-8') as f:
            f.writelines(code)

    # It True iif it could
    def exec_code(self, code):
        try:
            val = eval(code, self.globals)
            task_data.get().result = val
            return True
        except Exception as _:
            try:
                exec(code, self.globals)
                return True
            except Exception as e:
                task_data.get().result = e
                return False

    async def try_execute(self, text, safe_mode):
        if safe_mode:
            if self.exec_code(text):
                self.add_code(text)
            return

        new_text = await self.run_function_of_globals('on_message', text)

        if new_text is not None:
            text = new_text

        if self.exec_code(text):
            self.add_code(text)
        elif text.startswith('/'):
            await self.run_function_of_globals('on_slash_command', text)

        # Let's send a response to the user, or something.
        await self.run_function_of_globals('on_finish')

        # Save the last result
        self.last_result = task_data.get().result