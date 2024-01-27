from aiogram.filters import BaseFilter
from aiogram import types
import config
from utils import get_project_root
import json, string

class IsCussWord(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        cuss_words = get_project_root('cuss_words.json')
        return {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.text.split(' ')}\
        .intersection(set(json.load(open(cuss_words)))) != set()