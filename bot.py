from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import ForceReply
import pickle


LIMIT = range(1)
user_no = {}
count_pref = {}
print(user_no)


# Import data
def inp_data():
    with open('counter.pickle', 'rb') as handle:
        user_no = pickle.load(handle)
    return user_no

#user_no = inp_data()


def upd_counter():
    with open('counter.pickle', 'wb') as handle:
        pickle.dump(user_no, handle, protocol=pickle.HIGHEST_PROTOCOL)


def warn(bot, update):
    chat_id = update.message.chat_id
    comb_id = str(chat_id) + str(update.message.from_user.id)

    if str(chat_id) not in count_pref:
        count = 5
    else:
        count = count_pref["{}".format(chat_id)]

    if comb_id not in user_no or user_no["{}".format(comb_id)] == 0:  # CREATE USER
        user_no["{}".format(comb_id)] = 0
        user_no["{}".format(comb_id)] += 1
        upd_counter()

    elif comb_id in user_no:
        if user_no["{}".format(comb_id)] != count:
            user_no["{}".format(comb_id)] += 1
            upd_counter()
            if user_no["{}".format(comb_id)] == count-1:
                update.message.reply_text("Last sticker remaining ({}/{})".format(count-1, count), quote=True)
        elif user_no["{}".format(comb_id)] == count:
            print("COUNTTT")
            print(count)
            bot.deleteMessage(int(update.message.chat_id), int(update.message.message_id))
            upd_counter()
    print(user_no)


# Print sticker counter
def counter(bot, update):
    comb_id = str(update.message.chat_id) + str(update.message.from_user.id)
    name = update.message.from_user.first_name
    update.message.reply_text("Counter for {} is {}".format(name, user_no["{}".format(comb_id)]), quote=True)


def setcount(bot, update): # Set CUSTOM COUNTER
    if update.message.chat.get_member(update.message.from_user.id).status == 'creator':
        update.message.reply_text('Set group sticker limit', reply_markup=ForceReply(selective=update.message.message_id))
        return LIMIT
    else:
        update.message.reply_text("You need to be an administrator for this!")


def limit(bot, update):
    pref = int(update.message.text)
    update.message.reply_text("Limit is set at {}!".format(pref))
    count_pref["{}".format(update.message.chat_id)] = pref
    return ConversationHandler.END


def reset(bot, update):
    comb_id = str(update.message.chat_id) + str(update.message.from_user.id)
    user_no["{}".format(comb_id)] = 0


def cancel(bot, update):
    update.message.reply_text("Alright, default value is set at 5 stickers.")
    return ConversationHandler.END

# ################      MAIN        ##################


def main():
    updater = Updater(token='')
    dp = updater.dispatcher

    # Add conversation handler
    conv_handler = ConversationHandler(entry_points=[CommandHandler("setcount", setcount)], states={LIMIT: [MessageHandler(Filters.text, limit)]}, fallbacks=[CommandHandler('cancel', cancel)])

    # Dispatcher for commands
    dp.add_handler(CommandHandler("counter", counter))
    dp.add_handler(CommandHandler("reset", reset))

    # Dispatcher for msgs
    dp.add_handler(MessageHandler(Filters.sticker, warn))
    dp.add_handler(conv_handler)
    # Begin polling
    updater.start_polling(clean=True)
    updater.idle()


if __name__ == '__main__':
    main()
