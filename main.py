import os

from pyexpat.errors import messages
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler)
import random
import requests
import json
from datetime import datetime



BOT_TOKEN = '8394385147:AAFXWyxFJYAAY2aqh1tA5GS2RBaJrb68GFU'

NAME, FEEDBACK, RATING, CONFIRMATION = range(4)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	keyboard = [
		[KeyboardButton("Информация"), KeyboardButton("Помощь")],
		[KeyboardButton("Случайное число"), KeyboardButton("Обо мне")],
		[KeyboardButton("Inline кнопки"), KeyboardButton("Опрос")],
		[KeyboardButton("Оставить отзыв"), KeyboardButton("Курс валют")],
		[KeyboardButton("Погода"), KeyboardButton("Случайная шутка")]
	]
	reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
	await update.message.reply_text("Привет, я ботяра. Выбери одно из действий ниже:", reply_markup=reply_markup)

async def start_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text(
		'Отлично, давайте оставим отзыв. \n'
		'Пожалуйста введите ваше имя:'
	)

	return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
	user_name = update.message.text
	context.user_data['feedback_name'] = user_name

	await update.message.reply_text(
		f'Спасибо, {user_name}\n'
		f'Теперь напишите ваш отзыв:'
	)
	return FEEDBACK


async def get_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
	feedback_text = update.message.text
	context.user_data['feedback_text'] = feedback_text


	keyboard = [
		[InlineKeyboardButton("1 звезда", callback_data='rating_1'),
		 InlineKeyboardButton("2 звезды", callback_data='rating_2')],
		[InlineKeyboardButton("3 звезды", callback_data='rating_3'),
		 InlineKeyboardButton("4 звезды", callback_data='rating_4')],
		[InlineKeyboardButton("5 звезд", callback_data='rating_5')]
	]
	reply_markup = InlineKeyboardMarkup(keyboard)

	await update.message.reply_text(
		'Теперь оцените бота от 1 до 5 звезд:',
		reply_markup=reply_markup
	)
	return RATING

async def get_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
	query = update.callback_query
	await query.answer()

	rating = query.data.split('_')[1]
	context.user_data['feedback_rating'] = rating

	name = context.user_data.get['feedback_name', 'Пользователь']
	feedback = context.user_data.get['feedback_text', '']

	confirmation_text =  (
		f"Проверьте ваши данные:\n\n"
        f"Имя: {name}\n"
        f"Отзыв: {feedback}\n"
        f"Оценка: {rating}/5\n\n"
        f"Все верно?"
	)

	keyboard = [
		[InlineKeyboardButton("Да, отправить", callback_data='confirm_yes'),
		InlineKeyboardButton("Нет, отменить", callback_data='confirm_no')]
	]
	reply_markup = InlineKeyboardMarkup(keyboard)

	await query.edit_message_text(confirmation_text, reply_markup=reply_markup)
	return CONFIRMATION


async def confirm_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):

	query = update.callback_query
	await query.answer( )

	if query.data == "confirm_yes":

		name = context.user_data['feedback_name']
		rating = context.user_data['feedback_rating']
		feedback_text = context.user_data['feedback_text']


		print(f"Новый отзыв от {name}: Оценка {rating}/5 - {feedback_text}")


		context.user_data.clear( )

		await query.edit_message_text(
			f"Спасибо за ваш отзыв, {name}!\n"
			f"Ваша оценка {rating}/5 очень важна для нас!\n\n"
			f"Ваш отзыв: \"{feedback_text}\""
		)
	else:

		context.user_data.clear( )
		await query.edit_message_text("Отзыв отменен.")

	return ConversationHandler.END


async def cancel_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
	context.user_data.clear( )
	await update.message.reply_text('Диалог отменен.')
	return ConversationHandler.END


