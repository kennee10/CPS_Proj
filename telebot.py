#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import settings
import telegram
import logging
import haversine
import enum
import pprint

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
)

# Enable logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(filename)s:%(funcName)s():%(lineno)i: %(message)s", datefmt="%Y-%m-%d %H:%M:%S",  level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Where SMUC is
SMUC_LOCATION = telegram.Location(latitude=1.295220, longitude=103.849632)
SMUC_VENUE = telegram.Venue(location=SMUC_LOCATION, title="SMU Connexion", address="")


def get_distance_from_smuc(location):
    return haversine.haversine((SMUC_LOCATION.latitude, SMUC_LOCATION.longitude), (location.latitude, location.longitude))


####################   Foodie feature. Works in private chats


STATE_CHOOSE_MENU = "STATE_CHOOSE_MENU"

SHARE_LOCATION     = "location"

def start(update: Update, context: CallbackContext) -> None:

    # Build InlineKeyboard where each button has a displayed text and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn a list (hence `[[...]]`).
    keyboard = [[
        KeyboardButton("Share Location", request_location = True),
        ]]

    # Send message with text and appended InlineKeyboard
    update.message.reply_text("Choose", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard = True))

    return ConversationHandler.END

#TODO: what the bot does after you share location
def handle_location_from_private_chats(update: Update, context: CallbackContext) -> None:
    if update.edited_message: # Live Location
        message = update.edited_message
    elif update.message: # Non-live Location
        message = update.message
    else:
        logger.error("update.edited_message and update.message are both None")
        return

    # Calculate the distance between the user and SMUC
    distance = get_distance_from_smuc(message.location)
    message.reply_text(text=f"You're {distance:.3f}km away from SMUC 🚁")


def handle_stateless_callback_query(update: Update, context: CallbackContext):
    update.callback_query.answer()
    update.callback_query.message.reply_animation(animation="https://media.tenor.com/images/c6956678c2456adbcbaac55b57806240/tenor.gif", caption=f"idk what's happening, try doing /start to start?")


def handle_unknown_command(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="huh?")


def handle_text_message_from_private_chats(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text=f"hey, try /start")


def main() -> None:
    # Create an updater object, and pass it the bot's token. 
    # The updater continuously fetches new updates from Telegram and passes them to the updater.dispatcher object.
    updater = telegram.ext.Updater(settings.my_token)

    # Add handler for text messages (excluding commands), from private chats
    updater.dispatcher.add_handler(MessageHandler(
        filters=Filters.text & ~Filters.command & Filters.chat_type.private, 
        callback=handle_text_message_from_private_chats))

    # Add handler for location messages, from private chats
    updater.dispatcher.add_handler(MessageHandler(
        filters=Filters.location & Filters.chat_type.private, 
        callback=handle_location_from_private_chats))

    food_conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler(command="start", filters=Filters.chat_type.private, callback=start),
            CallbackQueryHandler(callback=handle_stateless_callback_query)
            ],
        states={
        },
        fallbacks=[CommandHandler(command="start", filters=Filters.chat_type.private, callback=start)],
    )


    # Add handler for food conversations
    updater.dispatcher.add_handler(food_conversation_handler)

    # Add handler for commands that don't get handled by anything so far
    updater.dispatcher.add_handler(MessageHandler(filters=Filters.command, callback=handle_unknown_command))

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT. 
    # This should be used most of the time, since start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
