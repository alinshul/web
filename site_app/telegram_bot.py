import telebot
from telebot import types
from django.conf import settings
from .models import CustomUser, Feedback, Reservation
import logging
from datetime import datetime, timedelta



# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

bot = telebot.TeleBot("8082851749:AAFjzwhJt_j9GoXI4lkRebR2TZsjeGUp-Ww")
user_data = {}


# Клавиатуры
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('Забронировать столик'),
        types.KeyboardButton('Мои бронирования'),
        types.KeyboardButton('Мой профиль'),
        types.KeyboardButton('Оставить отзыв')
    )
    return markup




def get_cancel_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Отменить'))
    return markup


def get_time_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    times = []
    for hour in range(10, 22):
        times.append(types.KeyboardButton(f"{hour}:00"))
        times.append(types.KeyboardButton(f"{hour}:30"))
    markup.add(*times)
    markup.add(types.KeyboardButton('Отменить'))
    return markup


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        user, created = CustomUser.objects.get_or_create(
            telegram_id=message.from_user.id,
            defaults={
                'username': f"tg_{message.from_user.id}",
                'first_name': message.from_user.first_name or '',
                'last_name': message.from_user.last_name or '',
                'is_telegram_user': True
            }
        )

        if created:
            bot.send_message(
                message.chat.id,
                "Добро пожаловать! Введите ваше имя:",
                reply_markup=get_cancel_keyboard()
            )
            bot.register_next_step_handler(message, process_name_step)
        else:
            bot.send_message(
                message.chat.id,
                f"С возвращением, {user.first_name}!",
                reply_markup=get_main_keyboard()
            )
    except Exception as e:
        logger.error(f"Ошибка в handle_start: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте снова.")


