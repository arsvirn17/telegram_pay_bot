from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

btnTopUp = InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up") # Кнопка "Пополнить Баланс"
topUpMenu = InlineKeyboardMarkup(row_width=1)
topUpMenu.insert(btnTopUp)

def buy_menu (isUrl=True, url="", bill=""):
    qiwiMenu = InlineKeyboardMarkup(row_width=1)
    if isUrl:
        btnUrlQIWI = InlineKeyboardButton(text="Ссылка на оплату", url=url) # Кнопка "Ссылка на оплату"
        qiwiMenu.insert(btnUrlQIWI)

    btnCheckQIWI = InlineKeyboardButton(text="Проверить оплату", callback_data="check_"+bill) # Кнопка "Проверить оплату"
    qiwiMenu.insert(btnCheckQIWI)
    return qiwiMenu

ikb_menu = InlineKeyboardMarkup(row_width=1,
                                inline_keyboard=[
                                    [
                                        InlineKeyboardButton(text="Показать пользователей с их балансом", callback_data="1") # Кнопка "Показать пользователей с их балансом"
                                    ],
                                    [
                                        InlineKeyboardButton(text="Показать логи", callback_data="2")
                                    ]
                                    # [
                                    #     InlineKeyboardButton(text="Кнопка 3", callback_data="3")
                                    # ],
                                    # [
                                    #     InlineKeyboardButton(text="Кнопка 4", callback_data="4")
                                    # ]
                                ])