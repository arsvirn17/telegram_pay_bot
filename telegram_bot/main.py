import logging
from aiogram import Bot, Dispatcher, executor, types 
import random
from aiogram.dispatcher.filters.state import StatesGroup, State

import config as cfg 
import markups as nav
from db import Database
from pyqiwip2p import QiwiP2P

logging.basicConfig(level=logging.INFO)

bot = Bot(token=cfg.TOKEN)
dp = Dispatcher(bot)

db = Database("database.db") # Подключение SQLite Database
p2p = QiwiP2P(auth_key=cfg.QIWI_TOKEN)


def is_number(_str): # Проверка сообщения (число или нет)
    try:
        int(_str)
        return True
    except ValueError:
        return False

@dp.message_handler(commands=['start']) 
async def start(message: types.Message): # Ответ на команду /start
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id)

        await bot.send_message(message.from_user.id, f"Привет, {message.from_user.full_name}\nЯ - бот для пополнения баланса.\nНажмите на кнопку, чтобы пополнить баланс", reply_markup=nav.topUpMenu)

@dp.message_handler(commands=['admin'])
async def admin(message: types.Message): # Ответ на команду /admin
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id)

        await bot.send_message(message.from_user.id, "Вы вошли в панель админа", reply_markup=nav.ikb_menu)

banned_users = int() # id заблокированого пользователя

@dp.message_handler(user_id=banned_users) 
async def handle_banned(message: types.Message): # Блокирование пользователя
    print(f"{message.from_user.full_name} пишет, но мы ему не ответим!")
    return True

@dp.message_handler()
async def bot_mess(message: types.Message): # Создание счёта qiwi
    if message.chat.type == "private":
        a = message.text
        db.add_block_user(a)
        if is_number(message.text):
            message_money = int(message.text)
            if message_money >= 5:
                comment = str(message.from_user.id) + "_" + str(random.randint(1000, 9999))
                bill = p2p.bill(amount=message_money, lifetime=5, comment=comment)

                db.add_check(message.from_user.id, message_money, bill.bill_id)

                await bot.send_message(message.from_user.id, f"Вам нужно отправить {message_money} руб. на счёт QIWI\nСсылку: {bill.pay_url}\nУказав комментарий к оплате: {comment}", reply_markup=nav.buy_menu(url=bill.pay_url, bill=bill.bill_id))
            else:
                await bot.send_message(message.from_user.id, "Минимальная сумма для пополнения 5 руб.")
        else: 
            await bot.send_message(message.from_user.id, "Введите целое число")

@dp.callback_query_handler(text="top_up")
async def top_up(callback: types.CallbackQuery): # Обработка клика кнопки "Пополнить баланс"
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await bot.send_message(callback.from_user.id, "Введите сумму, на которую вы хотите пополнить баланс")

@dp.callback_query_handler(text="1") 
async def show_users(callback: types.CallbackQuery): # Обработка клика кнопки "Показать пользователей и их баланс"
    await bot.send_message(callback.from_user.id, str(db.get_koll()))

@dp.callback_query_handler(text="2") 
async def show_logs(callback: types.CallbackQuery): # Обработка клика кнопки "Показать логи"
    await bot.send_message(callback.from_user.id, str(db.get_block()))

@dp.callback_query_handler(text_contains="check_") 
async def check(callback: types.CallbackQuery): # Проверка оплаты
    bill = str(callback.data[6:])
    info = db.get_check(bill)
    if info != False:
        if str(p2p.check(bill_id=bill).status) == "PAID":
            user_money = db.user_money(callback.from_user.id)
            money = int(info[2])
            db.set_money(callback.from_user.id, user_money+money)
            await bot.send_message(callback.from_user.id, "Ваш счёт пополнен! Напишите /start")

        else:
            await bot.send_message(callback.from_user.id, "Вы не оплатили счёт!", reply_markup=nav.buy_menu(False, bill=bill))
    else:
        await bot.send_message(callback.from_user.id, "Счёт не найден")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates = True)