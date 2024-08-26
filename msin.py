import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import aiosqlite
import os
import google.generativeai as genai
from aiogram.types import TelegramObject
from aiogram.filters import BaseFilter
import uts_pdf_ai

# использованные токены убраны
token = "MY_TELEGRAM_BOT_TOKEN"

os.environ["GOOGLE_API_KEY"] = "GOOGLE_API_KEY"
genai.configure(api_key = "GOOGLE_API_KEY")

# my telegram id
admin_id = [1111111111] 
class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject) -> bool:
        return obj.from_user.id in admin_id

dp = Dispatcher()

async def add_user(user_id, full_name, username):
    connect = await aiosqlite.connect('chat_log.db')
    cursor = await connect.cursor()
    check_user = await cursor.execute('SELECT * FROM history WHERE user_id = ?', (user_id,))
    check_user = await check_user.fetchone()
    if check_user is None:
        await cursor.execute('INSERT INTO history (user_id, full_name, username) VALUES (?, ?, ?)',
                             (user_id, full_name, username))
        await connect.commit()
    await cursor.close()
    await connect.close()


async def get_user_count():
    connect = await aiosqlite.connect('chat_log.db')
    cursor = await connect.cursor()
    user_count = await cursor.execute('SELECT COUNT(*) FROM history')
    user_count = await user_count.fetchone()
    await cursor.close()
    await connect.close()
    return user_count[0]


admin_keyboard = [
    [
        types.InlineKeyboardButton(text='Статистика', callback_data='admin_statistic')
    ]
]
admin_keyboard = types.InlineKeyboardMarkup(inline_keyboard=admin_keyboard)



@dp.message(Command('start'))
async def hello(message: types.Message) -> None:
    await add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    await message.answer(f'Добрый день, {message.from_user.full_name}\nРад вас видеть!\n'     
                         f'Мне можно задавать вопросы об академических дисциплинах, входящих в специальность «Управление в технических системах».')


@dp.message(Command('admin'), IsAdmin())
async def admin_command(message: types.Message) -> None:
    await message.answer('♪ Добро пожаловать в Админ-панель! ♪'
                         , reply_markup = admin_keyboard)


@dp.callback_query(F.data == 'admin_statistic', IsAdmin())
async def admin_statistic(call: types.CallbackQuery):
    user_count = await get_user_count()
    await call.message.edit_text(f'Взаимодействовали с ботом : {user_count}')


@dp.message()
async def llm_answer(message: types.Message)-> None:
    await message.answer(uts_pdf_ai.pdf_smart_search(message.text))


async def main() -> None:
    bot = Bot(token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bye")

