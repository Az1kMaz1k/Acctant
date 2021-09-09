import config
import logging
import yadisk

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import callback_query, document, message
from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup
from sqliter import Sqliter

# log level
logging.basicConfig(level=logging.INFO)

# bot init
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

# connection database
db = Sqliter('db.db')

# yadisk connection
ya = yadisk.YaDisk(token = config.ya_TOKEN)

# bot starting
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """This handler will be called when user sends `/start` command"""
    if not (db.check_user(message.from_user.id)):
        db.new_user(message.from_user.id, message.from_user.full_name)
        await message.answer("👋 Привет! "+ message.from_user.full_name +"👋\nЯ твой персональный ассиcтент 🤖\nПеред началом работы необходимо:\nИмя вашей компании(организации) 🏭\nДля хранения ваших документов. 🗂")
    else:
        result = db.get_user(message.from_user.id)
        if result[0][4] == "FALSE":
            await message.answer("C возвращением "+ message.from_user.full_name +"\nПродолжим работу 👋\nПеренесите ваши документы в чат 🗂\nЯ передам их на обработку ✍️")
        else:
            button_all_user = KeyboardButton("Получить список всех клиентов")
            kb1 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_all_user)
            await message.answer("✅ Добро пожаловать Администратор ✅\nЯ добавила для Вас пару командных кнопок 😉\nЧто поможет Вам удобно использовать меня 🤖", reply_markup=kb1)


# catch company_name
@dp.message_handler()
async def catch_company(message: types.Message):
    """This handler will be called when user sends some text"""
    # IF no company name
    if not (db.check_company_name(message.from_user.id)):
        await message.answer("Простите я все лишь ассистен для передачи документов\nЯ не умею ввести диалог 😓")
    else:
        result = db.get_user(message.from_user.id)
        if result[0][4] == "FALSE":
            inline_btn_1 = InlineKeyboardButton('Да', callback_data='button1')
            inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)
            await message.reply("Сохранить имя компании как: " + message.text + "?", reply_markup=inline_kb1)
        else:
            result = db.get_all_user()
            users = []
            for user in result:
                users.append(user[2] + " - компания:" + user[3])

            await message.answer(users)

# add company_name
@dp.callback_query_handler(text="button1")
async def process_callback_button1(call: types.CallbackQuery):
    """This handler will be called when user press button1"""
    company = call.message.text.replace("Сохранить имя компании как: ","")
    company = company.replace("?","")
    # IF Admin
    if company == config.admin_TOKEN:
        db.add_company(company,"TRUE",call.from_user.id)
        button_all_user = KeyboardButton(text="Получить список всех клиентов")
        kb1 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_all_user)
        await call.message.answer("✅ Добро пожаловать Администратор ✅\nЯ добавила для Вас пару командных кнопок 😉\nЧто поможет Вам удобно использовать меня 🤖", reply_markup=kb1)
    # IF user
    else:
        db.add_company(company,"FALSE",call.from_user.id)
        await call.message.answer("✅ Теперь все готово! ✅\nПеренесите ваши документы в чат 🗂\nЯ передам их на обработку ✍️")

# user send document(s)
@dp.message_handler(content_types=message.ContentType.DOCUMENT)
async def send_document(message: types.Message):
    """This handler will be called when user dowloand document (pdf)"""
    result = db.get_user(message.from_user.id)
    if result[0][4] == "FALSE":
        file_id = message.document.file_id
        file_name = message.document.file_name
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, file_name)
        result = db.get_user(message.from_user.id)
        if not (ya.exists("/Для проекта/" + result[0][1] + "_" + result[0][3])):
            ya.mkdir("/Для проекта/" + result[0][1] + "_" + result[0][3])
        if not (ya.exists("/Для проекта/" + result[0][1] + "_" + result[0][3] + "/" + file_name)):
            ya.upload(file_name,"/Для проекта/" + result[0][1] + "_" + result[0][3] + "/" + file_name)
            await message.answer("Документ успешно направлен на обработку ✅\nЕсли хотите направить еще документ,\nЯ всегда к Вашим услугам! 🤖")
        else:
            await message.answer("Такой файл уже существует! ⚠️\nПожалуйста переименуйте имя файла,\nи повторите отправку! 🤖")
    else:
        await message.answer("Прошу прощения Администратор! ⚠️\nУ вас нет возможности загружать файлы! 🤖")

# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)