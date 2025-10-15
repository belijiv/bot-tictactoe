import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from settings import settings
from game.session_manager import GameSessionsManager
from keyboards import create_game_keyboard

bot = Bot(token=settings['TOKEN'])
dp = Dispatcher()
router = Router()
dp.include_router(router)

session_manager = GameSessionsManager()

user_game_messages = {}


@router.message(Command('start'))
async def start_handler(msg: Message):
    await msg.answer(
        '🎮 Добро пожаловать в крестики-нолики!\n'
        '\n'
        '▶️ Для начала игры используйте /play'
    )


@router.message(Command('play'))
async def play_handler(msg: Message):
    user_id = msg.from_user.id
    game_id = session_manager.add_to_queue(user_id)

    if game_id:
        game = session_manager.get_game(game_id)
        symbol = '❌' if user_id == game.player_x else '⭕'

        message = await msg.answer(
            f'Игра найдена!\nВаш символ: {symbol}\n'
            f'Текущий ход: ❌\nID игры: {game_id}',
            reply_markup=create_game_keyboard(game_id)
        )

        user_game_messages[user_id] = message.message_id

        opponent_id = game.player_o if user_id == game.player_x else game.player_x
        opponent_symbol = '⭕' if user_id == game.player_x else '❌'

        try:
            opponent_message = await bot.send_message(
                opponent_id,
                f'Игра найдена!\nВаш символ: {opponent_symbol}\n'
                f'Текущий ход: ❌\nID игры: {game_id}',
                reply_markup=create_game_keyboard(game_id)
            )
            user_game_messages[opponent_id] = opponent_message.message_id

        except Exception as e:
            await msg.answer('Ошибка при уведомлении противника')
            print(f'Error notifying opponent: {e}')
    else:
        await msg.answer(
            '⏳ Ожидаем второго игрока...\n'
            'Для отмены поиска используйте /cancel'
        )


@router.message(Command('cancel'))
async def cancel_handler(msg: Message):
    user_id = msg.from_user.id
    if session_manager.remove_from_queue(user_id):
        await msg.answer('❌ Поиск игры отменен')
    else:
        await msg.answer('❌ Вы не ищете игру')


@router.callback_query(F.data.startswith('move:'))
async def move_handler(callback: CallbackQuery):
    try:
        _, game_id, row_str, col_str = callback.data.split(':')
        row, col = int(row_str), int(col_str)

        game = session_manager.get_game(game_id)
        if not game:
            await callback.answer('Игра не найдена или завершена!', show_alert=True)
            return

        user_id = callback.from_user.id
        if user_id not in [game.player_x, game.player_o]:
            await callback.answer('Вы не участник этой игры!', show_alert=True)
            return

        if game.make_move(user_id, row, col):
            board_state = game.board

            player_x_id = game.player_x
            player_o_id = game.player_o

            if game.game_over:
                if game.winner:
                    winner_text = '❌ Крестики выиграли!' if game.winner == player_x_id else '⭕ Нолики выиграли!'
                else:
                    winner_text = '🤝 Ничья!'

                for player_id in [player_x_id, player_o_id]:
                    try:
                        await bot.edit_message_text(
                            f'Игра завершена!\n{winner_text}\nID игры: {game_id}',
                            chat_id=player_id,
                            message_id=user_game_messages[player_id],
                            reply_markup=create_game_keyboard(game_id, board_state)
                        )
                    except Exception as e:
                        print(f'Error updating message for {player_id}: {e}')

                if player_x_id in user_game_messages:
                    del user_game_messages[player_x_id]
                if player_o_id in user_game_messages:
                    del user_game_messages[player_o_id]
                session_manager.del_game(game_id)
            else:
                current_symbol = '❌' if game.current_player == player_x_id else '⭕'

                for player_id in [player_x_id, player_o_id]:
                    try:
                        await bot.edit_message_text(
                            f'Текущий ход: {current_symbol}\nID игры: {game_id}',
                            chat_id=player_id,
                            message_id=user_game_messages[player_id],
                            reply_markup=create_game_keyboard(game_id, board_state)
                        )
                    except Exception as e:
                        print(f'Error updating message for {player_id}: {e}')

            await callback.answer()
        else:
            await callback.answer('Недопустимый ход! Не ваша очередь или клетка занята.', show_alert=True)

    except Exception as e:
        print(f'Error in move handler: {e}')
        await callback.answer('Произошла ошибка!', show_alert=True)


@router.message()
async def other_messages_handler(msg: Message):
    await msg.answer('▶️ Используйте /play для начала игры в крестики-нолики!')


async def main():
    print('Бот запущен!')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
