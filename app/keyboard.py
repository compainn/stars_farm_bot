from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_channels_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📢 Канал 1', url='https://t.me/nsiderNft')],
        #[InlineKeyboardButton(text='📢 Канал 2', url='https://t.me/chaser_luck')],
        [InlineKeyboardButton(text='✅ Я подписался', callback_data='check_subscribe')]
    ])

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='👤 Профиль', callback_data='profile')],
        [InlineKeyboardButton(text='💸 Вывод', callback_data='withdraw')]
    ])


back_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='◀️ назад', callback_data='back_menu')]
])


gift_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🚀 ракета - 50 зв', callback_data='gift_rocket')],
    [InlineKeyboardButton(text='◀️ назад', callback_data='back_menu')]
])


async def get_url_open_chat(user_id):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Перейти к диалогу',
        url=f'tg://openmessage?user_id={user_id}',
    )
    return builder.as_markup()
