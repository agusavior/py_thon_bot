# Python 3.8
import asyncio
import traceback

from typing import Dict

from chat_data import ChatData
import telegram_bot

import task_data

ALLOWED_USER_IDS = {
    680640473,
    43759228
}

# The keys of this dict are chatids, and the values of this dict are dicts of 'globals'
chat_data_of: Dict[int, ChatData] = dict()

# The allowed user ids
allowed_user_ids = ALLOWED_USER_IDS

async def on_message(update, context):
    # Auth
    if update.effective_user.id not in allowed_user_ids:
        print('Acceso denegado para usuario: ', update.effective_user.id)
        return

    # Shortcuts
    bot = context.bot
    message = update.message
    text = message.text
    chat_id = update.effective_chat.id

    # Finish if text is empty, or the message is an image or something weird.
    if text is None:
        return

    # Let's bind owr task with the information to
    # send messages in every 'print'
    tdata = task_data.get()
    tdata.bot = bot
    tdata.chat_id = chat_id
    tdata.root_message_id = message.message_id

    if chat_id not in chat_data_of:
        # Create and load chat data...
        chat_data = ChatData(chat_id)
        chat_data_of[chat_id] = chat_data
        await chat_data.load_from_file()

    # Get our chat data
    chat_data = chat_data_of[chat_id]

    # Save the chat data inside the task data
    tdata.chat_data = chat_data

    # Get the Lock object of this chat
    lock = chat_data.lock

    # Acquire... let's wait until the lock release
    await lock.acquire()
    try:
        if text.startswith('"') and text.endswith('"'):
            # Only ram mode. Safe mode.
            text = text[1:-1]

            await chat_data.try_execute(text, True)
        else:
            # Now, let's try to execute the text
            await chat_data.try_execute(text, False)
    except Exception as e:
        traceback.print_exc()

        await chat_data.run_function_of_globals('on_fatal_error', e)
    finally:
        lock.release()


async def __on_message(update, context):
    await task_data.create_task(on_message(update, context))


async def loop():
    while True:
        await asyncio.sleep(1)

        # TODO:
        #for chat_data in chat_data_of.values():
        #    await chat_data.run_function_of_globals('on_each_second')


async def main():
    # Start to using a custom 'print' function...
    task_data.start_using_task_data_logger()

    task = task_data.create_task(loop())

    # Start to listen bot messages
    # And in every message received, runs 'on_message'
    await telegram_bot.start_polling_coroutine(__on_message)

    # I think it is not necessary
    await task


if __name__ == '__main__':
    asyncio.run(main())
