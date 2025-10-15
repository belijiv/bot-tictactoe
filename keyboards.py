from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_game_keyboard(game_id: str, board=None):
    if board is None:
        board = [[' ' for _ in range(3)] for _ in range(3)]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for row in range(3):
        row_buttons = []
        for col in range(3):
            symbol = board[row][col]
            text = '⬜' if symbol == ' ' else ('❌' if symbol == 'X' else '⭕')
            callback_data = f'move:{game_id}:{row}:{col}'
            row_buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        keyboard.inline_keyboard.append(row_buttons)

    return keyboard