async def inline_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	keyboard = [
		[InlineKeyboardButton("Нравится", callback_data="like"),
		 InlineKeyboardButton("Не нравится", callback_data="dislike")],
		[InlineKeyboardButton("Сгенерировать число", callback_data="random"),
		 InlineKeyboardButton("Погода", callback_data="weather")],
		[InlineKeyboardButton("Опрос", callback_data="poll"),
		 InlineKeyboardButton("Случайная шутка", callback_data="joke")],
		[InlineKeyboardButton("Закрыть", callback_data="close")]
	]
	reply_markup = InlineKeyboardMarkup(keyboard)

	await update.message.reply_text(
		"Выберите действие:\n"
		"Попробуй эти интерактивные кнопки!",
		reply_markup=reply_markup
	)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

	query = update.callback_query
	await query.answer( )

	callback_data = query.data

	if callback_data == "like":
		await query.edit_message_text("Спасибо за лайк! Рад, что нравлюсь!")

	elif callback_data == "dislike":
		await query.edit_message_text("Ой, жаль что не понравилось... Что можно улучшить?")

	elif callback_data == "random":
		number = random.randint(1, 1000)
		await query.edit_message_text(f"Сгенерировано число: {number}")

	elif callback_data == "weather":
		weather_options = ["Солнечно", "Дождь", "Снег", "Облачно", "Ветрено"]
		weather = random.choice(weather_options)
		temperature = random.randint(-10, 35)
		await query.edit_message_text(
			f"Случайный прогноз:\n"
			f"{weather}\n"
			f"Температура: {temperature}°C"
		)

	elif callback_data == "poll":
		keyboard = [
			[InlineKeyboardButton("Python", callback_data="poll_python")],
			[InlineKeyboardButton("JavaScript", callback_data="poll_js")],
			[InlineKeyboardButton("Другое", callback_data="poll_other")]
		]
		reply_markup = InlineKeyboardMarkup(keyboard)
		await query.edit_message_text(
			"Быстрый опрос:\nКакой ваш любимый язык программирования?",
			reply_markup=reply_markup
		)

	elif callback_data == "joke":
		jokes = [
			"Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 == Dec 25",
			"Сколько программистов нужно, чтобы вкрутить лампочку? Ни одного, это hardware проблема!",
			"Почему Python стал таким популярным? Потому что у него змеиное обаяние!",
			"Коммит - это когда ты говоришь 'я больше не буду это трогать'",
			"Лучшие программисты - ленивые программисты. Они найдут самый простой способ сделать работу"
		]
		joke = random.choice(jokes)
		await query.edit_message_text(f"Случайная шутка:\n\n{joke}")

	elif callback_data == "close":
		await query.delete_message( )

	elif callback_data.startswith("poll_"):
		answer = callback_data.split("_")[1]
		user = query.from_user.first_name

		answer_texts = {
			"python": "Python",
			"js": "JavaScript",
			"other": "Другое"
		}

		await query.edit_message_text(
			f"Спасибо за участие в опросе!\n\n"
			f"{user} выбрал(а): {answer_texts.get(answer, answer)}\n"
			f"Ваш голос учтен"
		)


async def get_exchange_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
	try:
		response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
		data = response.json()

		usd_rate = data['Valute']['USD']['Value']
		eur_rate = data['Valute']['EUR']['Value']
		date = data['Date'][:10]

		message = (
			f'Курсы валют на {date}:'
			f'USD: {usd_rate}руб.\n'
			f'EUR: {eur_rate}руб.\n'
			f'Источник: ЦБ РФ.'
		)

	except Exception as e:
		message = f'Не удалось получить курс валют. Ошибка {e}'

	await update.message.reply_text(message)

async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text('Введите название города:')

	context.user_data['waiting_for_city'] = True

async def handle_weather_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if context.user_data.get('waiting_for_city'):
		city = update.message.text
		context.user_data['waiting_for_city'] = False

		try:
			url = f'http://wttr.in/{city}?format=j1'
			response = requests.get(url)
			data = response.json()

			current = data['current_condition'][0]

			temp_c = current['temp_C']
			feels_like = current['FeelsLikeC']
			humidity = current['humidity']
			description = current['weatherDesc'][0]['value']
			wind_speed = current['windspeedKmph']

			message = (
				f"Погода в {city}:\n"
				f"Температура: {temp_c}°C\n"
				f"Ощущается как: {feels_like}°C\n"
				f"Влажность: {humidity}%\n"
				f"Ветер: {wind_speed} км/ч\n"
				f"Описание: {description}"
			)

		except Exception as e:
			message = f'Не удалось получить погоду для города {city}. Ошибка {e}'

		await update.message.reply_text(message)


