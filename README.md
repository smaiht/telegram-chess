# Telegram Chess Inline Bot
## About

- A simple and efficient Telegram bot for playing chess, built using Aiogram. 
- This bot operates in inline mode, allowing users to play chess with other chat participants.
- All moves are reflected and updated in the original message, ensuring a seamless gaming experience.

## Dependencies

This project utilizes the [python-chess](https://github.com/niklasf/python-chess) library by [niklasf](https://github.com/niklasf) for chess logic and operations.


## Try Before Install

Want to give it a shot before installing? It's easy! Simply type `@nujno_mnogo_rabot` in any chat on Telegram and click "Play Chess".

![Telegram_Z43QP52CSi](https://github.com/smaiht/telegram-chess/assets/23002525/6b78b7cd-a4fd-46f9-a28b-cd8d48c542e1)


## Installation

### 1. Install via pip

```bash
pip install telegram-chess
```


### 2. Manual Installation

- Download the `telegram_chess.py` file.
- Place it in your project directory.




## Usage with Aiogram 3.0.1
```python
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineQuery
import asyncio

from telegram_chess import TelegramChess

TOKEN = "BOT_TOKEN_GOES_HERE" 
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

chess_game = TelegramChess()

@dp.inline_query()
async def inline_echo(inline_query: types.InlineQuery):
    await chess_game.answer_with_inline_chess_query(inline_query)

@dp.callback_query(F.data.startswith(chess_game.chess_data_start))
async def handle_callback(callback_query: types.CallbackQuery):
    await chess_game.make_move(callback_query, bot)

async def on_startup():
    print("Welcome to Chess Bot by @EnMind")

async def main() -> None:
    await dp.start_polling(bot)
    await on_startup()

if __name__ == "__main__":
    asyncio.run(main())
```

Enjoy playing chess with your friends on Telegram!
