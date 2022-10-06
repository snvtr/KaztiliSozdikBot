import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ParseMode
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from config import TOKEN, W

logging.basicConfig(format=u'%(filename)s [ln:%(lineno)+3s]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['help', 'start'])
async def help_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, 'Просто вводи слово на любом из двух языков.', parse_mode=ParseMode.MARKDOWN)

@dp.message_handler()
async def echo_message(msg: types.Message):
    #arguments = msg.text.rstrip().split(' ')
    reply = lookup(msg.text.lower())
    await bot.send_message(msg.from_user.id, reply, parse_mode=ParseMode.MARKDOWN)

def load_dict():
    with open('dict.txt', mode='r', encoding='utf-8') as f:
        for ln in f:
            ln = ln.rstrip()
            if not ln.find('==') == 0 and ln[2:].find('==') > 0:
                # есть слово и значение
                items = ln.rstrip().split('==')
                cur_word   = items[0].lower()
                tmp_array  = items[1].lower().split(',')
                cur_meaning = [i.strip() for i in tmp_array]
                W[cur_word] = {}
                W[cur_word]['meaning'] = cur_meaning
            elif ln.find('==') == 0:
                # довесок к значению, отдельными строками фразы
                items = ln.rstrip().split('==')
                phrase    = items[1].replace('=', '').lower()
                tmp_array = items[2].lower().split(',')
                meaning = [i.strip() for i in tmp_array]
                W[cur_word][phrase] = meaning

def lookup(in_str):
    out_str_r = ''
    if in_str in W.keys():
        out_str_r = 'рус.: '+str(W[in_str]['meaning']).replace("'", '')+'\n'
    else:
        out_str_r = 'рус.: не найдено\n'
    out_str_k = ''
    for key in W.keys():
        if in_str in W[key]['meaning']:
            out_str_k += 'каз.: ' + key + ' (' + str(W[key]['meaning']).replace("'", '') + ')\n'
    if out_str_k == '':
        out_str_k = 'каз.: не найдено\n'
    return out_str_r + out_str_k

if __name__ == '__main__':
    load_dict()
    executor.start_polling(dp)