async def get_random_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
	try:
		response = requests.get('https://official-joke-api.appspot.com/random_joke')
		data = response.json( )

		joke = f"{data['setup']}\n...\n{data['punchline']}"

	except Exception as e:
		jokes = [
			"Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 == Dec 25",
			"Сколько программистов нужно, чтобы вкрутить лампочку? Ни одного, это hardware проблема",
			"Почему Python стал таким популярным? Потому что у него змеиное обаяние!"
		]
		joke = random.choice(jokes)

	await update.message.reply_text(joke)


async def get_cat_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
	try:
		response = requests.get('https://catfact.ninja/fact')
		data = response.json( )
		fact = data['fact']
	except:
		fact = "Коты спят около 16 часов в день!"

	await update.message.reply_text(f"Факт о котах:\n{fact}")

async def show_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Python", callback_data="poll_python")],
        [InlineKeyboardButton("JavaScript", callback_data="poll_js")],
        [InlineKeyboardButton("Java", callback_data="poll_java")],
        [InlineKeyboardButton("C++", callback_data="poll_cpp")],
        [InlineKeyboardButton("Другое", callback_data="poll_other")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Опрос: Какой ваш любимый язык программирования?", reply_markup=reply_markup)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
	user_text = update.message.text

	# Проверяем, не ждем ли мы ввод города для погоды
	if context.user_data.get('waiting_for_city'):
		await handle_weather_city(update, context)
		return

	if user_text == "Информация" or user_text == "информация":
		await update.message.reply_text('Я бот версии 6.0 с интеграцией API!')
	elif user_text == 'Помощь' or user_text == 'помощь':
		help_text = '''
Помощь по боту:

Обычные кнопки:
Информация - о боте
Помощь - это сообщение
Случайное число - генератор
Обо мне - подробная информация
Inline кнопки - интерактивные кнопки
Опрос - участие в опросе
Оставить отзыв - многошаговая форма
Курс валют - текущие курсы
Погода - погода в городе
Случайная шутка - случайная шутка

Команды:
/start - перезапуск бота
/inline - inline кнопки
/cancel - отмена текущего диалога
/weather - погода
/rates - курсы валют
/joke - случайная шутка
/catfact - факт о котах
        '''
		await update.message.reply_text(help_text)
	elif user_text == 'Случайное число':
		number = random.randint(1, 100)
		await update.message.reply_text(f'Твое случайное число: {number}')
	elif user_text == "Обо мне":
		user = update.message.from_user
		user_info = f"Имя: {user.first_name}\nID: {user.id}"
		await update.message.reply_text(user_info)
	elif user_text == "Inline кнопки":
		await inline_command(update, context)
	elif user_text == "Опрос":
		await show_poll(update, context)
	elif user_text == "Оставить отзыв":
		await start_feedback(update, context)
	elif user_text == "Курс валют":
		await get_exchange_rates(update, context)
	elif user_text == "Погода":
		await get_weather(update, context)
	elif user_text == "Случайная шутка":
		await get_random_joke(update, context)
	else:
		await update.message.reply_text(f"Вы написали: {user_text}")



async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await get_weather(update, context)

async def rates_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await get_exchange_rates(update, context)

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await get_random_joke(update, context)

async def catfact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await get_cat_fact(update, context)


def main( ):
	app = Application.builder( ).token(BOT_TOKEN).concurrent_updates(False).build( )

	feedback_handler = ConversationHandler(
		entry_points=[MessageHandler(filters.Regex('^Оставить отзыв$'), start_feedback)],
		states={
			NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
			FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_feedback)],
			RATING: [CallbackQueryHandler(get_rating, pattern="^rating_")],
			CONFIRMATION: [CallbackQueryHandler(confirm_feedback, pattern="^confirm_")]
		},
		fallbacks=[CommandHandler('cancel', cancel_feedback)],
		per_message=True
	)

	# Обработчики команд
	app.add_handler(CommandHandler("start", start_command))
	app.add_handler(CommandHandler("inline", inline_command))
	app.add_handler(CommandHandler("cancel", cancel_feedback))
	app.add_handler(CommandHandler("weather", weather_command))
	app.add_handler(CommandHandler("rates", rates_command))
	app.add_handler(CommandHandler("joke", joke_command))
	app.add_handler(CommandHandler("catfact", catfact_command))

	app.add_handler(feedback_handler)
	app.add_handler(CallbackQueryHandler(button_handler))
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

	print("Бот запущен!")
	app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
	main()