# Обработка имени
def process_name_step(message):
    try:
        if message.text == 'Отменить':
            bot.send_message(message.chat.id, "Регистрация отменена.", reply_markup=types.ReplyKeyboardRemove())
            return

        if len(message.text.strip()) < 2:
            raise ValueError("Имя должно содержать минимум 2 символа")

        user_data[message.chat.id] = {
            'telegram_id': message.from_user.id,
            'name': message.text.strip()
        }

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Поделиться номером", request_contact=True))
        markup.add(types.KeyboardButton('Отменить'))

        msg = bot.send_message(
            message.chat.id,
            "Отправьте ваш телефон или нажмите кнопку:",
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_phone_step)

    except Exception as e:
        logger.error(f"Ошибка в process_name_step: {e}")
        bot.send_message(
            message.chat.id,
            f"Ошибка: {str(e)}\nВведите ваше имя еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        bot.register_next_step_handler(message, process_name_step)


# Обработка телефона
def process_phone_step(message):
    try:
        if message.text == 'Отменить':
            bot.send_message(message.chat.id, "Регистрация отменена.", reply_markup=types.ReplyKeyboardRemove())
            return

        phone = None
        if message.contact:
            phone = message.contact.phone_number
        elif message.text:
            if not message.text.startswith('+') or not message.text[1:].isdigit() or len(message.text) != 12:
                raise ValueError("Телефон должен быть в формате +79991234567")
            phone = message.text

        if not phone:
            raise ValueError("Телефон не получен")

        # Создаем пользователя
        user = CustomUser.objects.create(
            username=f"tg_{user_data[message.chat.id]['telegram_id']}",
            first_name=user_data[message.chat.id]['name'],
            phone=phone,
            telegram_id=user_data[message.chat.id]['telegram_id'],
            is_telegram_user=True
        )

        bot.send_message(
            message.chat.id,
            f"Регистрация завершена!\nИмя: {user.first_name}\nТелефон: {user.phone}",
            reply_markup=get_main_keyboard()
        )

        # Очищаем временные данные
        if message.chat.id in user_data:
            del user_data[message.chat.id]

    except Exception as e:
        logger.error(f"Ошибка в process_phone_step: {e}")
        bot.send_message(
            message.chat.id,
            f"Ошибка: {str(e)}\nПопробуйте снова:",
            reply_markup=get_cancel_keyboard()
        )
        bot.register_next_step_handler(message, process_phone_step)


# Бронирование столика
@bot.message_handler(func=lambda msg: msg.text == 'Забронировать столик')
def start_reservation(message):
    try:
        user = CustomUser.objects.get(telegram_id=message.from_user.id)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        today = datetime.now().date()

        buttons = []
        for i in range(7):
            date = today + timedelta(days=i)
            buttons.append(types.KeyboardButton(date.strftime('%d.%m.%Y')))

        markup.add(*buttons)
        markup.add(types.KeyboardButton('Отменить'))

        bot.send_message(
            message.chat.id,
            "Выберите дату бронирования:",
            reply_markup=markup
        )
        bot.register_next_step_handler(message, process_reservation_date)
    except Exception as e:
        logger.error(f"Ошибка в start_reservation: {e}")
        bot.send_message(message.chat.id, "Ошибка при бронировании.", reply_markup=get_main_keyboard())


def process_reservation_date(message):
    try:
        if message.text == 'Отменить':
            bot.send_message(message.chat.id, "Бронирование отменено.", reply_markup=get_main_keyboard())
            return

        reservation_date = datetime.strptime(message.text, '%d.%m.%Y').date()
        user_data[message.chat.id] = {'reservation_date': message.text}

        bot.send_message(
            message.chat.id,
            "Выберите время:",
            reply_markup=get_time_keyboard()
        )
        bot.register_next_step_handler(message, process_reservation_time)
    except Exception as e:
        logger.error(f"Ошибка в process_reservation_date: {e}")
        bot.send_message(message.chat.id, "Неверный формат даты.", reply_markup=get_main_keyboard())


def process_reservation_time(message):
    try:
        if message.text == 'Отменить':
            bot.send_message(message.chat.id, "Бронирование отменено.", reply_markup=get_main_keyboard())
            return

        reservation_time = datetime.strptime(message.text, '%H:%M').time()
        user = CustomUser.objects.get(telegram_id=message.from_user.id)

        Reservation.objects.create(
            user=user,
            date=datetime.strptime(user_data[message.chat.id]['reservation_date'], '%d.%m.%Y').date(),
            time=reservation_time,
            persons=2,
            status='pending'
        )

        bot.send_message(
            message.chat.id,
            f"Столик забронирован на {user_data[message.chat.id]['reservation_date']} в {message.text}",
            reply_markup=get_main_keyboard()
        )

        if message.chat.id in user_data:
            del user_data[message.chat.id]

    except Exception as e:
        logger.error(f"Ошибка в process_reservation_time: {e}")
        bot.send_message(message.chat.id, "Ошибка при бронировании.", reply_markup=get_main_keyboard())







# Обработчик для кнопки "Мой профиль"
@bot.message_handler(func=lambda msg: msg.text == 'Мой профиль')
def show_profile(message):
    try:
        user = CustomUser.objects.get(telegram_id=message.from_user.id)

        profile_text = (
            f"<b>Ваш профиль</b>\n\n"
            f"Имя: {user.first_name}\n"
            f"Телефон: {user.phone if user.phone else 'не указан'}\n"
            f"Telegram ID: {user.telegram_id}\n\n"
            f"Изменить данные можно через кнопки ниже."
        )

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Изменить имя', 'Изменить телефон')
        markup.add('На главную')

        bot.send_message(
            message.chat.id,
            profile_text,
            parse_mode='HTML',
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Ошибка в show_profile: {e}")
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при загрузке профиля.",
            reply_markup=get_main_keyboard()
        )


# Обработчик для кнопки "Мои бронирования"
@bot.message_handler(func=lambda msg: msg.text == 'Мои бронирования')
def show_user_reservations(message):
    try:
        user = CustomUser.objects.get(telegram_id=message.from_user.id)
        print(user)
        reservations = Reservation.objects.filter(user=user).order_by('date', 'time')
        print(reservations)
        if not reservations.exists():
            bot.send_message(
                message.chat.id,
                "У вас пока нет активных бронирований.",
                reply_markup=get_main_keyboard()
            )
            return

        response = "<b>Ваши бронирования</b>:\n\n"
        for i, res in enumerate(reservations, 1):
            response += (
                f"{i}. <b>{res.date.strftime('%d.%m.%Y')}</b> в {res.time.strftime('%H:%M')}\n"
                f" Персон: {res.persons} | Статус: {res.get_status_display()}\n\n"
            )
        print(response)
        bot.send_message(
            message.chat.id,
            response,
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в show_user_reservations: {e}")
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при загрузке бронирований.",
            reply_markup=get_main_keyboard()
        )


# Обработчик для кнопки "Оставить отзыв"
@bot.message_handler(func=lambda msg: msg.text == 'Оставить отзыв')
def start_feedback(message):
    try:
        msg = bot.send_message(
            message.chat.id,
            "Напишите ваш отзыв или предложение:",
            reply_markup=get_cancel_keyboard()
        )
        bot.register_next_step_handler(msg, process_feedback)
    except Exception as e:
        logger.error(f"Ошибка в start_feedback: {e}")
        bot.send_message(
            message.chat.id,
            "Произошла ошибка.",
            reply_markup=get_main_keyboard()
        )


def process_feedback(message):
    try:
        if message.text == 'Отменить':
            bot.send_message(
                message.chat.id,
                "Отправка отзыва отменена.",
                reply_markup=get_main_keyboard()
            )
            return

        user = CustomUser.objects.get(telegram_id=message.from_user.id)
        Feedback.objects.create(
            user=user,
            message=message.text,
            source='TG'
        )

        bot.send_message(
            message.chat.id,
            "Спасибо за ваш отзыв! Мы ценим ваше мнение.",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_feedback: {e}")
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при сохранении отзыва.",
            reply_markup=get_main_keyboard()
        )


# Обработчики для изменения профиля
@bot.message_handler(func=lambda msg: msg.text in ['Изменить имя', 'Изменить телефон'])
def handle_profile_edit(message):
    try:
        if message.text == 'Изменить имя':
            msg = bot.send_message(
                message.chat.id,
                "Введите новое имя:",
                reply_markup=get_cancel_keyboard()
            )
            bot.register_next_step_handler(msg, process_new_name)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Поделиться номером", request_contact=True))
            markup.add(types.KeyboardButton('Отменить'))
            msg = bot.send_message(
                message.chat.id,
                "Отправьте новый телефон или нажмите кнопку:",
                reply_markup=markup
            )
            bot.register_next_step_handler(msg, process_new_phone)
    except Exception as e:
        logger.error(f"Ошибка в handle_profile_edit: {e}")
        bot.send_message(
            message.chat.id,
            "Произошла ошибка.",
            reply_markup=get_main_keyboard()
        )


def process_new_name(message):
    try:
        if message.text == 'Отменить':
            bot.send_message(
                message.chat.id,
                "Изменение имени отменено.",
                reply_markup=get_main_keyboard()
            )
            return

        if len(message.text.strip()) < 2:
            raise ValueError("Имя должно содержать минимум 2 символа")

        user = CustomUser.objects.get(telegram_id=message.from_user.id)
        old_name = user.first_name
        user.first_name = message.text.strip()
        user.save()

        bot.send_message(
            message.chat.id,
            f"Имя успешно изменено с '{old_name}' на '{user.first_name}'",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_new_name: {e}")
        bot.send_message(
            message.chat.id,
            f"Ошибка: {str(e)}",
            reply_markup=get_main_keyboard()
        )


def process_new_phone(message):
    try:
        if message.text == 'Отменить':
            bot.send_message(
                message.chat.id,
                "Изменение телефона отменено.",
                reply_markup=get_main_keyboard()
            )
            return

        phone = None
        if message.contact:
            phone = message.contact.phone_number
        elif message.text:
            if not message.text.startswith('+') or not message.text[1:].isdigit() or len(message.text) != 12:
                raise ValueError("Телефон должен быть в формате +79991234567")
            phone = message.text

        if not phone:
            raise ValueError("Телефон не получен")

        user = CustomUser.objects.get(telegram_id=message.from_user.id)
        old_phone = user.phone
        user.phone = phone
        user.save()

        bot.send_message(
            message.chat.id,
            f"Телефон успешно изменен с '{old_phone}' на '{user.phone}'",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_new_phone: {e}")
        bot.send_message(
            message.chat.id,
            f"Ошибка: {str(e)}",
            reply_markup=get_main_keyboard()
        )

