from aiogram import Bot
from config import REQUIRED_CHANNELS


async def check_subscriptions(user_id: int, bot: Bot) -> bool:
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(
                chat_id=channel,
                user_id=user_id
            )

            if member.status not in ['member', 'administrator', 'creator']:
                print(f"❌ {user_id} не подписан на {channel} (статус: {member.status})")
                return False

        except Exception as e:
            print(f"⚠️ Ошибка при проверке {user_id} в канале {channel}: {e}")
            return False

    print(f"✅ {user_id} подписан на все каналы")
    return True
