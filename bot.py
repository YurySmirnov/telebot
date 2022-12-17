import telebot
from telebot import types

bot = telebot.TeleBot('')

dict_users = dict()

current_account = [False, '']

def deny(message):
    bot.send_message(message.chat.id, "Ты не авторизован, для регистрации - /reg, для авторизации - /sign_in")


class User:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.categories = {'Планы': {}, 'Желания': {}, 'Мечты': {}}


@bot.message_handler(commands=['start'])
def start(message):
    mess = f"Вечер в хату, {message.from_user.first_name}, для информации пропиши /help"
    bot.send_message(message.chat.id, mess, parse_mode="html", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, '''Для взаимодействия с ботом использовать команды
            для регистрации - /reg
            для авторизации - /sign_in
            для выхода из учётной записи - /sign_out
            для удаления аккаунта - /erase_account
            для создания заметки - /make_note
            для удаления заметки - /erase_note
            для просмотра своих заметок - /show_objects
            для переименования категории - /rename_category
        для переноса заметки из одной категории в другую - /translate_note

            Для любых операций с заметками необходима авторизация!''')


@bot.message_handler(commands=['reg'])
def reg(message):
    bot.send_message(message.chat.id, "Придумай и введи логин", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, reg_get_login)


def reg_get_login(message):
    global login
    login = message.text
    bot.send_message(message.chat.id, "Придумай и введи пароль")
    bot.register_next_step_handler(message, reg_get_password)


def reg_get_password(message):
    global password
    password = message.text
    is_reg_success = reg_make_user(login, password)
    if is_reg_success:
        bot.send_message(message.chat.id, "Учетная запись создана. Теперь ты можешь авторизоваться - /sign_in")
    else:
        bot.send_message(message.chat.id, "Логин уже занят, повторить попытку регистрации - /reg")


def reg_make_user(login, password):
    if login in dict_users:
        return False
    dict_users[login] = User(login, password)
    return True


@bot.message_handler(commands=['sign_in'])
def sign_in(message):
    bot.send_message(message.chat.id, "Введи логин учётной записи")
    bot.register_next_step_handler(message, sign_in_get_login)


def sign_in_get_login(message):
    global login
    login = message.text
    if (login in dict_users.keys()):
        bot.send_message(message.chat.id, "Введи пароль учётной записи")
        bot.register_next_step_handler(message, sign_in_get_password)
    else:
        bot.send_message(message.chat.id, "Такого логина не существует, повторить попытку авторизации - /sign_in")


def sign_in_get_password(message):
    global password
    password = message.text
    if password == dict_users.get(login).password:
        current_account[1] = login
        current_account[0] = True
        bot.send_message(message.chat.id, "Ты вошёл в учётную запись, для вызова меню - /help")
    else:
        bot.send_message(message.chat.id, "Ты ввёл неправильный пароль, повторить попытку авторизации - /sign_in")


@bot.message_handler(commands=['sign_out'])
def sign_out(message):
    if current_account[0] != '':
        current_account[0] = False
        bot.send_message(message.chat.id, "Ты вышел из учётной записи, для авторизации - /sign_in", reply_markup=types.ReplyKeyboardRemove())
    else:
        deny(message)


@bot.message_handler(commands=['erase_account'])
def eraseaccount(message):
    if current_account[0]:
        del dict_users[current_account[1]]
        bot.send_message(message.chat.id, "Учётная запись успешно удалена, для создания новой - /reg", reply_markup=types.ReplyKeyboardRemove())
    else:
        deny(message)


@bot.message_handler(commands=['make_note'])
def make_note(message):
    if not current_account[0]:
        deny(message)
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*dict_users[current_account[1]].categories.keys())
    bot.send_message(message.chat.id, "Выбери категорию заметки или напиши новую категорию", reply_markup=markup)
    bot.register_next_step_handler(message, get_category_object)


def get_category_object(message):
    global category
    category = message.text
    if category not in dict_users[current_account[1]].categories.keys():
        dict_users[current_account[1]].categories[category] = {}
    bot.send_message(message.chat.id, "Введи имя заметки", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_name_object)


def get_name_object(message):
    global name
    name = message.text
    is_there_name = False
    for category in dict_users[current_account[1]].categories.keys():
        if name in dict_users[current_account[1]].categories[category].values():
            is_there_name = True
    if is_there_name:
        bot.send_message(message.chat.id, "Имя занято другим, попробуй заново - /make_note")
    else:
        bot.send_message(message.chat.id, "Введи текст заметки")
        bot.register_next_step_handler(message, add_text)


def add_text(message):
    global text
    text = message.text
    dict_users[current_account[1]].categories[category][name] = text
    bot.send_message(message.chat.id, "Заметка создана, для вызова меню - /help")


@bot.message_handler(commands=['rename_category'])
def rename_category(message):
    if not current_account[0]:
        deny(message)
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*dict_users[current_account[1]].categories.keys())
    bot.send_message(message.chat.id, "Выбери категорию заметки для переименования", reply_markup=markup)
    bot.register_next_step_handler(message, get_old_category)


