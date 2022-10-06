import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ParseMode
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from config import TOKEN, words, minis

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
    if '*' in msg.text:
        reply = lookup_ext(msg.text.lower())
    else:
        reply = lookup(msg.text.lower())
    await bot.send_message(msg.from_user.id, reply, parse_mode=ParseMode.MARKDOWN)

def load_dict():
    with open('mini.txt', mode='r', encoding='utf-8') as f:
        for ln in f:
            #if not ln.find('==') == 0 and ln[2:].find('==') > 0:
                # есть слово и значение
            items = ln.rstrip().split('==')
            cur_word   = items[0].lower()
            tmp_array  = items[1].lower().split(',')
            cur_meaning = [i.strip() for i in tmp_array]
            minis[cur_word] = cur_meaning

    with open('dict.txt', mode='r', encoding='utf-8') as f:
        for ln in f:
            items = ln.rstrip().split('==')
            cur_word   = items[0].lower()
            tmp_array  = items[1].lower().split(',')
            cur_meaning = [i.strip() for i in tmp_array]
            words[cur_word] = cur_meaning


def lookup(in_str):
    ''' ищет слово в двух словарях, малом и большом. если в малом слово есть тоже, тогда ставится * - признак высокой частотности '''
    out_str_r = ''
    out_str_k = ''
    if in_str in words.keys():
        out_str_r = 'рус.: '+str(words[in_str]).replace("'", '')+'\n'
    else:
        out_str_r = 'рус.: не найдено\n'
    is_mini_dict = False
    for key in words.keys():
        if in_str in words[key]:
            if key in minis.keys():
                mini = ' \*'
                is_mini_dict = True
            else:
                mini = ''
            out_str_k += 'каз.: ' + key + ' (' + str(words[key]).replace("'", '') + ')' + mini + '\n'
    if out_str_k == '':
        out_str_k = 'каз.: не найдено\n'
    ret_str = out_str_r + out_str_k
    if is_mini_dict:
        ret_str += '\n\* - слово входит в 3000 самых встречающихся.\n'
    return ret_str

def lookup_ext(in_str):
    ''' ищет слово по подстроке '''
    matches = []
    in_str = in_str.replace('*', '')
    for key in words.keys():
        if key.find(in_str) >= 0:
            matches.append((key, words[key]))
        #for i in words[key]:
        #    if i.find(in_str) >= 0:
        #        matches.append((key, words[key]))
        #        break
    return str(matches)
        

if __name__ == '__main__':
    load_dict()
    executor.start_polling(dp)
