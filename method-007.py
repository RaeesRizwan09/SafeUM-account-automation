from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from concurrent.futures import ThreadPoolExecutor
from os import system, name
from random import choice, choices
from ssl import CERT_NONE
from gzip import decompress
from json import dumps
import threading
import asyncio
import os

try:
    from websocket import create_connection
except ImportError:
    system('pip install websocket-client')
    from websocket import create_connection

API_TOKEN = '7252751093:AAEudeFLbSbcDEH6oRGjBqpwvFVjN9ZPYB4'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

def work(user_id):
    global user_data
    username = choice('qwertyuioplkjhgfdsazxcvbnm') + ''.join(choices(list('qwertyuioplkjhgfdsazxcvbnm1234567890'), k=12))
    try:
        con = create_connection(
            "wss://193.200.173.45/Auth",
            header={
                "app": "com.safeum.android",
                "host": None,
                "remoteIp": "193.200.173.45",
                "remotePort": str(8080),
                "sessionId": "b6cbb22d-06ca-41ff-8fda-c0ddeb148195",
                "time": "2023-04-30 12:13:32",
                "url": "wss://51.79.208.190/Auth"
            },
            sslopt={"cert_reqs": CERT_NONE}
        )
        con.send(dumps({
            "action": "Register",
            "subaction": "Desktop",
            "locale": "en_IN",
            "gmt": "+05",
            "password": {
                "m1x": "aefb63e82a28d0f7864c9162e97014e062e2d82961a2cfdfa2d795ebe597cbd0",
                "m1y": "36708d26797e41be1528c777db8d2679f2bc26f2356798e499f4004f5e119a88",
                "m2": "4b03e693bff7381edb8d81687f0daf7ab2291258cb28eb3200c0db7870a6a91c",
                "iv": "a924eefd30f6138eb47a1e500e1f0e9b",
                "message": "4caf0b1bf8d2f9e8da57069ce4aed5013d0c745bdbfa0ff59bf43e6d2f1b0c88fd979c155529348bdbf3baabd1ff8669d50613c260918a6f93ab5d576779795ac13dd4804f42198b2866d1467dced3b1"
            },
            "magicword": {
                "m1x": "d20e90d862a1a3c73687ba5fdc3523d5b59b9143c5e0f62321b46e69ec6a96f6",
                "m1y": "a17a92e1eb880ff3432f98d9dc7fc16a0f59e906c85ef1dd690a6585196b082b",
                "m2": "0bdc3b308d3e224127594e53864a714ece879d846a74196835b2b7554eda73ad",
                "iv": "bb3ee985ea37262ef61f1b3db7fbbede",
                "message": "6fcb86db8feea00fc0d46ca1c9590b74"
            },
            "magicwordhint": "0000",
            "login": str(username),
            "devicename": "Xiaomi 23128PC33I",
            "softwareversion": "1.1.0.2300",
            "nickname": "rqhi9wb8er8jw5",
            "os": "AND",
            "deviceuid": "5f8d62999fe0bd86",
            "devicepushuid": "*eB6Q8j1TSUCg-Xz8cOnqbG:APA91bHBo1vUF4B_b6ohA7aNshKALxlhPztOxtOAxYgB1rvs1n45KPmCysnJmUKRG46UKNB9wUXJuk34AXsNKr0Q_lYsbhyleeTuFFrSq2P_SOGFjcOy1D6kRXpDeMsyhueqz6R9aEue",
            "osversion": "and_13.0.0",
            "id": "364651978"
        }))
        gzip = decompress(con.recv()).decode('utf-8')
        if '"status":"Success"' in gzip:
            user_data[user_id]['success'] += 1
            user_data[user_id]['accounts'].append(username + ':aaaa')
            with open(f'accounts_{user_id}.txt', 'a') as f:
                f.write(username + ":aaaa | TG : @RAEES SAHIB\n")
        else:
            user_data[user_id]['failed'] += 1
    except:
        user_data[user_id]['retry'] += 1

def start_work_process(user_id):
    global user_data
    if user_data[user_id]['executor'] is None:
        user_data[user_id]['executor'] = ThreadPoolExecutor(max_workers=1000)
    while not user_data[user_id]['stop_event'].is_set():
        user_data[user_id]['executor'].submit(work, user_id)
        system("cls" if name == "nt" else "clear")

async def send_status_update(user_id):
    while not user_data[user_id]['stop_event'].is_set():
        if user_data[user_id]['status_message_id'] and user_data[user_id]['status_chat_id']:
            try:
                await bot.edit_message_text(
                    chat_id=user_data[user_id]['status_chat_id'],
                    message_id=user_data[user_id]['status_message_id'],
                    text=f"Success: {user_data[user_id]['success']}\nFailed: {user_data[user_id]['failed']}\nRetry: {user_data[user_id]['retry']}"
                )
            except:
                pass
        await asyncio.sleep(5)

@dp.message_handler(commands=['start_process'])
async def start_process(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {
            'stop_event': threading.Event(),
            'executor': None,
            'success': 0,
            'failed': 0,
            'retry': 0,
            'accounts': [],
            'status_message_id': None,
            'status_chat_id': None
        }
    user_data[user_id]['stop_event'].clear()
    status_message = await message.answer(f"Success: {user_data[user_id]['success']}\nFailed: {user_data[user_id]['failed']}\nRetry: {user_data[user_id]['retry']}")
    user_data[user_id]['status_message_id'] = status_message.message_id
    user_data[user_id]['status_chat_id'] = status_message.chat.id
    threading.Thread(target=start_work_process, args=(user_id,)).start()
    asyncio.create_task(send_status_update(user_id))
    await message.reply("The process has started.")

@dp.message_handler(commands=['stop_process'])
async def stop_process(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]['stop_event']:
        user_data[user_id]['stop_event'].set()
        with open(f'accounts_{user_id}.txt', 'w') as f:
            f.write("\n".join(user_data[user_id]['accounts']))
        with open(f'accounts_{user_id}.txt', 'rb') as f:
            await message.reply_document(f)
        await message.reply("The process has been stopped.")

@dp.message_handler(commands=['start'])
async def show_menu(message: types.Message):
    menu_text = ("Welcome to the SafeUM Terminator bot!\n\n"
                 "This bot helps you get SafeUM account easily without using any other tool or python script.\n"
                 "Credits: @RAEES_SAHIB\n\n"
                 "Use the buttons below to start or stop the process.")
    start_button = InlineKeyboardButton("Start", callback_data="start_process")
    stop_button = InlineKeyboardButton("Stop", callback_data="stop_process")
    menu_markup = InlineKeyboardMarkup().add(start_button, stop_button)
    await message.reply(menu_text, reply_markup=menu_markup)

@dp.callback_query_handler(lambda c: c.data in ["start_process", "stop_process"])
async def process_callback(callback_query: types.CallbackQuery):
    command = callback_query.data
    if command == "start_process":
        await start_process(callback_query.message)
    elif command == "stop_process":
        await stop_process(callback_query.message)
    await bot.answer_callback_query(callback_query.id)

@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(message.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
