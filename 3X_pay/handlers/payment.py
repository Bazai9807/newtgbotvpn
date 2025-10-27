from bot.handlers.start import my_vpn_handler
from bot.keyboards.user import user_main_keyboard


# В функции обработки успешного платежа добавьте:
@router.callback_query(F.data.startswith("payment_success"))
async def payment_success_handler(callback: CallbackQuery, session: AsyncSession):
    try:
        # ... существующий код обработки платежа ...

        # После успешной обработки платежа показываем меню /my_vpn
        await callback.message.edit_text(
            "✅ Оплата прошла успешно! Ваша подписка активирована.",
            reply_markup=user_main_keyboard()
        )

        # Или альтернативный вариант - напрямую вызываем my_vpn_handler
        await my_vpn_handler(callback.message, session)

    except Exception as e:
        logger.error(f"Error in payment success: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при активации подписки. Обратитесь к администратору."
        )