import logging
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.markdown import html_decoration as fmt
from config import token

logging.basicConfig(level=logging.INFO)

logging.info("Initializing bot")
bot = Bot(token=token)
dp = Dispatcher()

request_url = 'https://24.kg/?!'
initial_delay = 0
interval = 60

async def perform_request():
    global request_url
    async with aiohttp.ClientSession() as session:
        try:
            logging.info(f"Performing request to {request_url}")
            async with session.get(request_url) as response:
                response_text = await response.text()
                logging.info(f"Success: {response.status} - {response_text[:100]}...")  # Log first 100 chars
        except aiohttp.ClientError as e:
            logging.error(f"Error during request: {e}")

async def schedule_tasks():
    await asyncio.sleep(initial_delay)
    while True:
        await perform_request()
        await asyncio.sleep(interval)

@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот для выполнения HTTP-запросов с заданной периодичностью. Используйте команды /set_url, /set_initial_delay и /set_interval для настройки.")

@dp.message(Command(commands=["set_url"]))
async def set_url(message: Message):
    global request_url
    try:
        request_url = message.text.split(' ')[1]
        await message.answer(f"URL установлен на: {fmt.quote(request_url)}")
    except IndexError:
        await message.answer("Не указан URL. Используйте команду в формате: /set_url <URL>")

@dp.message(Command(commands=["set_initial_delay"]))
async def set_initial_delay(message: Message):
    global initial_delay
    try:
        initial_delay = int(message.text.split('')[1])
        await message.answer(f"Начальная задержка установлена на: {initial_delay} секунд")
    except (IndexError, ValueError):
        await message.answer("Не указана задержка. Используйте команду в формате: /set_initial_delay <seconds>")

@dp.message(Command(commands=["set_interval"]))
async def set_interval(message: Message):
    global interval
    try:
        interval = int(message.text.split('')[1])
        await message.answer(f"Интервал между запросами установлен на: {interval} секунд")
    except (IndexError, ValueError):
        await message.answer("Не указан интервал. Используйте команду в формате: /set_interval <seconds>")

async def main():
    logging.info("Starting main function")
    asyncio.create_task(schedule_tasks())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.info("Running main")
    asyncio.run(main())