def get_old_category(message):
    global old_category
    old_category = message.text
    if old_category not in dict_users[current_account[1]].categories.keys():
        bot.send_message(message.chat.id, "Ты выбрал несуществующую категорию, попробуй заново /rename_category",
                         reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, "Придумайте новую категорию", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_new_category)


def get_new_category(message):
    global new_category
    new_category = message.text
    if new_category in dict_users[current_account[1]].categories.keys():
        bot.send_message(message.chat.id, "Вы выбрали уже существующую категорию, попробуйте заново /rename_category")
        return
    dict_users[current_account[1]].categories[new_category] = dict_users[current_account[1]].categories[old_category]
    del dict_users[current_account[1]].categories[old_category]
    bot.send_message(message.chat.id, "Категория успешно переименована, меню - /help")


@bot.message_handler(commands=['show_objects'])
def show_objects(message):
    if not current_account[0]:
        deny(message)
    else:
        login = current_account[1]
        if len(dict_users.get(login).categories) == 0:
            bot.send_message(message.chat.id, "У вас ещё нет записок, для создания - /make_note")
            return
        categories = dict_users.get(login).categories
        for category in categories:
            current_category = dict_users.get(login).categories[category]
            for name, text in current_category.items():
                bot.send_message(message.chat.id, f'Категория: {category}; имя: {name}; текст: {text}')

        bot.send_message(message.chat.id, '''Вот и все записки как бы...
                                          Меню - /help''')


@bot.message_handler(commands=['erase_note'])
def erase_note(message):
    if not current_account[0]:
        deny(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*dict_users[current_account[1]].categories.keys())
        bot.send_message(message.chat.id, "Введи категорию удаляемой заметки", reply_markup=markup)
        bot.register_next_step_handler(message, get_erase_category)


def get_erase_category(message):
    login = current_account[1]
    global category
    category = message.text
    if category not in dict_users[login].categories.keys():
        bot.send_message(message.chat.id, "Категории с таким именем не существует, попробовать удалить заметку ещё раз - /erase_note",
                         reply_markup=types.ReplyKeyboardRemove())
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        print(dict_users[current_account[1]].categories[category].keys())
        if len(dict_users[current_account[1]].categories[category].keys()) == 0:
            bot.send_message(message.chat.id, "В текущей категории заметок ещё нет, попробуйте заново /erase_note")
            return
        markup.add(*dict_users[current_account[1]].categories[category].keys())
        bot.send_message(message.chat.id, "Введи имя заметки", reply_markup=markup)
        bot.register_next_step_handler(message, get_erase_name)


def get_erase_name(message):
    login = current_account[1]
    global name
    name = message.text
    if name not in dict_users[login].categories[category].keys():
        bot.send_message(message.chat.id, "Заметки с таким именем не существует, попробуй заново /erase_note",
                         reply_markup=types.ReplyKeyboardRemove())
    else:
        del dict_users[login].categories[category][name]
        bot.send_message(message.chat.id, "Заметка удалена, для вызова меню - /help", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['translate_note'])
def transfer_note(message):
    if not current_account[0]:
        deny(message)
    else:
        global markup
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*dict_users[current_account[1]].categories.keys())
        bot.send_message(message.chat.id, "Введи изначальную категорию переносимой заметки", reply_markup=markup)
        bot.register_next_step_handler(message, get_transfer_category_old)


def get_transfer_category_old(message):
    global old_category
    old_category = message.text
    if old_category not in dict_users[login].categories.keys():
        bot.send_message(message.chat.id, "Категории с таким именем не существует, попробуйте заново /translate_note")
    else:
        if len(dict_users[current_account[1]].categories[old_category].keys()) > 0:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*dict_users[current_account[1]].categories[old_category].keys())
            bot.send_message(message.chat.id, "Выбери имя заметки", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "В текущей категории заметок ещё нет, попробуйте заново /translate_note")
            return
        bot.register_next_step_handler(message, get_transfer_name)


def get_transfer_name(message):
    global name
    name = message.text
    if name not in dict_users[login].categories[old_category].keys():
        bot.send_message(message.chat.id, "Заметки с таким именем не существует, попробуй заново /translate_note")
    else:
        global text
        text = dict_users[login].categories[old_category][name]
        bot.send_message(message.chat.id, "Выбери желаемую категорию для заметки", reply_markup=markup)
        bot.register_next_step_handler(message, get_transfer_category_new)


def get_transfer_category_new(message):
    global new_category
    new_category = message.text
    if new_category not in dict_users[current_account[1]].categories.keys():
        bot.send_message(message.chat.id, "Вы выбрали несуществующую категорию, попробуй заново /translate_note")
        return
    dict_users[current_account[1]].categories[new_category][name] = text
    del dict_users[current_account[1]].categories[old_category][name]
    bot.send_message(message.chat.id, "Заметка успешна перенесена, для вызова меню - /help")

@bot.message_handler()
def get_text(message):
    if message.json['text'] not in ['/reg', '/start', '/erase_account', '/sign_in', '/sign_out', '/make_note', '/erase_note',
                                    '/show_objects', '/rename_category', '/translate_note', '/help']:
        bot.send_message(message.chat.id, message.json['text'] + ' - нет такой команды, для помощи нажми /help ', parse_mode="html",
                         reply_markup=types.ReplyKeyboardRemove())

bot.polling(none_stop=True)
