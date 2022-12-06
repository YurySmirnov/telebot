import telebot
from telebot import types
bot = telebot.TeleBot('5753570878:AAE00JFc4RRELkZYRl8YQVhYzHBi6iLL50Q')

def deny(message):
    bot.send_message(message.chat.id, "Вы не авторизованы")


class User:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.categories = {'Планы' : {}, 'Желания' : {}, 'Мечты' : {}}
        self.list_buttons = ['Планы', 'Желания', 'Мечты']

        
usrs = dict()

currentaccount = [False, '']


@bot.message_handler(commands=['start'])
def start(message):
    mess = f"Вечер в хату, {message.from_user.first_name}, для информации пропиши /help"
    bot.send_message(message.chat.id, mess, parse_mode="html", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, '''Для взаимодействия использовать команды
            Для регистрации - /reg
            Для деавторизации - /erase_account
            Для авторизации - /signin
            Для выхода из учётной записи - /signout
            Для создания заметки - /make_note
            Для удаления заметки - /erase_note
            Для просмотра своих заметок - /show_objects
            Для переименования категории - /rename_category
        Для переноса заметки из одной категории в другую - /translate_note
            
            !!Перед отправкой любой из последних пяти команд авторизируйтесь''')


@bot.message_handler(commands=['reg'])
def reg(message):
    bot.send_message(message.chat.id, "Придумайте и введите логин", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, reg_get_login)


def reg_get_login(message):
    global login
    login = message.text
    bot.send_message(message.chat.id, "Придумайте и введите пароль")
    bot.register_next_step_handler(message, reg_get_password)


def reg_get_password(message):
    global password
    password = message.text
    success = reg_makeusr(login, password)
    if success:
        bot.send_message(message.chat.id, "Учетная запись создана. Теперь вы можете авторизоваться")
    else:
        bot.send_message(message.chat.id, "Логин уже занят")


def reg_makeusr(login, password):
    if login in usrs.keys():
        return False
    usrs[login] = User(login, password)
    return True


@bot.message_handler(commands=['signin'])
def signin(message):
    bot.send_message(message.chat.id, "Введите логин учётной записи")
    bot.register_next_step_handler(message, signin_get_login)

def signin_get_login(message):
    global login
    login = message.text
    if (login in usrs.keys()):
        bot.send_message(message.chat.id, "Введите пароль учётной записи")
        bot.register_next_step_handler(message, signin_get_password)
    else:
        bot.send_message(message.chat.id, "Такого логина не существует")


def signin_get_password(message):
    global password
    password = message.text
    if password == usrs.get(login).password:
        currentaccount[0] = True
        currentaccount[1] = login
        bot.send_message(message.chat.id, "Вы вошли в учётную запись")
    else:
        bot.send_message(message.chat.id, "Вы ввели неправильный пароль")


@bot.message_handler(commands=['signout'])
def signout(message):
    if currentaccount[0]:
        currentaccount[0] = False
        bot.send_message(message.chat.id, "Вы вышли из учётной записи", reply_markup=types.ReplyKeyboardRemove())
    else:
        deny(message)


@bot.message_handler(commands=['erase_account'])
def eraseaccount(message):
    if currentaccount[0]:
        del usrs[currentaccount[1]]
        bot.send_message(message.chat.id, "Учётная запись удалена", reply_markup=types.ReplyKeyboardRemove())
    else:
        deny(message)


@bot.message_handler(commands=['make_note'])
def make_note(message):
    if not currentaccount[0]:
        deny(message)
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*usrs[currentaccount[1]].categories.keys())
    bot.send_message(message.chat.id, "Выберите категорию заметки или напишите новую категорию", reply_markup=markup)
    bot.register_next_step_handler(message, get_category_object)


def get_category_object(message):
    global category
    category = message.text
    if category not in usrs[currentaccount[1]].categories.keys():
        usrs[currentaccount[1]].categories[category] = {}
    bot.send_message(message.chat.id, "Введите имя заметки", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_name_object)


def get_name_object(message):
    global name
    name = message.text
    is_there_name = False
    for category in usrs[currentaccount[1]].categories.keys():
        if name in usrs[currentaccount[1]].categories[category].values():
            is_there_name = True
    if is_there_name:
        bot.send_message(message.chat.id, "Имя занято другим, попробуйте заново - /make_note")
    else:
        bot.send_message(message.chat.id, "Введите текст заметки")
        bot.register_next_step_handler(message, add_text)


def add_text(message):
    global text
    text = message.text
    usrs[currentaccount[1]].categories[category][name] = text
    bot.send_message(message.chat.id, "Заметка создана")


@bot.message_handler(commands=['rename_category'])
def rename_category(message):
    if not currentaccount[0]:
        deny(message)
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*usrs[currentaccount[1]].categories.keys())
    bot.send_message(message.chat.id, "Выберите категорию заметки для переименования", reply_markup=markup)
    bot.register_next_step_handler(message, get_old_category)


