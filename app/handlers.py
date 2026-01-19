from aiogram import F, Router
from aiogram import Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
import app.keyboard as kb
import app.database.requests as rq
from app.services.subscription import check_subscriptions
from config import INVITE_PRIZE, FIRST_PRIZE, ADMIN_ID, MIN_WITHDRAW, GIFTS

router = Router()

@router.message(Command('start'))
async def start_handler(message: Message):
    args = message.text.split()
    inviter_id = int(args[1]) if len(args) > 1 else None

    user = await rq.set_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        inviter_id=inviter_id
    )

    await message.answer(
        "📢 <b>Подпишитесь на наши каналы чтобы получить бонус!</b>",
        parse_mode='HTML',
        reply_markup=kb.get_channels_kb()
    )

@router.callback_query(F.data == "check_subscribe")
async def check_subscription(callback: CallbackQuery, bot: Bot):
    is_subscribed = await check_subscriptions(callback.from_user.id, bot)

    if not is_subscribed:
        await callback.answer(
            "❌ Вы не подписаны на все каналы!",
            show_alert=True
        )
        return

    user = await rq.get_user(callback.from_user.id)

    if user and user.balance == 0:
        await rq.add_stars(user.tg_id, FIRST_PRIZE)
        user.balance = FIRST_PRIZE

        if user.invited_by:
            inviter = await rq.get_user(user.invited_by)
            if inviter:
                try:
                    await bot.send_message(
                        inviter.tg_id,
                        f"<b>Пользователь @{user.username or 'без имени'} "
                        f"перешел по вашей реферальной ссылке</b>\n\n"
                        f"<b>Вам начислено:</b> {INVITE_PRIZE} ⭐\n",
                        parse_mode='HTML'
                    )
                except Exception as e:
                    print(f"Не удалось отправить уведомление пригласившему {inviter.tg_id}: {e}")

    ref_link = f"https://t.me/RefEmpie_Bot?start={callback.from_user.id}"

    await callback.message.edit_text(
        f"✅ <b>Отлично! Вы подписаны на все каналы!</b>\n\n"
        f"<i>Приглашайте друзей и получайте {INVITE_PRIZE} звезды за каждого!</i>",
        parse_mode='HTML',
        reply_markup=kb.main_menu()
    )

    await callback.answer()

@router.callback_query(F.data == 'profile')
async def profil(callback: CallbackQuery):
    user = await rq.get_user(callback.from_user.id)
    ref_link = f"https://t.me/RefEmpie_Bot?start={callback.from_user.id}"
    await callback.message.edit_text(f'👤 профиль @{user.username}\n\n'
                                     f'приглашено пользователей: {user.referrals_count}\n\n'
                                     f'<b>баланс:</b> <code>{user.balance}</code> ⭐\n\n'
                                     f'<b>реферальная ссылка:\n</b><code>{ref_link}</code>\n\n'
                                     f'<b>заявок в рассмотрении:</b> <code>{user.active_requests}</code>\n\n'
                                     f'<i>Получайте по {INVITE_PRIZE} ⭐ за каждого приглашенного пользователя, который подпишется на все каналы</i>'
    , reply_markup=kb.back_menu, parse_mode='HTML')

@router.callback_query(F.data == 'back_menu')
async def back_menu(callback: CallbackQuery):
    await callback.message.edit_text("Главное меню", reply_markup=kb.main_menu())

@router.callback_query(F.data == 'withdraw')
async def withdraw(callback: CallbackQuery):
    user = await rq.get_user(callback.from_user.id)

    if not user:
        await callback.answer("❌ Ошибка", show_alert=True)
        return

    if user.balance < MIN_WITHDRAW:
        await callback.answer(
            f"❗ Минимум для вывода: {MIN_WITHDRAW} ⭐\nВаш баланс: {user.balance} ⭐",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        "<b>Выберите подарок:\n<i>не забудьте установить юзернейм!</i>\n<i>иначе вывод не будет осуществлен!</i></b>",
        reply_markup=kb.gift_list,
        parse_mode='HTML'
    )

@router.callback_query(F.data.startswith("gift_"))
async def choose_gift(callback: CallbackQuery):
    user = await rq.get_user(callback.from_user.id)

    if not user:
        await callback.answer("❌ Ошибка", show_alert=True)
        return

    user_id = callback.from_user.id
    gift_type = callback.data.split('_')[1]

    if gift_type not in GIFTS:
        await callback.answer("❌ Неизвестный подарок", show_alert=True)
        return

    gift = GIFTS[gift_type]

    if user.balance < gift['price']:
        await callback.answer(
            f"❌ Недостаточно звезд!\nНужно: {gift['price']} ⭐",
            show_alert=True
        )
        return

    await rq.increment_active_requests(user.tg_id)
    await rq.add_stars(user.tg_id, -gift['price'])

    await callback.bot.send_message(
        ADMIN_ID,
        f"<b>Пользователь @{callback.from_user.username} id: <code>{callback.from_user.id}</code> оставил заявку на вывод подарка:</b>\n\n"
        f"<code>{gift['name']}</code>\n\n"
        f"<code>/close_request {callback.from_user.id}</code>",
        reply_markup=await kb.get_url_open_chat(user_id),
        parse_mode='HTML'
    )

    await callback.message.edit_text(
        f"✅ <b>Заявка создана!</b>\n\n"
        f"<b>Подарок:</b> {gift['name']}\n\n"
        f"<b>Активных заявок:</b> {user.active_requests + 1}\n\n"
        f"<i>Админ получил уведомление.\n"
        f"Ожидайте рассмотрения!</i>",
        parse_mode='HTML',
        reply_markup=kb.main_menu()
    )

    await callback.answer()

@router.message(Command('close_request'))
async def close_request(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) == 2:
        user_id = int(parts[1])
        await rq.decrement_active_requests(user_id)
        await message.answer(f"✅ Заявка пользователя {user_id} закрыта")
    else:
        await message.answer("Использование: /close_request user_id")
