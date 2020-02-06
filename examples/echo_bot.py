from aiobot import Updater, Update, VkBot, MessageHandler


def echo_callback(update: Update, bot: VkBot):
    user = update.message.peer_id
    text = update.message.text
    bot.send_message(user, text)


if __name__ == '__main__':
    # Передаем в Updater id группы, токен и версию API
    updater = Updater('group_id', 'access_token', 'api_version')
    dp = updater.dispatcher
    # Создаем обработчик сообщений, который вызывает echo_callback для каждого
    echo_handler = MessageHandler(echo_callback)
    # Регестрируем обработчик в диспетчере
    dp.add_handler(echo_handler)
    # Запускаем Updater в режиме LongPoll
    updater.run()
