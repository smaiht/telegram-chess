import chess
from aiogram.types import InlineQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types

class TelegramChess:
    chess_piece_symbols = {
        'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
        'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
        ".": " ",
        "*": "[*]",
        "|": "(*",
        "+": "*†",
        "#": "*",
        "x": "{*}"
    }

    chess_data_start = 'chess:'



    def __init__(self):
        self.board_states = {}



    def create_chess_markup(self, chess_figures):
        markup_rows = []
        for row_index, row in enumerate(chess_figures):
            buttons = []
            for col_index, figure in enumerate(row):
                cell_name = f'{self.chess_data_start}{chr(col_index + 97)}{8 - row_index}'  # 'a' ASCII code is 97
                buttons.append(InlineKeyboardButton(text=figure, callback_data=cell_name)) 
            markup_rows.append(buttons)
        markup = InlineKeyboardMarkup(inline_keyboard=markup_rows)
        return markup



    def render_board(self, board, highlight_squares=None, capturable_squares=None, active_piece=None):
        board_str = str(board).replace(' ', '')
        rows = board_str.split('\n')

        board_array = [[self.chess_piece_symbols[square] for square in row] for row in rows]
        legal_moves_from = [move.from_square for move in board.legal_moves]
        
        for square in range(64):
            row = 7 - square // 8
            col = square % 8

            if active_piece is None and square in legal_moves_from and board_array[row][col] != self.chess_piece_symbols["."]:
                board_array[row][col] = f"({board_array[row][col]})"

            if highlight_squares and square in highlight_squares:
                if square in capturable_squares:
                    board_array[row][col] = f"x{board_array[row][col]}"
                else:
                    board_array[row][col] = f"[{board_array[row][col]}]"

            if active_piece is not None and square == active_piece:
                board_array[row][col] = f"({board_array[row][col]})"

        return board_array



    def update_chess_state(self, inline_message_id, selected_square=None):
        if inline_message_id not in self.board_states:
            self.board_states[inline_message_id] = {"board": chess.Board(), "selected_square": selected_square}
        else:
            self.board_states[inline_message_id]["selected_square"] = selected_square
        return self.board_states[inline_message_id]



    async def answer_with_inline_chess_query(self, inline_query):
        board = chess.Board()
        markup = self.create_chess_markup(self.render_board(board))
        input_content = types.InputTextMessageContent(
            message_text=f"{inline_query.query}\n\n————Шахматы————",
        )
        item = types.InlineQueryResultArticle(
            id='1',
            title='Chess Game',
            description='Зарубиться в шахматы',
            input_message_content=input_content,
            reply_markup=markup,
            thumb_url="https://i.imgur.com/KhU0s3z.jpg",
        )
        await inline_query.answer(results=[item], cache_time=1, switch_pm_parameter="start", switch_pm_text="Отправить запрос!")



    async def make_move(self, callback_query, bot):
        game_text = f"————Шахматы————\n"
        
        square = callback_query.data[len(self.chess_data_start):] 
        inline_message_id = callback_query.inline_message_id

        self.board_states.setdefault(inline_message_id, {"board": chess.Board(), "selected_square": None})
        state = self.board_states[inline_message_id]
        
        board = state["board"]
        square_num = chess.parse_square(square)
        selected_square = state["selected_square"]

        markup = self.create_chess_markup(self.render_board(board))
        if selected_square is None:
            moves = [move for move in board.legal_moves if move.from_square == square_num]
            if moves:
                selected_square = square_num
                markup = self.create_chess_markup(self.render_board(board, [move.to_square for move in moves], [move.to_square for move in moves if board.piece_at(move.to_square)], selected_square))
                game_text += f"<a href='tg://user?id={callback_query.from_user.id}'>{callback_query.from_user.full_name}</a> выбрал <b>{square}</b>"
            else:
                await bot.answer_callback_query(callback_query.id, text='Invalid position, please select a chess piece with legal moves.')
        else:
            if selected_square == square_num:
                selected_square = None
                markup = self.create_chess_markup(self.render_board(board))
            else:
                legal_moves = [move for move in board.legal_moves if move.from_square == selected_square]
                legal_targets = [move.to_square for move in legal_moves]
                if square_num in legal_targets:
                    move = legal_moves[legal_targets.index(square_num)]
                    success_capture = board.is_capture(move)
                    captured_piece = board.remove_piece_at(square_num)
                    
                    piece_moving = board.piece_at(move.from_square) # Get piece before making move.
                    board.push(move)
                    selected_square = None

                    game_text += f"<a href='tg://user?id={callback_query.from_user.id}'>{callback_query.from_user.full_name}</a> сходил <b>{move}</b>"
                    
                    if success_capture:
                        action_text = f"{chess.piece_name(piece_moving.piece_type)} съел {chess.piece_name(captured_piece.piece_type)}"
                        game_text += f": {action_text}"

                    action_text = ""
                    if board.is_checkmate():
                        action_text = f"Шах и мат! {callback_query.from_user.full_name} победил!"
                    elif board.is_check():
                        action_text = f"{callback_query.from_user.full_name} поставил Шах!"
                    elif board.is_stalemate():
                        action_text = f"{callback_query.from_user.full_name} застрял в тупике! Ничья!"
                    elif board.is_insufficient_material():
                        action_text = f"{callback_query.from_user.full_name} не может победить! Ничья!"
                    elif board.is_seventyfive_moves():
                        action_text = f"Ничья! {callback_query.from_user.full_name} не может победить за 75 ходов!"
                    elif board.is_variant_draw():
                        action_text = f"Ничья! {callback_query.from_user.full_name} не может победить!"

                    game_text += f": {action_text}"

                    if piece_moving.piece_type == chess.PAWN and board.piece_at(square_num).piece_type == chess.QUEEN:
                        action_text = f" (Пешка {callback_query.from_user.full_name} превратилась в Ферзя!)"
                        game_text += f": {action_text}"

                    await bot.answer_callback_query(callback_query.id, text=action_text)

                    markup = self.create_chess_markup(self.render_board(board))
                else:
                    await bot.answer_callback_query(callback_query.id, text="Invalid move, please enter a valid target square.")
                    return

        self.update_chess_state(inline_message_id, selected_square)
        await bot.edit_message_text(text=game_text, inline_message_id=inline_message_id, reply_markup=markup)

