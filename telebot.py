#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# DATA
data = {
    "667047883-vuvip": {
        "name": "Gabriella",
        "languagePreference": "English",
        "IC": "T0012345A",
        "address": "Blk 884 yishun street 81",
        "DOB": "1-1-2000",
        "bloodType": "O+",
        "emergencyContact": "81234567",
        "relationshipOfEmergencyContact": "Mother"
    }
}

currentLatitude = 0
currentLongitude = 0

from ast import Call
import time
import settings
import telegram
import logging
import haversine
import serial
import enum
import pprint
import time


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


def location(update: Update, context: CallbackContext) -> None:
    message = None
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    global currentLatitude
    currentLatitude = message.location.latitude
    global currentLongitude
    currentLongitude = message.location.longitude
    #context.bot.send_location(chat_id=201975615, latitude =  message.location.latitude, longitude =  message.location.longitude)


def sendInfo(usersData, bot):
    data_string = ("Name: " + usersData.get('name') + "\nLanguage Preference: " + usersData.get('languagePreference') 
    + "\nIC: " + usersData.get('IC') + "\nAddress: " + usersData.get('address') + "\nDate of Birth: " + usersData.get('DOB')
    + "\nBlood Type: " + usersData.get('bloodType') + "\nEmergency Contact: " + usersData.get('emergencyContact')
    + "\nRelationship of Emergency Contact: " + usersData.get('relationshipOfEmergencyContact'))
    bot.send_message(chat_id=201975615, text = data_string)
    bot.send_location(chat_id=201975615, latitude =  currentLatitude, longitude =  currentLongitude)

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
    bot = telegram.Bot(settings.my_token)

    # Add handler for text messages (excluding commands), from private chats
    updater.dispatcher.add_handler(MessageHandler(
        filters=Filters.text & ~Filters.command & Filters.chat_type.private, 
        callback=handle_text_message_from_private_chats))

    # Add handler for location messages, from private chats
    updater.dispatcher.add_handler(MessageHandler(
        filters=Filters.location & Filters.chat_type.private, 
        callback=location))

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
    # updater.idle()
    print("im here")

    sendInfo(data["667047883-vuvip"], bot)
    #comment out the whole block below and use the above line of code to test without microbit
'''
    # Set up the Serial connection to capture the Microbit communications
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = "COM9"
    ser.open()

    while True:
        time.sleep(10)

        if ser.in_waiting > 0:

            microbitdata = str(ser.readline())
            uniqueIdentifier = microbitdata[3:22].strip()
            print(uniqueIdentifier)
            
            # check if user exists
            if uniqueIdentifier in data:
                
                usersData = data[uniqueIdentifier]
                sendInfo(usersData)
                '''

if __name__ == "__main__":
    main()
