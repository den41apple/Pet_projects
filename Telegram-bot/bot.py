import telebot
from telebot import types
import time
from requests import ReadTimeout
from image_maker import congratulation_func
from envparse import env
from time import sleep
from parser_auto_ru import parse, quantity_auto_return

message_global = str()

TOKEN = env.str('TOKEN')

bot = telebot.TeleBot(TOKEN)

# Переменные для клавиатуры
mk_pct = '🖼 Сделать открытку'
mk_parser = '📲Спарсить автомобили'
yes = '✅ Да'
no = '🙅 Нет'
crysler = '🛺Crysler'
haval = '🚕Haval'
mini = '🚗Mini'
subaru = '🚙Subaru'

welcome_message = '🎉*Тебя приветствует тестовый бот*🎊\n\nЗдесь ты можешь:\n\n' \
                  '1. Сделать *праздничную открытку*\n' \
                  '2. Спарсить актуальные *объявления о продаже авто в Москве* с сайта auto.ru\n\n' \
                  '⏬Для подолжения нажми кнопку ниже⏬'

# Меню клавиатуры
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keyboard.row(mk_pct, mk_parser)


def menu_restart(call):
    """Выводит сообщение после получения картинки пользователем"""
    bot.send_message(call.from_user.id, 'Спасибо, что пользуешься мной, мне нравится делать картинки 🙂',
                     reply_markup=keyboard, parse_mode='Markdown')


@bot.message_handler(commands=['start'])
def menu(message):
    """Выполняет действия по команде /START"""
    bot.send_message(message.chat.id, welcome_message, reply_markup=keyboard, parse_mode='Markdown')


def menu_with_call(call):
    """Дублирует меню, но выполняется после INLINE клавиатуры"""
    bot.send_message(call.from_user.id, welcome_message, reply_markup=keyboard, parse_mode='Markdown')


def menu_with_message(message):
    """Дублирует меню, но выполняется после INLINE клавиатуры"""
    bot.send_message(message.chat.id, welcome_message, reply_markup=keyboard, parse_mode='Markdown')


# Словарь для фраз которые печатаем на картинке
# Это для того что бы каждому пользователю делать картинку с его фразой
phrases = {}

dict_for_answers = {'привет': 'Ну приветик',
                    'пока': 'ну давай, пока',
                    'кто я?': 'ты самый лучший человек!',
                    'расскажи секрет': 'неа',
                    'unknow': 'нет такой комманды',
                    crysler: 'Crysler',
                    haval: 'Haval',
                    mini: 'Mini',
                    subaru: 'Subaru'
                    }


@bot.message_handler(content_types=['text'])
def start_message(message):
    """Принимает текст из чата и отдает заготовленный текст из словаря dict_for_answers"""

    try:
        # Ищет различные варианты в словаре
        bot.send_message(message.chat.id, message.from_user.first_name + ', ' + dict_for_answers[message.text.lower()])
    except KeyError as err:
        pass

    def make_picture(call, text_from_call):
        """Собственно, отправляется в модуль создания картинки"""
        image_to_send = congratulation_func(phrases[call.from_user.id])
        bot.send_photo(chat_id=call.from_user.id, photo=image_to_send)

    # Сообщение из чата -> парсить
    if message.text == mk_parser:
        def go_to_parse(message):
            bot.send_message(message.chat.id, f'Задача парсинга автомобилей марки *{dict_for_answers[message.text]}* начата\n\n'
                                              f'По окончанию будет прислан файл csv', parse_mode='Markdown')
            bot.send_document(message.chat.id, parse(variant=dict_for_answers[message.text]))

            bot.send_message(message.chat.id, f'Автомобилей получено: *{quantity_auto_return()} шт*',
                             parse_mode='Markdown')

            sleep(1)
            bot.send_message(message.chat.id, message.from_user.first_name +
                             ', используй эту информацию во благо 👆')
            sleep(1)
            bot.send_message(message.chat.id, 'Ладно, шучу 😎 давай сделаем еще что-нибудь?')
            sleep(1.5)
            menu_with_message(message)

        keyboard_for_parsing = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard_for_parsing.row(mini, subaru)
        keyboard_for_parsing.row(crysler, haval)

        bot.send_message(message.chat.id, message.from_user.first_name +
                         ' выбери марку машины:', parse_mode='Markdown', reply_markup=keyboard_for_parsing)


        bot.register_next_step_handler(message, go_to_parse)



    # Сообщение из чата -> делать картинку
    elif message.text == mk_pct:
        bot.send_message(message.chat.id, message.from_user.first_name +
                         ' введи *короткий* текст который будет на картинке:', parse_mode='Markdown')

        def check_text(message):
            """Здесь спрашивается верный ли текст"""
            global text_from_call
            keyboard_check_text = types.InlineKeyboardMarkup()
            key_yes = types.InlineKeyboardButton(text=yes, callback_data='yes')
            key_no = types.InlineKeyboardButton(text=no, callback_data='no')
            keyboard_check_text.add(key_yes, key_no)
            text_from_call = message.text  # Текст открытки который выводится для проверки
            phrases.setdefault(message.chat.id, message.text)

            # Создаем словарь фраз, что бы не перепутать кому какой фразой ответить
            phrases.setdefault(message.chat.id, message.text)  # Здесь создаем ключ если нет
            phrases[message.chat.id] = message.text  # А здесь мы его меняем при повторном проходе

            bot.send_message(message.chat.id, f'"{text_from_call}" - Это верный текст?',
                             reply_markup=keyboard_check_text)

            @bot.callback_query_handler(func=lambda call: call.data == 'yes')
            def make_picture_final_yes(call):
                """Последняя стадия, удостоверяется в верности текста ЕСЛИ ДА"""
                make_picture(call=call, text_from_call=text_from_call)
                sleep(1.5)
                bot.send_message(call.from_user.id, '*Поздравляю, у тебя отличная открытка!*', parse_mode='Markdown')
                sleep(1)
                menu_restart(call)

            @bot.callback_query_handler(func=lambda call: call.data == 'no')
            # @bot.callback_query_handlers
            def make_picture_final_no(call):
                """Последняя стадия, удостоверяется в верности текста ЕСЛИ НЕТ"""
                menu_with_call(call)

        # Посылает на проверку сообщение
        bot.register_next_step_handler(message, check_text)


# Запуск бота
def telegram_polling():
    try:
        bot.polling(none_stop=True)

    except ReadTimeout as err:
        # Остановка бота
        bot.stop_polling()
        time.sleep(3)
        telegram_polling()


if __name__ == '__main__':
    telegram_polling()
