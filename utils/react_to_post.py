from aiogram import types

from random import choice

async def react_to_post(emoji, message):
    emojis = ["👍", "❤️", "🔥", "👏", "💯"]
    if emoji:
        react = types.ReactionTypeEmoji(emoji=emoji)
        await message.react([react])
    else:
        react = types.ReactionTypeEmoji(emoji=choice(emojis))
        await message.react([react])