def get_old_category(message):
    global old_category
    old_category = message.text
    if old_category not in usrs[currentaccount[1]].categories.keys():
        bot.send_message(message.chat.id, "Вы выбрали несуществующую категорию, попробуйте заново /rename_category", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, "Придумайте новую категорию", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_new_category)


def get_new_category(message):
    global new_category
    new_category = message.text
    if new_category in usrs[currentaccount[1]].categories.keys():
        bot.send_message(message.chat.id, "Вы выбрали уже существующую категорию, попробуйте заново /rename_category")
        return
    usrs[currentaccount[1]].categories[new_category] = usrs[currentaccount[1]].categories[old_category]
    del usrs[currentaccount[1]].categories[old_category]
    bot.send_message(message.chat.id, "Категория успешно переименована")


@bot.message_handler(commands=['show_objects'])
def show_objects(message):
    if not currentaccount[0]:
        deny(message)
    else:
        login = currentaccount[1]
        if len(usrs.get(login).categories) == 0:
            bot.send_message(message.chat.id, "У вас ещё нет записок")
            return
        categories = usrs.get(login).categories
        for category in categories:
            current_category = usrs.get(login).categories[category]
            for name, text in current_category.items():
                bot.send_message(message.chat.id, f'Категория: {category}; имя: {name}; текст: {text}')

        bot.send_message(message.chat.id, "Вот и все записки как бы...")


@bot.message_handler(commands=['erase_note'])
def erase_note(message):
    if not currentaccount[0]:
        deny(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*usrs[currentaccount[1]].categories.keys())
        bot.send_message(message.chat.id, "Введите категорию удаляемой заметки", reply_markup=markup)
        bot.register_next_step_handler(message, get_erase_category)


def get_erase_category(message):
    login = currentaccount[1]
    global category
    category = message.text
    if category not in usrs[login].categories.keys():
        bot.send_message(message.chat.id, "Категории с таким именем не существует", reply_markup=types.ReplyKeyboardRemove())
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        print(usrs[currentaccount[1]].categories[category].keys())
        if len(usrs[currentaccount[1]].categories[category].keys()) == 0:
            bot.send_message(message.chat.id, "В текущей категории заметок ещё нет, попробуйте заново /erase_note")
            return
        markup.add(*usrs[currentaccount[1]].categories[category].keys())
        bot.send_message(message.chat.id, "Введите имя заметки", reply_markup=markup)
        bot.register_next_step_handler(message, get_erase_name)


def get_erase_name(message):
    login = currentaccount[1]
    global name
    name = message.text
    if name not in usrs[login].categories[category].keys():
        bot.send_message(message.chat.id, "Заметки с таким именем не существует, попробуйте заново /erase_note", reply_markup=types.ReplyKeyboardRemove())
    else:
        del usrs[login].categories[category][name]
        bot.send_message(message.chat.id, "Заметка удалена", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['translate_note'])
def transfer_note(message):
    if not currentaccount[0]:
        deny(message)
    else:
        global markup
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*usrs[currentaccount[1]].categories.keys())
        bot.send_message(message.chat.id, "Введите изначальную категорию переносимой заметки", reply_markup=markup)
        bot.register_next_step_handler(message, get_transfer_category_old)


def get_transfer_category_old(message):
    global old_category
    old_category = message.text
    if old_category not in usrs[login].categories.keys():
        bot.send_message(message.chat.id, "Категории с таким именем не существует, попробуйте создать /make_note")
    else:
        if len(usrs[currentaccount[1]].categories[old_category].keys()) > 0:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*usrs[currentaccount[1]].categories[old_category].keys())
            bot.send_message(message.chat.id, "Выберите имя заметки", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "В текущей категории заметок ещё нет, попробуйте создать /make_note")
            return
        bot.register_next_step_handler(message, get_transfer_name)


def get_transfer_name(message):
    global name
    name = message.text
    if name not in usrs[login].categories[old_category].keys():
        bot.send_message(message.chat.id, "Заметки с таким именем не существует, попробуйте заново /translate_note")
    else:
        global text
        text = usrs[login].categories[old_category][name]
        bot.send_message(message.chat.id, "Выберите желаемую категорию для заметки", reply_markup=markup)
        bot.register_next_step_handler(message, get_transfer_category_new)


def get_transfer_category_new(message):
    global new_category
    new_category = message.text
    if new_category not in usrs[currentaccount[1]].categories.keys():
        bot.send_message(message.chat.id, "Вы выбрали несуществующую категорию, попробуйте заново /translate_note")
        return
    usrs[currentaccount[1]].categories[new_category][name] = text
    del usrs[currentaccount[1]].categories[old_category][name]
    bot.send_message(message.chat.id, "Заметка успешна перенесена")


bot.polling(none_stop=True)
