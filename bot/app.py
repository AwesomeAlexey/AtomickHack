import telebot
from yolo_bot import YOLOBot
from configuration import config

bot = telebot.TeleBot(config.token)
yolo_bot = YOLOBot(config.model)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: telebot.types.Message):

    reply_text = "Привет! Я - бот Трёх Роботов, умею предсказывать дефекты сварки!\n\n"
    reply_text += "Я не провидец, нет, просто многое успел повидать в своей жизни 🤓\n\n"
    reply_text += "Ты можешь прислать мне фото своей работы, а я скажу, есть ли там ошибки 😎"
    bot.send_message(message.chat.id, text=reply_text)


@bot.message_handler(content_types=['photo'])
def process_photo(message: telebot.types.Message):

    bot.send_message(message.chat.id, "Секундочку, сейчас посмотрю")

    raw_photo_id = message.photo[-1].file_id

    file = bot.get_file(file_id=raw_photo_id)
    file_data = bot.download_file(file_path=file.file_path)

    text, encoded_image = yolo_bot.get_response(file_data)

    if text == "":
        result_text = "YOLки-иголки! Отличная работа! Я не смог найти дефектов на этом фото"
        bot.reply_to(message, result_text)
        return

    result_text = "Вот дефекты, которые я нашёл на этом изображении:\n\n"
    result_text += text + "\n\n"
    result_text += "Пометил их на изображении."

    bot.send_photo(message.chat.id, photo=encoded_image, caption=result_text, reply_to_message_id=message.id)


@bot.message_handler()
def wrong_message(message: telebot.types.Message):

    reply_text = "Не надо слов, просто скинь мне фото 😏\n\n"
    reply_text += "Если надо напомнить, как всё устроено, мы всегда можем /start-ануть сначала"
    bot.reply_to(message, text=reply_text)

bot.infinity_polling()
