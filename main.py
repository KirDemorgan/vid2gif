import asyncio
import random
import os
import subprocess
import string
import shutil

from xdd import TOKEN

from aiogram.types import FSInputFile
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.filters import CommandStart

bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher()

MAX_FILE_SIZE_MB = 25

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Отправьте мне видео .mp4 для получения .gif")

@dp.message()
async def handler(message: Message):
    attach = message.document
    if not attach:
        if message.video:
            attach = message.video
        else:
            return

    if attach.file_name.endswith(".mp4"):
        file_name = attach.file_name
        file_size_mb = attach.file_size / \
            (1024 * 1024)  # Размер файла в мегабайтах

        if file_size_mb <= MAX_FILE_SIZE_MB:
            random_letters = ''.join(random.choice(
                string.ascii_letters) for _ in range(8))

            temp_dir = f'temp-{random_letters}'

            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            file_path = os.path.join(temp_dir, file_name)

            file_id = attach.file_id
            file = await bot.get_file(file_id)
            xdd = file.file_path

            await bot.download_file(xdd, destination=file_path)

            gif_file_name = f'demorgan_bot{random_letters}.gif'
            gif_file_path = os.path.join(temp_dir, gif_file_name)
            command = f'ffmpeg -i "{file_path}" "{gif_file_path}"'

            try:
                subprocess.run(command, shell=True, check=True)

                if os.path.getsize(gif_file_path) / (1024 * 1024) <= MAX_FILE_SIZE_MB:
                    gif = FSInputFile(
                        gif_file_path, filename="gif_name.gif")
                    await message.answer_animation(animation=gif)
                    await message.answer(f'{message.from_user.first_name} gif created!')
                    await message.answer_document(document=gif, disable_content_type_detection=True)

                else:
                    await message.answer(f'{message.from_user.first_name} Файл слишком большой. Попробуйте уменьшить качество исходного видео.')
            except subprocess.CalledProcessError:
                await message.answer('Произошла ошибка при создании .gif')
            finally:
                os.remove(file_path)
                os.remove(gif_file_path)
                shutil.rmtree(temp_dir)

        else:
            await message.answer(f"Пожалуйста, прикрепите .mp4 файл для создания .gif.")

async def main():
    print("Бот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
